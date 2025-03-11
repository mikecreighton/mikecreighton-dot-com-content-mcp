# CLAUDE.md - Guidelines for mikecreighton-dot-com-content-mcp

## Commands
- Run server: `python server.py`
- Run downloader: `python download.py`
- Install dependencies: `python -m pip install -e .`
- Lint: `ruff check .`
- Format: `ruff format .`
- Type check: `mypy .`

## Code Style
- Python 3.12+ compatible code
- Type annotations required for all functions
- Use descriptive variable names in snake_case
- Class names in PascalCase
- Constants in UPPER_SNAKE_CASE
- Docstrings for all public functions (Google style)
- Max line length: 88 characters
- Imports: standard lib → third party → local (alphabetical)
- Error handling: use specific exceptions, document in docstrings
- Asynchronous code preferred for I/O operations

## Project Structure
- `server.py`: MCP server implementation
- `download.py`: Website crawler and content processor
- `html/`: Downloaded HTML files
- `markdown/`: Generated markdown files