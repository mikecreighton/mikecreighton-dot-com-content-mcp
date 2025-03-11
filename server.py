#!/usr/bin/env python3
"""
Model Context Protocol (MCP) server for MikeCreighton.com content.
"""
import json
import os
from typing import Dict, List, Any, Optional
from pydantic import AnyUrl

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource

# Create an MCP server
mcp = FastMCP("MikeCreighton.com Content")


def load_site_map() -> Dict[str, Any]:
    """
    Load the site map from the JSON file.

    Returns:
        Dict containing the site map.
    """
    try:
        with open("site_map.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading site_map.json: {e}")
        return {}


def read_file(file_path: str) -> Optional[str]:
    """
    Read a file and return its contents.

    Args:
        file_path: Path to the file to read.

    Returns:
        The file contents as a string, or None if the file couldn't be read.
    """
    # Remove the leading ./ if present
    if file_path.startswith("./"):
        file_path = file_path[2:]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


@mcp.tool("get_page_content")
async def get_page_content(page_name: str) -> str:
    """Get the markdown content for a page."""
    site_map = load_site_map()

    if page_name not in site_map:
        raise ValueError(f"Page '{page_name}' not found")

    markdown_path = site_map[page_name].get("markdown", "")
    if not markdown_path:
        raise ValueError(f"No Markdown content available for '{page_name}'")

    content = read_file(markdown_path)
    if content is None:
        raise ValueError(f"Could not read Markdown content for '{page_name}'")

    return content


# Tools for model-controlled operations
@mcp.tool("list_pages")
async def list_pages() -> List[Dict[str, str]]:
    """
    List all available pages with their titles and descriptions and the `page_name` which can be used with `get_page_content` to get the content of the page.

    Returns:
        List of dictionaries with 'page_name', 'title', and 'description' for each page.
    """
    site_map = load_site_map()
    pages = []

    for page_name, page_info in site_map.items():
        pages.append(
            {
                "page_name": page_name,
                "title": page_info.get("name", ""),
                "description": page_info.get("description", ""),
            }
        )

    return pages


@mcp.tool("search_pages")
async def search_pages(query: str) -> List[Dict[str, str]]:
    """
    Search for pages containing the query in title or description.

    Args:
        query: The search query.

    Returns:
        List of matching pages with their metadata.
    """
    site_map = load_site_map()
    results = []

    query = query.lower()
    for page_name, page_info in site_map.items():
        title = page_info.get("name", "").lower()
        description = page_info.get("description", "").lower()

        if query in title or query in description:
            results.append(
                {
                    "page_name": page_name,
                    "title": page_info.get("name", ""),
                    "description": page_info.get("description", ""),
                    "relevance": "high" if query in title else "medium",
                }
            )

    # Sort by relevance
    results.sort(key=lambda x: 0 if x["relevance"] == "high" else 1)

    return results


if __name__ == "__main__":
    # Check if site_map.json exists, if not suggest running download.py
    if not os.path.exists("site_map.json"):
        print(
            "Warning: site_map.json not found. Please run download.py first to crawl the website."
        )
    else:
        print("Starting MCP server...")
        mcp.run(transport="stdio")
