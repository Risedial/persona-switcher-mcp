"""Unit tests for validation functions."""

import pytest
from src.validators import (
    validate_persona_name,
    validate_description,
    validate_instructions,
    validate_field_name
)


class TestValidatePersonaName:
    """Tests for validate_persona_name function."""

    def test_valid_names(self):
        """Test that valid persona names pass validation."""
        valid_names = [
            "code-reviewer",
            "test123",
            "my-persona",
            "a",
            "a" * 50,  # Max length
        ]
        for name in valid_names:
            is_valid, error = validate_persona_name(name)
            assert is_valid is True, f"'{name}' should be valid"
            assert error == ""

    def test_invalid_uppercase(self):
        """Test that uppercase letters are rejected."""
        is_valid, error = validate_persona_name("Code-Reviewer")
        assert is_valid is False
        assert "lowercase" in error.lower()

    def test_invalid_underscore(self):
        """Test that underscores are rejected."""
        is_valid, error = validate_persona_name("code_reviewer")
        assert is_valid is False
        assert "lowercase" in error.lower() or "hyphen" in error.lower()

    def test_invalid_space(self):
        """Test that spaces are rejected."""
        is_valid, error = validate_persona_name("code reviewer")
        assert is_valid is False

    def test_invalid_too_long(self):
        """Test that names over 50 characters are rejected."""
        is_valid, error = validate_persona_name("a" * 51)
        assert is_valid is False
        assert "long" in error.lower()

    def test_invalid_empty(self):
        """Test that empty names are rejected."""
        is_valid, error = validate_persona_name("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_invalid_special_characters(self):
        """Test that special characters are rejected."""
        invalid_names = ["code@reviewer", "code.reviewer", "code/reviewer"]
        for name in invalid_names:
            is_valid, error = validate_persona_name(name)
            assert is_valid is False, f"'{name}' should be invalid"


class TestValidateDescription:
    """Tests for validate_description function."""

    def test_valid_descriptions(self):
        """Test that valid descriptions pass validation."""
        valid_descriptions = [
            "A" * 10,  # Min length
            "A" * 100,  # Mid length
            "A" * 200,  # Max length
            "This is a valid description for testing",
        ]
        for desc in valid_descriptions:
            is_valid, error = validate_description(desc)
            assert is_valid is True, f"Description of length {len(desc)} should be valid"
            assert error == ""

    def test_invalid_too_short(self):
        """Test that descriptions under 10 characters are rejected."""
        is_valid, error = validate_description("Short")
        assert is_valid is False
        assert "short" in error.lower()

    def test_invalid_too_long(self):
        """Test that descriptions over 200 characters are rejected."""
        is_valid, error = validate_description("A" * 201)
        assert is_valid is False
        assert "long" in error.lower()

    def test_invalid_empty(self):
        """Test that empty descriptions are rejected."""
        is_valid, error = validate_description("")
        assert is_valid is False
        assert "empty" in error.lower()


class TestValidateInstructions:
    """Tests for validate_instructions function."""

    def test_valid_instructions(self):
        """Test that valid instructions pass validation."""
        valid_instructions = [
            "A" * 20,  # Min length
            "A" * 1000,  # Mid length
            "These are valid instructions for a persona",
        ]
        for inst in valid_instructions:
            is_valid, error = validate_instructions(inst)
            assert is_valid is True, f"Instructions of length {len(inst)} should be valid"
            assert error == "" or "warning" in error.lower()

    def test_invalid_too_short(self):
        """Test that instructions under 20 characters are rejected."""
        is_valid, error = validate_instructions("Too short")
        assert is_valid is False
        assert "short" in error.lower()

    def test_invalid_empty(self):
        """Test that empty instructions are rejected."""
        is_valid, error = validate_instructions("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_warning_large_instructions(self):
        """Test that very large instructions return a warning."""
        is_valid, error = validate_instructions("A" * 11000)  # Over 10KB
        assert is_valid is True  # Not an error, just a warning
        assert "warning" in error.lower()


class TestValidateFieldName:
    """Tests for validate_field_name function."""

    def test_valid_fields(self):
        """Test that valid field names pass validation."""
        valid_fields = ["description", "instructions", "author", "version"]
        for field in valid_fields:
            is_valid, error = validate_field_name(field)
            assert is_valid is True, f"'{field}' should be valid"
            assert error == ""

    def test_invalid_fields(self):
        """Test that invalid field names are rejected."""
        invalid_fields = ["name", "invalid", "unknown", ""]
        for field in invalid_fields:
            is_valid, error = validate_field_name(field)
            assert is_valid is False, f"'{field}' should be invalid"
            assert "invalid" in error.lower() or "allowed" in error.lower()
