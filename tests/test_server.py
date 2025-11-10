"""Integration tests for the MCP server."""

import pytest
from pathlib import Path


class TestServerIntegration:
    """Integration tests for server functionality.

    Note: These tests require the FastMCP Client for full integration testing.
    They serve as a template for manual testing with MCP Inspector.
    """

    def test_server_imports(self):
        """Test that server module can be imported."""
        from src import server
        assert server.mcp is not None
        assert server.persona_manager is not None

    def test_tools_registered(self):
        """Test that all tools are registered."""
        from src.server import mcp

        # Get registered tool names
        tool_names = [tool.name for tool in mcp.list_tools()]

        # Verify all 5 tools are registered
        expected_tools = [
            "list_personas",
            "activate_persona",
            "create_persona",
            "edit_persona",
            "delete_persona"
        ]

        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Tool '{tool_name}' not registered"


# Manual testing checklist for MCP Inspector:
"""
To test with MCP Inspector:

1. Start the inspector:
   npx @modelcontextprotocol/inspector python src/server.py

2. Open http://localhost:6274 in browser

3. Verify:
   - [ ] 5 tools appear in tool list
   - [ ] Prompts loaded from personas/ directory
   - [ ] list_personas returns data
   - [ ] activate_persona works with valid persona
   - [ ] activate_persona returns error for invalid persona
   - [ ] create_persona creates file
   - [ ] edit_persona updates file
   - [ ] delete_persona requires confirmation
   - [ ] delete_persona removes file with confirm=true
   - [ ] Error responses are properly formatted
   - [ ] Logs appear in terminal (stderr)

4. Test with Claude Desktop:
   - [ ] Add server to claude_desktop_config.json
   - [ ] Restart Claude Desktop
   - [ ] Prompts appear in selector
   - [ ] Selecting prompt applies instructions
   - [ ] Tools are callable mid-conversation
   - [ ] Creating new persona works
   - [ ] Notifications trigger prompt list refresh
"""
