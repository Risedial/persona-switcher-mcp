"""Unit tests for PersonaManager."""

import pytest
from pathlib import Path
from src.persona_manager import PersonaManager
from src.errors import (
    PersonaNotFoundError,
    PersonaAlreadyExistsError,
    ValidationError,
    ConfirmationRequiredError,
)


class TestListPersonas:
    """Tests for list_personas method."""

    def test_list_empty_directory(self, persona_manager):
        """Test listing personas in empty directory."""
        result = persona_manager.list_personas()
        assert result["count"] == 0
        assert result["personas"] == []

    def test_list_multiple_personas(self, persona_manager, sample_persona_data):
        """Test listing multiple personas."""
        # Create 3 personas
        for i in range(3):
            persona_manager.create_persona(
                name=f"test-persona-{i}",
                description=sample_persona_data["description"],
                instructions=sample_persona_data["instructions"],
                author=sample_persona_data["author"]
            )

        result = persona_manager.list_personas()
        assert result["count"] == 3
        assert len(result["personas"]) == 3

    def test_list_skips_invalid_files(self, persona_manager, tmp_personas_dir):
        """Test that invalid files are skipped."""
        # Create valid persona
        persona_manager.create_persona(
            name="valid-persona",
            description="Valid test persona",
            instructions="These are valid instructions."
        )

        # Create invalid file (no frontmatter)
        invalid_file = tmp_personas_dir / "invalid.md"
        invalid_file.write_text("No frontmatter here")

        result = persona_manager.list_personas()
        assert result["count"] == 1  # Only valid persona counted


class TestGetPersona:
    """Tests for get_persona method."""

    def test_get_existing_persona(self, persona_manager, sample_persona_data):
        """Test getting an existing persona."""
        # Create persona
        persona_manager.create_persona(**sample_persona_data)

        # Get persona
        result = persona_manager.get_persona(sample_persona_data["name"])

        assert result["name"] == sample_persona_data["name"]
        assert result["description"] == sample_persona_data["description"]
        assert result["instructions"] == sample_persona_data["instructions"]
        assert result["author"] == sample_persona_data["author"]

    def test_get_nonexistent_persona(self, persona_manager):
        """Test getting a persona that doesn't exist."""
        with pytest.raises(PersonaNotFoundError):
            persona_manager.get_persona("nonexistent-persona")

    def test_get_persona_invalid_name(self, persona_manager):
        """Test getting persona with invalid name format."""
        with pytest.raises(ValidationError):
            persona_manager.get_persona("Invalid Name")


class TestCreatePersona:
    """Tests for create_persona method."""

    def test_create_persona_success(self, persona_manager, sample_persona_data, tmp_personas_dir):
        """Test successful persona creation."""
        result = persona_manager.create_persona(**sample_persona_data)

        assert result["success"] is True
        assert result["persona_name"] == sample_persona_data["name"]
        assert "file_path" in result

        # Verify file was created
        file_path = tmp_personas_dir / f"{sample_persona_data['name']}.md"
        assert file_path.exists()

    def test_create_persona_already_exists(self, persona_manager, sample_persona_data):
        """Test creating persona that already exists."""
        # Create once
        persona_manager.create_persona(**sample_persona_data)

        # Try to create again
        with pytest.raises(PersonaAlreadyExistsError):
            persona_manager.create_persona(**sample_persona_data)

    def test_create_persona_invalid_name(self, persona_manager, sample_persona_data):
        """Test creating persona with invalid name."""
        sample_persona_data["name"] = "Invalid Name"
        with pytest.raises(ValidationError):
            persona_manager.create_persona(**sample_persona_data)

    def test_create_persona_description_too_short(self, persona_manager, sample_persona_data):
        """Test creating persona with description that's too short."""
        sample_persona_data["description"] = "Short"
        with pytest.raises(ValidationError):
            persona_manager.create_persona(**sample_persona_data)

    def test_create_persona_instructions_too_short(self, persona_manager, sample_persona_data):
        """Test creating persona with instructions that are too short."""
        sample_persona_data["instructions"] = "Too short"
        with pytest.raises(ValidationError):
            persona_manager.create_persona(**sample_persona_data)


class TestEditPersona:
    """Tests for edit_persona method."""

    def test_edit_description(self, persona_manager, sample_persona_data):
        """Test editing persona description."""
        # Create persona
        persona_manager.create_persona(**sample_persona_data)

        # Edit description
        new_description = "Updated test description for persona"
        result = persona_manager.edit_persona(
            sample_persona_data["name"],
            "description",
            new_description
        )

        assert result["success"] is True
        assert result["field_updated"] == "description"

        # Verify change
        persona = persona_manager.get_persona(sample_persona_data["name"])
        assert persona["description"] == new_description

    def test_edit_instructions(self, persona_manager, sample_persona_data):
        """Test editing persona instructions."""
        # Create persona
        persona_manager.create_persona(**sample_persona_data)

        # Edit instructions
        new_instructions = "These are updated test instructions for the persona."
        result = persona_manager.edit_persona(
            sample_persona_data["name"],
            "instructions",
            new_instructions
        )

        assert result["success"] is True
        assert result["field_updated"] == "instructions"

        # Verify change
        persona = persona_manager.get_persona(sample_persona_data["name"])
        assert persona["instructions"] == new_instructions

    def test_edit_nonexistent_persona(self, persona_manager):
        """Test editing persona that doesn't exist."""
        with pytest.raises(PersonaNotFoundError):
            persona_manager.edit_persona(
                "nonexistent-persona",
                "description",
                "New description"
            )

    def test_edit_invalid_field(self, persona_manager, sample_persona_data):
        """Test editing with invalid field name."""
        # Create persona
        persona_manager.create_persona(**sample_persona_data)

        with pytest.raises(ValidationError):
            persona_manager.edit_persona(
                sample_persona_data["name"],
                "invalid_field",
                "Some value"
            )


class TestDeletePersona:
    """Tests for delete_persona method."""

    def test_delete_persona_success(self, persona_manager, sample_persona_data, tmp_personas_dir):
        """Test successful persona deletion."""
        # Create persona
        persona_manager.create_persona(**sample_persona_data)

        # Delete with confirmation
        result = persona_manager.delete_persona(sample_persona_data["name"], confirm=True)

        assert result["success"] is True
        assert result["persona_name"] == sample_persona_data["name"]

        # Verify file was deleted
        file_path = tmp_personas_dir / f"{sample_persona_data['name']}.md"
        assert not file_path.exists()

    def test_delete_persona_no_confirmation(self, persona_manager, sample_persona_data):
        """Test deleting persona without confirmation."""
        # Create persona
        persona_manager.create_persona(**sample_persona_data)

        # Try to delete without confirmation
        with pytest.raises(ConfirmationRequiredError):
            persona_manager.delete_persona(sample_persona_data["name"], confirm=False)

    def test_delete_nonexistent_persona(self, persona_manager):
        """Test deleting persona that doesn't exist."""
        with pytest.raises(PersonaNotFoundError):
            persona_manager.delete_persona("nonexistent-persona", confirm=True)


class TestEnsureDirectoryInitialized:
    """Tests for ensure_directory_initialized method."""

    def test_creates_example_persona(self, tmp_path):
        """Test that example persona is created in empty directory."""
        personas_dir = tmp_path / "personas"
        personas_dir.mkdir()

        manager = PersonaManager(personas_dir)
        manager.ensure_directory_initialized()

        # Check that example persona was created
        example_file = personas_dir / "example.md"
        assert example_file.exists()

        # Verify it's a valid persona
        persona = manager.get_persona("example")
        assert "name" in persona
        assert "description" in persona
        assert "instructions" in persona
