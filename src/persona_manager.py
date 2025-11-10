"""Business logic for persona CRUD operations."""

import logging
from pathlib import Path

import frontmatter

from .errors import (
    ConfirmationRequiredError,
    FileAccessError,
    InvalidPersonaFormatError,
    PersonaAlreadyExistsError,
    PersonaNotFoundError,
    StorageError,
    ValidationError,
)
from .utils import atomic_write, ensure_directory_exists
from .validators import (
    validate_description,
    validate_field_name,
    validate_instructions,
    validate_persona_name,
)


class PersonaManager:
    """Manages persona CRUD operations."""

    def __init__(self, personas_dir: Path):
        """Initialize PersonaManager.

        Args:
            personas_dir: Path to personas directory
        """
        self.personas_dir = personas_dir
        self.logger = logging.getLogger(__name__)

    def list_personas(self) -> dict:
        """List all available personas with metadata.

        Returns:
            Dictionary with personas list and count

        Raises:
            PersonasDirectoryNotFoundError: If directory doesn't exist
        """
        if not self.personas_dir.exists():
            self.logger.warning(f"Personas directory not found: {self.personas_dir}")
            return {"personas": [], "count": 0}

        personas = []

        for file_path in self.personas_dir.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)

                # Validate required fields
                if 'name' not in post.metadata:
                    self.logger.warning(f"Skipping {file_path.name}: missing 'name' field")
                    continue

                if 'description' not in post.metadata:
                    self.logger.warning(f"Skipping {file_path.name}: missing 'description' field")
                    continue

                personas.append({
                    "name": post.metadata['name'],
                    "description": post.metadata['description'],
                    "version": post.metadata.get('version', '1.0'),
                    "author": post.metadata.get('author', 'User'),
                    "filename": file_path.stem
                })

                self.logger.debug(f"Loaded persona: {post.metadata['name']}")

            except Exception as e:
                self.logger.warning(f"Skipping invalid file {file_path.name}: {e}")
                continue

        return {
            "personas": personas,
            "count": len(personas)
        }

    def get_persona(self, name: str) -> dict:
        """Load and return a specific persona.

        Args:
            name: Persona name (filename without .md)

        Returns:
            Dictionary with persona data

        Raises:
            ValidationError: If name format is invalid
            PersonaNotFoundError: If persona doesn't exist
            InvalidPersonaFormatError: If persona file is corrupted
            FileAccessError: If file cannot be read
        """
        # Validate name format
        valid, error = validate_persona_name(name)
        if not valid:
            raise ValidationError(error)

        # Construct file path
        file_path = self.personas_dir / f"{name}.md"

        # Validate path doesn't escape directory
        try:
            if not file_path.resolve().is_relative_to(self.personas_dir.resolve()):
                raise ValidationError("Invalid persona name")
        except ValueError:
            raise ValidationError("Invalid persona name")

        # Check file exists
        if not file_path.exists():
            raise PersonaNotFoundError(
                f"Persona '{name}' not found",
                details={"persona_name": name}
            )

        # Load persona
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
        except PermissionError:
            raise FileAccessError(f"Permission denied reading persona '{name}'")
        except Exception as e:
            raise InvalidPersonaFormatError(
                f"Failed to parse persona file '{name}.md'",
                details={"error": str(e)}
            )

        # Validate required fields
        if 'name' not in post.metadata or 'description' not in post.metadata:
            raise InvalidPersonaFormatError(
                f"Persona '{name}' missing required fields (name, description)"
            )

        return {
            "name": post.metadata['name'],
            "description": post.metadata['description'],
            "version": post.metadata.get('version', '1.0'),
            "author": post.metadata.get('author', 'User'),
            "instructions": post.content
        }

    def create_persona(
        self,
        name: str,
        description: str,
        instructions: str,
        author: str = "User"
    ) -> dict:
        """Create a new persona file.

        Args:
            name: Persona name (used as filename)
            description: Brief description
            instructions: Full persona instructions
            author: Author name

        Returns:
            Dictionary with success message and file path

        Raises:
            ValidationError: If inputs are invalid
            PersonaAlreadyExistsError: If persona already exists
            FileAccessError: If directory not writable
            StorageError: If disk full
        """
        # Validate inputs
        valid, error = validate_persona_name(name)
        if not valid:
            raise ValidationError(error, details={"field": "name"})

        valid, error = validate_description(description)
        if not valid:
            raise ValidationError(error, details={"field": "description"})

        valid, error = validate_instructions(instructions)
        if not valid:
            raise ValidationError(error, details={"field": "instructions"})

        # Check if file already exists
        file_path = self.personas_dir / f"{name}.md"
        if file_path.exists():
            raise PersonaAlreadyExistsError(
                f"Persona '{name}' already exists",
                details={"persona_name": name, "file_path": str(file_path)}
            )

        # Ensure directory exists
        try:
            ensure_directory_exists(self.personas_dir)
        except OSError as e:
            raise FileAccessError(
                "Cannot create personas directory",
                details={"error": str(e)}
            )

        # Create frontmatter post
        post = frontmatter.Post(
            content=instructions,
            name=name,
            description=description,
            version="1.0",
            author=author
        )

        # Write file atomically
        try:
            content = frontmatter.dumps(post)
            atomic_write(file_path, content)
            self.logger.info(f"Created persona: {name}")
        except PermissionError:
            raise FileAccessError(
                "Cannot write to personas directory. Permission denied.",
                details={"directory": str(self.personas_dir)}
            )
        except OSError as e:
            if "No space left" in str(e) or "Disk quota" in str(e):
                raise StorageError(
                    "Failed to create persona: No space left on device",
                    details={"persona_name": name}
                )
            raise FileAccessError(
                f"Failed to create persona: {str(e)}",
                details={"persona_name": name}
            )

        return {
            "success": True,
            "persona_name": name,
            "file_path": str(file_path),
            "message": f"Persona '{name}' created successfully"
        }

    def edit_persona(self, name: str, field: str, value: str) -> dict:
        """Update an existing persona's field.

        Args:
            name: Persona name
            field: Field to update (description, instructions, author, version)
            value: New value

        Returns:
            Dictionary with success message

        Raises:
            ValidationError: If inputs are invalid
            PersonaNotFoundError: If persona doesn't exist
            FileAccessError: If file not writable
        """
        # Validate field name
        valid, error = validate_field_name(field)
        if not valid:
            raise ValidationError(error, details={"field": "field"})

        # Validate value based on field
        if field == "description":
            valid, error = validate_description(value)
            if not valid:
                raise ValidationError(error, details={"field": "value"})
        elif field == "instructions":
            valid, error = validate_instructions(value)
            if not valid:
                raise ValidationError(error, details={"field": "value"})

        if not value:
            raise ValidationError("Value cannot be empty", details={"field": "value"})

        # Load existing persona
        persona = self.get_persona(name)  # This validates name and checks existence

        # Update field
        file_path = self.personas_dir / f"{name}.md"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            # Update appropriate field
            if field == "instructions":
                post.content = value
            else:
                post.metadata[field] = value

            # Write back atomically
            content = frontmatter.dumps(post)
            atomic_write(file_path, content)
            self.logger.info(f"Updated persona '{name}' field '{field}'")

        except PermissionError:
            raise FileAccessError(
                f"Permission denied writing to persona '{name}'",
                details={"persona_name": name}
            )
        except Exception as e:
            raise FileAccessError(
                f"Failed to update persona: {str(e)}",
                details={"persona_name": name}
            )

        return {
            "success": True,
            "persona_name": name,
            "field_updated": field,
            "message": f"Persona '{name}' updated successfully"
        }

    def delete_persona(self, name: str, confirm: bool) -> dict:
        """Delete a persona file.

        Args:
            name: Persona name
            confirm: Must be True to proceed

        Returns:
            Dictionary with success message

        Raises:
            ConfirmationRequiredError: If confirm is not True
            ValidationError: If name is invalid
            PersonaNotFoundError: If persona doesn't exist
            FileAccessError: If file cannot be deleted
        """
        # Check confirmation
        if confirm is not True:
            raise ConfirmationRequiredError(
                "Confirmation required to delete persona. Set confirm=true to proceed.",
                details={"persona_name": name}
            )

        # Validate name
        valid, error = validate_persona_name(name)
        if not valid:
            raise ValidationError(error)

        # Check file exists
        file_path = self.personas_dir / f"{name}.md"
        if not file_path.exists():
            raise PersonaNotFoundError(
                f"Persona '{name}' not found",
                details={"persona_name": name}
            )

        # Delete file
        try:
            file_path.unlink()
            self.logger.info(f"Deleted persona: {name}")
        except PermissionError:
            raise FileAccessError(
                f"Permission denied deleting persona '{name}'",
                details={"persona_name": name}
            )
        except Exception as e:
            raise FileAccessError(
                f"Failed to delete persona: {str(e)}",
                details={"persona_name": name}
            )

        return {
            "success": True,
            "persona_name": name,
            "message": f"Persona '{name}' deleted successfully"
        }

    def ensure_directory_initialized(self) -> None:
        """Ensure personas directory exists and has example persona.

        Creates directory and example persona if needed.
        """
        # Create directory if missing
        if not self.personas_dir.exists():
            self.logger.info(f"Creating personas directory: {self.personas_dir}")
            ensure_directory_exists(self.personas_dir)

        # Create example persona if directory is empty
        existing_files = list(self.personas_dir.glob("*.md"))
        if not existing_files:
            self.logger.info("Creating example persona")
            self._create_example_persona()

    def _create_example_persona(self) -> None:
        """Create example persona to demonstrate format."""
        example_name = "example"
        example_description = "Example persona demonstrating the file format"
        example_instructions = """This is an example persona to demonstrate the file format.

You can use this as a template when creating your own personas.

Key features:
- YAML frontmatter for metadata
- Markdown content for instructions
- Clear, concise instructions
- Specific behavior guidelines

Replace this content with your own instructions when creating new personas."""

        try:
            self.create_persona(
                name=example_name,
                description=example_description,
                instructions=example_instructions,
                author="System"
            )
        except PersonaAlreadyExistsError:
            # Already exists, that's fine
            pass
        except Exception as e:
            self.logger.warning(f"Failed to create example persona: {e}")
