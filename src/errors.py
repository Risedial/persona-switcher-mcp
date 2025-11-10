"""Custom exception classes for persona operations."""


class PersonaError(Exception):
    """Base exception for all persona operations."""

    code = "persona_error"

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PersonaNotFoundError(PersonaError):
    """Persona file doesn't exist."""

    code = "persona_not_found"


class PersonaAlreadyExistsError(PersonaError):
    """Attempted to create existing persona."""

    code = "persona_already_exists"


class InvalidPersonaFormatError(PersonaError):
    """Persona file has invalid YAML/structure."""

    code = "invalid_persona_format"


class ValidationError(PersonaError):
    """Input validation failed."""

    code = "validation_error"


class FileAccessError(PersonaError):
    """File system permission denied."""

    code = "file_access_error"


class StorageError(PersonaError):
    """Disk full or other storage issue."""

    code = "storage_error"


class ConfirmationRequiredError(PersonaError):
    """Confirmation not provided for destructive operation."""

    code = "confirmation_required"


class PersonasDirectoryNotFoundError(PersonaError):
    """Personas directory doesn't exist."""

    code = "personas_directory_not_found"
