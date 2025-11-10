"""Input validation functions for persona operations."""

import re


def validate_persona_name(name: str) -> tuple[bool, str]:
    """Validate persona name format.

    Args:
        name: Persona name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Persona name cannot be empty"

    if len(name) > 50:
        return False, "Persona name too long (max 50 characters)"

    if not re.match(r'^[a-z0-9-]+$', name):
        return False, "Persona name must contain only lowercase letters, numbers, and hyphens"

    return True, ""


def validate_description(description: str) -> tuple[bool, str]:
    """Validate persona description.

    Args:
        description: Description to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not description:
        return False, "Description cannot be empty"

    if len(description) < 10:
        return False, "Description too short (minimum 10 characters)"

    if len(description) > 200:
        return False, "Description too long (maximum 200 characters)"

    return True, ""


def validate_instructions(instructions: str) -> tuple[bool, str]:
    """Validate persona instructions.

    Args:
        instructions: Instructions to validate

    Returns:
        Tuple of (is_valid, warning_or_error_message)
    """
    if not instructions:
        return False, "Instructions cannot be empty"

    if len(instructions) < 20:
        return False, "Instructions too short (minimum 20 characters)"

    # Warning for very large instructions (not an error)
    if len(instructions) > 10240:  # 10KB
        return True, f"Warning: Instructions are very large ({len(instructions)} bytes)"

    return True, ""


def validate_field_name(field: str) -> tuple[bool, str]:
    """Validate field name for edit operations.

    Args:
        field: Field name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    allowed_fields = ["description", "instructions", "author", "version"]

    if field not in allowed_fields:
        return False, f"Invalid field name. Allowed fields: {', '.join(allowed_fields)}"

    return True, ""
