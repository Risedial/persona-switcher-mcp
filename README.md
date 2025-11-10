# Persona Switcher MCP Server

Dynamic AI persona management for Claude with file-based storage. Switch between different AI personas mid-conversation or start conversations with pre-configured personas.

## Features

- **Dynamic Persona Prompts**: Start conversations with specific personas from Claude Desktop's prompt selector
- **Mid-Conversation Switching**: Activate different personas without losing conversation context
- **File-Based Storage**: Personas stored as markdown files with YAML frontmatter for easy editing and version control
- **CRUD Operations**: Create, read, update, and delete personas through MCP tools
- **Zero Configuration**: Works out of the box with sensible defaults
- **Automatic Initialization**: Creates example persona on first run
- **Validation**: Built-in input validation for persona names, descriptions, and instructions
- **Error Handling**: Comprehensive error messages with helpful suggestions

## Requirements

- Python 3.10 or higher
- Claude Desktop (for integration)
- At least 10MB disk space for persona files

## Installation

### 1. Clone or Download

```bash
cd "persona-switcher-mcp Project"
cd persona-switcher-mcp
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows**: `venv\Scripts\activate`
- **macOS/Linux**: `source venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For development (includes testing tools):
```bash
pip install -r requirements-dev.txt
```

### 4. Install as Editable Package (Optional)

```bash
pip install -e .
```

## Configuration

### Environment Variables

All configuration is optional. Create a `.env` file if you want to customize:

```bash
# Copy example configuration
cp .env.example .env
```

Available options:

| Variable | Default | Description |
|----------|---------|-------------|
| `PERSONAS_DIR` | `./personas` | Path to personas directory |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `AUTO_RELOAD` | `false` | Auto-reload prompts when files change (requires watchdog) |

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "persona-switcher": {
      "command": "python",
      "args": [
        "C:/Users/YourUsername/path/to/persona-switcher-mcp/src/server.py"
      ],
      "env": {
        "PERSONAS_DIR": "C:/Users/YourUsername/path/to/persona-switcher-mcp/personas",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important**: Use absolute paths and forward slashes (/) even on Windows.

After adding the configuration, restart Claude Desktop.

## Usage

### Testing with MCP Inspector

Before integrating with Claude Desktop, test the server with MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python src/server.py
```

Open http://localhost:6274 in your browser to interact with the server.

### Creating Personas

Personas are stored as markdown files with YAML frontmatter in the `personas/` directory.

#### File Format

```markdown
---
name: Code Reviewer
description: Expert code reviewer focusing on best practices, security, and performance
version: 1.0
author: User
---

You are an expert code reviewer with deep knowledge of software engineering best practices.

Your focus areas:
- Code quality and maintainability
- Security vulnerabilities
- Performance optimization
- Design patterns
- Testing coverage

When reviewing code, provide:
1. Overall assessment
2. Specific issues with line references
3. Actionable recommendations
4. Security concerns (if any)

Be thorough but constructive in your feedback.
```

#### Naming Rules

- Filename pattern: `^[a-z0-9-]+\.md$`
- Lowercase letters only
- Numbers allowed
- Hyphens for word separation
- No spaces, underscores, or special characters

**Valid**: `code-reviewer.md`, `technical-writer.md`, `python-expert.md`
**Invalid**: `Code-Reviewer.md`, `code_reviewer.md`, `code reviewer.md`

### Available Tools

#### 1. `list_personas`

List all available personas with their metadata.

**Parameters**: None

**Returns**:
```json
{
  "personas": [
    {
      "name": "Code Reviewer",
      "description": "Expert code reviewer...",
      "version": "1.0",
      "author": "User",
      "filename": "code-reviewer"
    }
  ],
  "count": 1
}
```

**Example Usage**:
```
User: "What personas are available?"
Claude: *calls list_personas()*
Claude: "You have 3 personas available: Code Reviewer, Technical Writer, and Creative Brainstormer."
```

#### 2. `activate_persona`

Load and activate a persona's instructions mid-conversation.

**Parameters**:
- `name` (string): Persona name (filename without .md)

**Returns**:
```json
{
  "success": true,
  "persona_name": "Code Reviewer",
  "instructions": "You are an expert code reviewer...",
  "metadata": {
    "description": "Expert code reviewer...",
    "version": "1.0",
    "author": "User"
  }
}
```

**Example Usage**:
```
User: "Switch to code reviewer mode"
Claude: *calls activate_persona({name: "code-reviewer"})*
Claude: "I've activated the Code Reviewer persona. I'm now ready to review your code with a focus on best practices, security, and performance."
```

#### 3. `create_persona`

Create a new persona file.

**Parameters**:
- `name` (string): Persona name (lowercase with hyphens, 1-50 chars)
- `description` (string): Brief description (10-200 chars)
- `instructions` (string): Full instructions (minimum 20 chars)
- `author` (string, optional): Author name (default: "User")

**Returns**:
```json
{
  "success": true,
  "persona_name": "python-expert",
  "file_path": "personas/python-expert.md",
  "message": "Persona 'python-expert' created successfully"
}
```

**Example Usage**:
```
User: "Create a Python expert persona"
Claude: *calls create_persona({
  name: "python-expert",
  description: "Python programming expert specialized in best practices",
  instructions: "You are a Python expert with deep knowledge of...",
  author: "User"
})*
Claude: "I've created the Python Expert persona. You can activate it anytime or start a new conversation with it from the prompt selector."
```

#### 4. `edit_persona`

Update an existing persona's metadata or instructions.

**Parameters**:
- `name` (string): Persona name
- `field` (string): Field to update (`description`, `instructions`, `author`, or `version`)
- `value` (string): New value

**Returns**:
```json
{
  "success": true,
  "persona_name": "code-reviewer",
  "field_updated": "description",
  "message": "Persona 'code-reviewer' updated successfully"
}
```

**Example Usage**:
```
User: "Update the code reviewer's instructions to focus more on security"
Claude: *calls edit_persona({
  name: "code-reviewer",
  field: "instructions",
  value: "You are an expert code reviewer with primary focus on security vulnerabilities..."
})*
Claude: "I've updated the Code Reviewer persona to emphasize security in code reviews."
```

#### 5. `delete_persona`

Remove a persona file from the personas directory.

**Parameters**:
- `name` (string): Persona name
- `confirm` (boolean): Must be `true` to confirm deletion

**Returns**:
```json
{
  "success": true,
  "persona_name": "old-persona",
  "message": "Persona 'old-persona' deleted successfully"
}
```

**Example Usage**:
```
User: "Delete the old-persona"
Claude: *calls delete_persona({name: "old-persona", confirm: true})*
Claude: "I've deleted the old-persona. It's no longer available."
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_validators.py

# Run with verbose output
pytest -v
```

### Project Structure

```
persona-switcher-mcp/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── server.py             # FastMCP server and tools
│   ├── persona_manager.py    # Business logic (CRUD operations)
│   ├── validators.py         # Input validation functions
│   ├── errors.py            # Custom exception classes
│   ├── config.py            # Configuration management
│   └── utils.py             # Utility functions (atomic writes)
├── personas/                 # Persona markdown files
│   ├── example.md           # Example persona (created automatically)
│   └── *.md                 # User-created personas
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_validators.py  # Validator tests
│   ├── test_persona_manager.py  # PersonaManager tests
│   ├── test_server.py       # Integration tests
│   └── fixtures/            # Test data files
├── pyproject.toml           # Python project configuration
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── README.md               # This file
├── .env.example            # Example environment configuration
├── .gitignore              # Git ignore rules
└── LICENSE                 # MIT License
```

### Code Quality

The codebase follows these principles:

- **Layered Architecture**: Clear separation between presentation (server.py), business logic (persona_manager.py), and utilities
- **Input Validation**: All inputs validated before processing
- **Error Handling**: Comprehensive error classes with helpful messages
- **Atomic File Operations**: Prevents file corruption during writes
- **Logging**: All operations logged to stderr for debugging
- **Type Hints**: Python 3.10+ type hints throughout
- **Documentation**: Docstrings for all public functions and classes

## Troubleshooting

### Server Won't Start

**Error**: "Personas directory not found"
**Solution**: The server will automatically create the directory. Check file permissions.

**Error**: "Module not found"
**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Personas Not Appearing in Claude Desktop

**Issue**: Prompts don't show up in the prompt selector

**Solutions**:
1. Verify server is configured correctly in `claude_desktop_config.json`
2. Use absolute paths in the configuration
3. Restart Claude Desktop after configuration changes
4. Check Claude Desktop logs for errors
5. Verify persona files have valid YAML frontmatter with `name` and `description` fields

### Tool Calls Failing

**Error**: "Persona not found"
**Solution**:
- Use `list_personas()` to see available personas
- Check that the persona name matches the filename (without .md extension)
- Ensure persona file has valid YAML frontmatter

**Error**: "Validation error"
**Solution**:
- Persona names must be lowercase with hyphens only
- Descriptions must be 10-200 characters
- Instructions must be at least 20 characters

### File Permission Errors

**Error**: "Permission denied" or "Cannot write to personas directory"

**Solutions**:
- Check directory permissions: `ls -la personas/`
- Make directory writable: `chmod u+w personas/`
- On Windows, check folder properties and ensure write permission

### Logs Not Appearing

**Issue**: Can't see server logs

**Solution**: Logs are written to stderr. When running with MCP Inspector or Claude Desktop, check:
- Terminal output where you started the server
- Claude Desktop logs (check application logs directory)
- Set `LOG_LEVEL=DEBUG` in .env for more detailed logs

## Example Personas

### Code Reviewer

File: `personas/code-reviewer.md`

```markdown
---
name: Code Reviewer
description: Expert code reviewer focusing on best practices, security, and performance
version: 1.0
author: System
---

You are an expert code reviewer with deep knowledge of software engineering best practices.

Your focus areas:
- Code quality and maintainability
- Security vulnerabilities (OWASP Top 10)
- Performance optimization
- Design patterns and architecture
- Testing coverage and quality

When reviewing code, provide:
1. Overall assessment of code quality
2. Specific issues with line references
3. Actionable recommendations for improvement
4. Security concerns (if any)
5. Performance implications

Be thorough but constructive in your feedback. Explain the "why" behind each suggestion.
```

### Technical Writer

File: `personas/technical-writer.md`

```markdown
---
name: Technical Writer
description: Professional technical writer specializing in clear, concise documentation
version: 1.0
author: System
---

You are a professional technical writer with expertise in creating clear, user-friendly documentation.

Your specialties:
- API documentation
- User guides and tutorials
- README files
- Technical specifications
- Code comments and docstrings

Your writing principles:
- Clarity over cleverness
- Active voice over passive
- Examples for complex concepts
- Consistent terminology
- Proper formatting and structure

When writing documentation:
1. Start with a clear summary
2. Explain the "what" and "why"
3. Provide code examples
4. Include edge cases and limitations
5. End with troubleshooting tips
```

### Creative Brainstormer

File: `personas/creative-brainstormer.md`

```markdown
---
name: Creative Brainstormer
description: Innovative thinker generating creative ideas and solutions
version: 1.0
author: System
---

You are a creative brainstorming partner with a knack for innovative thinking and problem-solving.

Your approach:
- Think divergently before converging
- Explore unconventional angles
- Build on ideas iteratively
- Combine concepts in novel ways
- Challenge assumptions

When brainstorming:
1. Generate multiple diverse ideas (quantity over quality initially)
2. Explore "what if" scenarios
3. Look for unexpected connections
4. Question constraints
5. Refine promising concepts

Be enthusiastic, open-minded, and constructive. No idea is too wild in the brainstorming phase.
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastMCP](https://gofastmcp.com) - The official Python SDK for MCP servers
- Inspired by the [MCP Persona Server](https://lobehub.com/mcp/mickdarling-persona-mcp-server) concept
- Follows [MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/)

## Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: See the [MCP Documentation](https://modelcontextprotocol.io/)
- **FastMCP Docs**: https://gofastmcp.com

---

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-11-09
