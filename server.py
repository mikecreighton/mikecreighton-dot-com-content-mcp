# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("MikeCreighton.com Content")


@mcp.resource("mikecreighton://list_pages")
def list_pages() -> list[str]:
    """List all pages"""
    return []


@mcp.resource("mikecreighton://page/markdown/{page_name}")
def get_page_markdown(page_name: str) -> str:
    """Gets the markdown for a page"""
    return ""


@mcp.resource("mikecreighton://page/html/{page_name}")
def get_page_html(page_name: str) -> str:
    """Gets the HTML for a page"""
    return ""
