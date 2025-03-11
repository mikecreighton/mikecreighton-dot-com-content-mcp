#!/usr/bin/env python3
"""
Model Context Protocol (MCP) server for MikeCreighton.com content.
"""
import json
import os
from typing import Dict, List, Any, Optional
from pydantic import AnyUrl

from mcp.server.fastmcp import FastMCP
from mcp.types import (
    Resource as MCPResource,
)
from mcp.server.fastmcp.resources.types import FileResource

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


@mcp.tool("get_mikecreighton_website_page_content")
async def get_page_content(page_id: str) -> str:
    """
    Tool that gets the Markdown content for a page on Mike Creighton Consulting's website (https://mikecreighton.com).

    Args:
        page_id: The unique identifier of the page to get the content for (discoverable using the `list_mikecreighton_website_pages` tool)

    Returns:
        The Markdown content for the page.
    """
    site_map = load_site_map()

    if page_id not in site_map:
        raise ValueError(f"Page '{page_id}' not found")

    markdown_path = site_map[page_id].get("markdown", "")
    if not markdown_path:
        raise ValueError(f"No Markdown content available for '{page_id}'")

    content = read_file(markdown_path)
    if content is None:
        raise ValueError(f"Could not read Markdown content for '{page_id}'")

    return content


# Tools for model-controlled operations
@mcp.tool("list_mikecreighton_website_pages")
async def list_pages() -> List[Dict[str, str]]:
    """
    Tool that lists all available pages on Mike Creighton Consulting's website (https://mikecreighton.com). Pages will include their titles and descriptions and the `page_id` which can be used with the `get_mikecreighton_website_page_content` tool to get the full Markdown content of the page.

    Returns:
        List of dictionaries with 'page_id', 'title', and 'description' for each page.
    """
    site_map = load_site_map()
    pages = []

    for page_id, page_info in site_map.items():
        pages.append(
            {
                "page_id": page_id,
                "title": page_info.get("name", ""),
                "description": page_info.get("description", ""),
            }
        )

    return pages


@mcp.tool("search_mikecreighton_website_pages")
async def search_pages(query: str) -> List[Dict[str, str]]:
    """
    Tool that searches for pages on Mike Creighton Consulting's website (https://mikecreighton.com) containing exact string matches for the query in a page's title or description.

    Args:
        query: The search query.

    Returns:
        List of dictionaries each representing a page, each containing:
            - page_id (str): Identifier for the page
            - title (str): The page title
            - description (str): Brief description of the page
            - relevance (str): Either "high" (query in title) or "medium" (query in description)
    """
    site_map = load_site_map()
    results = []

    query = query.lower()
    for page_id, page_info in site_map.items():
        title = page_info.get("name", "").lower()
        description = page_info.get("description", "").lower()

        if query in title or query in description:
            results.append(
                {
                    "page_id": page_id,
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

        # Add all the pages to the MCP server as resources
        site_map_items = load_site_map()
        for page_id, page_info in site_map_items.items():
            # Get the markdown file path but strip off the leading ./
            markdown_path = page_info["markdown"]
            if markdown_path.startswith("./"):
                markdown_path = markdown_path[2:]
            full_cwd_path = os.path.join(os.getcwd(), markdown_path)

            # We're going straight to the FileResource type here because it's a
            # simple way to get the content of the file into the MCP server without
            # having to handle the file reading logic. We need to do this because
            # we don't want to use the @mcp.resource decorator since we can't
            # dynamically create those functions at runtime.
            mcp.add_resource(
                FileResource(
                    uri=f"mikecreighton://page/{page_id}",
                    name=page_info["name"],
                    description=page_info["description"],
                    mime_type="text/markdown",
                    path=full_cwd_path,
                    is_binary=False,
                )
            )

        print("Starting MCP server...")
        mcp.run(transport="stdio")
