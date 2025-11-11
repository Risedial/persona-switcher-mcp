"""Wrapper script to run persona-switcher MCP server.

This script properly sets up the Python path and runs the server.
"""

import sys
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).parent.resolve()
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

# Now import and run the server
from src.server import main

if __name__ == "__main__":
    main()
