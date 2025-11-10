"""FastMCP server for persona switching."""

import logging
import os
import signal
import sys
from pathlib import Path

import frontmatter
from fastmcp import FastMCP, Context
from mcp.types import TextContent, Tool

from .config import Config
from .errors import (
    ConfirmationRequiredError,
    FileAccessError,
    InvalidPersonaFormatError,
    PersonaAlreadyExistsError,
    PersonaError,
    PersonaNotFoundError,
    PersonasDirectoryNotFoundError,
    StorageError,
    ValidationError,
)
from .persona_manager import PersonaManager

# Configure logging to stderr
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Load and validate configuration
Config.validate()
logger.debug(f"Configuration loaded: PERSONAS_DIR={Config.PERSONAS_DIR}, LOG_LEVEL={Config.LOG_LEVEL}")

# Initialize FastMCP server
mcp = FastMCP(name="PersonaSwitcher")

# Initialize PersonaManager
persona_manager = PersonaManager(Config.PERSONAS_DIR)


def load_prompts_from_directory():
    """Load prompts from persona markdown files."""
    personas_dir = Config.PERSONAS_DIR

    if not personas_dir.exists():
        logger.warning(f"Personas directory not found: {personas_dir}")
        return

    loaded = 0
    for file_path in personas_dir.glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            # Validate required fields
            if 'name' not in post.metadata:
                logger.warning(f"Skipping {file_path.name}: missing 'name' field")
                continue

            if 'description' not in post.metadata:
                logger.warning(f"Skipping {file_path.name}: missing 'description' field")
                continue

            # Create prompt function
            def make_prompt_function(content):
                def prompt_fn():
                    return content
                return prompt_fn

            prompt_fn = make_prompt_function(post.content)
            prompt_fn.__name__ = file_path.stem
            prompt_fn.__doc__ = post.metadata['description']

            # Register with FastMCP
            mcp.prompt(name=post.metadata['name'], description=post.metadata['description'])(prompt_fn)

            loaded += 1
            logger.debug(f"Loaded prompt: {post.metadata['name']}")

        except Exception as e:
            logger.warning(f"Skipping invalid file {file_path.name}: {e}")
            continue

    logger.info(f"Loaded {loaded} prompts from {personas_dir}")


# Tool 1: list_personas
@mcp.tool(
    description="List all available personas with their metadata"
)
def list_personas() -> dict:
    """List all available personas with metadata.

    Returns:
        Dictionary with personas list and count
    """
    try:
        result = persona_manager.list_personas()
        logger.info(f"Listed {result['count']} personas")
        return result
    except Exception as e:
        logger.error(f"Error listing personas: {e}")
        raise


# Tool 2: activate_persona
@mcp.tool(
    description="Load and activate a specific persona's instructions mid-conversation"
)
def activate_persona(name: str) -> dict:
    """Activate a persona by loading its instructions.

    Args:
        name: The name of the persona to activate (filename without .md extension)

    Returns:
        Dictionary with success status, persona name, instructions, and metadata
    """
    try:
        persona = persona_manager.get_persona(name)
        logger.info(f"Activated persona: {name}")

        return {
            "success": True,
            "persona_name": persona["name"],
            "instructions": persona["instructions"],
            "metadata": {
                "description": persona["description"],
                "version": persona["version"],
                "author": persona["author"]
            }
        }
    except PersonaNotFoundError as e:
        # Include available personas for helpful error
        try:
            available_list = persona_manager.list_personas()
            available = [p["filename"] for p in available_list["personas"]]
        except:
            available = []

        raise PersonaNotFoundError(
            f"Persona '{name}' not found",
            details={
                "persona_name": name,
                "available_personas": available,
                "suggestion": "Check the persona name or use list_personas() to see available options"
            }
        )
    except Exception as e:
        logger.error(f"Error activating persona: {e}")
        raise


# Tool 3: create_persona
@mcp.tool(
    description="Create a new persona file with specified name, description, and instructions"
)
async def create_persona(
    ctx: Context,
    name: str,
    description: str,
    instructions: str,
    author: str = "User"
) -> dict:
    """Create a new persona file.

    Args:
        ctx: MCP context
        name: Persona name (lowercase with hyphens, e.g., 'code-reviewer')
        description: Brief description (10-200 characters)
        instructions: Full instructions for Claude (minimum 20 characters)
        author: Author name (optional, default: 'User')

    Returns:
        Dictionary with success status, persona name, and file path
    """
    try:
        result = persona_manager.create_persona(name, description, instructions, author)
        logger.info(f"Created persona: {name}")

        # Notify clients that prompts list changed
        await ctx.request_context.session.send_prompt_list_changed()

        return result
    except Exception as e:
        logger.error(f"Error creating persona: {e}")
        raise


# Tool 4: edit_persona
@mcp.tool(
    description="Update an existing persona's metadata or instructions"
)
async def edit_persona(
    ctx: Context,
    name: str,
    field: str,
    value: str
) -> dict:
    """Edit an existing persona's field.

    Args:
        ctx: MCP context
        name: Persona name
        field: Field to update ('description', 'instructions', 'author', or 'version')
        value: New value for the field

    Returns:
        Dictionary with success status, persona name, and updated field
    """
    try:
        result = persona_manager.edit_persona(name, field, value)
        logger.info(f"Edited persona '{name}' field '{field}'")

        # Notify if name or description changed (affects prompts)
        if field in ["name", "description", "instructions"]:
            await ctx.request_context.session.send_prompt_list_changed()

        return result
    except Exception as e:
        logger.error(f"Error editing persona: {e}")
        raise


# Tool 5: delete_persona
@mcp.tool(
    description="Remove a persona file from the personas directory (requires confirmation)"
)
async def delete_persona(
    ctx: Context,
    name: str,
    confirm: bool
) -> dict:
    """Delete a persona file.

    Args:
        ctx: MCP context
        name: Persona name to delete
        confirm: Must be true to confirm deletion

    Returns:
        Dictionary with success status, persona name, and confirmation message
    """
    try:
        result = persona_manager.delete_persona(name, confirm)
        logger.info(f"Deleted persona: {name}")

        # Notify clients that prompts list changed
        await ctx.request_context.session.send_prompt_list_changed()

        return result
    except Exception as e:
        logger.error(f"Error deleting persona: {e}")
        raise


def shutdown_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info("Shutting down PersonaSwitcher MCP server...")
    sys.exit(0)


def main():
    """Main entry point for the server."""
    try:
        logger.info("Starting PersonaSwitcher MCP server...")

        # Setup signal handlers
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        # Ensure directory initialized
        persona_manager.ensure_directory_initialized()

        # Load prompts from persona files
        load_prompts_from_directory()

        logger.info("PersonaSwitcher MCP server ready")

        # Run server
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
