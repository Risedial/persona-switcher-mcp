"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
from src.persona_manager import PersonaManager


@pytest.fixture
def tmp_personas_dir(tmp_path):
    """Create temporary personas directory for testing.

    Args:
        tmp_path: pytest's temporary directory fixture

    Returns:
        Path to temporary personas directory
    """
    personas_dir = tmp_path / "personas"
    personas_dir.mkdir()
    return personas_dir


@pytest.fixture
def persona_manager(tmp_personas_dir):
    """Create PersonaManager with temporary directory.

    Args:
        tmp_personas_dir: Temporary personas directory fixture

    Returns:
        PersonaManager instance
    """
    return PersonaManager(tmp_personas_dir)


@pytest.fixture
def sample_persona_data():
    """Sample persona data for testing.

    Returns:
        Dictionary with sample persona data
    """
    return {
        "name": "test-persona",
        "description": "Test persona for unit tests",
        "instructions": "These are test instructions for the persona.",
        "author": "Test Suite"
    }
