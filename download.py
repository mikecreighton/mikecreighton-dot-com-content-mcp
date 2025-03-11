#!/usr/bin/env python3
"""
Script for crawling and downloading all HTML pages from mikecreighton.com,
converting them to markdown, and creating a site map.
"""
import os
import json
import logging
import re
import shutil
from typing import Dict, List, Set, Optional, TypedDict
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from markitdown import MarkItDown


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PageInfo(TypedDict):
    """Type definition for page information in the site map."""

    base: str  # Base path of the page which acts as the unique identifier
    html: str  # Path to the HTML file
    markdown: str  # Path to the Markdown file
    name: str  # Title of the page
    description: str  # Description of the page


class WebsiteCrawler:
    """Crawler for downloading mikecreighton.com website content."""

    def __init__(self, base_url: str = "https://mikecreighton.com"):
        """
        Initialize the crawler.

        Args:
            base_url: The base URL of the website to crawl.
        """
        self.base_url = base_url
        self.visited: Set[str] = set()
        self.to_visit: List[str] = ["/"]
        self.site_map: Dict[str, PageInfo] = {}

        # Set up directories
        self.html_dir = Path("./html")
        self.markdown_dir = Path("./markdown")

        # Clear and recreate directories
        self._clear_directory(self.html_dir)
        self._clear_directory(self.markdown_dir)

        # Initialize MarkItDown
        self.md_converter = MarkItDown()

    def _clear_directory(self, directory: Path) -> None:
        """
        Clear all files and subdirectories in the given directory path.
        If the directory doesn't exist, create it.

        Args:
            directory: Path to the directory to clear.
        """
        logger.info(f"Clearing directory: {directory}")

        # Remove directory if it exists
        if directory.exists():
            # Remove all files and subdirectories
            for item in directory.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        else:
            # Create directory if it doesn't exist
            directory.mkdir(exist_ok=True)

    def get_normalized_path(self, url: str) -> str:
        """
        Normalize URL path for consistency.

        Args:
            url: The URL to normalize.

        Returns:
            Normalized path string.
        """
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")

        # Handle root path
        if not path:
            return "index"

        # For all other paths, just use the path without leading slashes
        return path.lstrip("/")

    def get_file_paths(self, url_path: str) -> tuple[Path, Path, str]:
        """
        Generate file paths for HTML and Markdown files.

        Args:
            url_path: The URL path.

        Returns:
            Tuple of (html_path, markdown_path, base_path).
        """
        normalized = self.get_normalized_path(url_path)

        # Create directory structure if needed
        parts = normalized.split("/")
        if len(parts) > 1:
            directory = "/".join(parts[:-1])
            html_dir = self.html_dir / directory
            md_dir = self.markdown_dir / directory
            html_dir.mkdir(parents=True, exist_ok=True)
            md_dir.mkdir(parents=True, exist_ok=True)

        html_path = self.html_dir / f"{normalized}.html"
        markdown_path = self.markdown_dir / f"{normalized}.md"

        return html_path, markdown_path, normalized

    def extract_page_info(self, soup: BeautifulSoup) -> tuple[str, str]:
        """
        Extract title and description from HTML.

        Args:
            soup: BeautifulSoup object of the page.

        Returns:
            Tuple of (title, description).
        """
        title = soup.title.string if soup.title else "No Title"

        description_meta = soup.find("meta", attrs={"name": "description"})
        description = description_meta.get("content", "") if description_meta else ""

        # Clean up title and description - remove leading/trailing whitespace,
        # carriage returns, and consecutive spaces
        title = self.clean_text(title)
        description = self.clean_text(description)

        return title, description

    def clean_text(self, text: str) -> str:
        """
        Clean text by removing leading/trailing whitespace, carriage returns,
        and consecutive spaces.

        Args:
            text: The text string to clean.

        Returns:
            Cleaned text string.
        """
        if not text:
            return ""

        # Remove carriage returns and newlines
        text = text.replace("\r", " ").replace("\n", " ")

        # Replace consecutive spaces with a single space using regex
        text = re.sub(r"\s+", " ", text)

        # Remove leading and trailing whitespace
        text = text.strip()

        return text

    def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """
        Extract links from the page that belong to the same domain.

        Args:
            soup: BeautifulSoup object of the page.
            current_url: The current URL being processed.

        Returns:
            List of URLs to visit.
        """
        links = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            absolute_url = urljoin(self.base_url, href)

            # Only include links to the same domain
            if absolute_url.startswith(self.base_url):
                # Convert to relative path
                relative_path = urlparse(absolute_url).path
                if (
                    relative_path
                    and relative_path not in self.visited
                    and relative_path not in self.to_visit
                ):
                    links.append(relative_path)

        return links

    def download_page(self, url_path: str) -> Optional[BeautifulSoup]:
        """
        Download a page and save it as HTML.

        Args:
            url_path: The URL path to download.

        Returns:
            BeautifulSoup object of the downloaded page or None if failed.
        """
        full_url = urljoin(self.base_url, url_path)
        logger.info(f"Downloading: {full_url}")

        try:
            response = requests.get(full_url, timeout=30)
            response.raise_for_status()

            html_content = response.text
            html_path, _, _ = self.get_file_paths(url_path)

            # Save HTML content
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return BeautifulSoup(html_content, "html.parser")
        except Exception as e:
            logger.error(f"Failed to download {full_url}: {e}")
            return None

    def convert_to_markdown(self, html_path: Path, markdown_path: Path) -> bool:
        """
        Convert HTML to Markdown using MarkItDown.

        Args:
            html_path: Path to the HTML file.
            markdown_path: Path to save the Markdown file.

        Returns:
            True if conversion successful, False otherwise.
        """
        try:
            result = self.md_converter.convert(str(html_path))

            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(result.text_content)

            return True
        except Exception as e:
            logger.error(f"Failed to convert {html_path} to markdown: {e}")
            return False

    def crawl(self) -> Dict[str, PageInfo]:
        """
        Crawl the website, download pages, convert to markdown, and create site map.

        Returns:
            Dictionary containing the site map.
        """
        while self.to_visit:
            current_path = self.to_visit.pop(0)

            if current_path in self.visited:
                continue

            self.visited.add(current_path)

            soup = self.download_page(current_path)
            if not soup:
                continue

            # Get file paths
            html_path, markdown_path, base_path = self.get_file_paths(current_path)

            # Extract page info
            title, description = self.extract_page_info(soup)

            # Convert to markdown
            markdown_success = self.convert_to_markdown(html_path, markdown_path)

            # Add to site map
            self.site_map[base_path] = {
                "base": base_path,
                "html": f"./html/{base_path}.html",
                "markdown": f"./markdown/{base_path}.md" if markdown_success else "",
                "name": title,
                "description": description,
            }

            # Extract links and add to queue
            new_links = self.extract_links(soup, current_path)
            self.to_visit.extend(new_links)

            logger.info(f"Processed: {current_path} ({len(self.to_visit)} remaining)")

        return self.site_map

    def save_site_map(self, output_file: str = "site_map.json") -> None:
        """
        Save the site map to a JSON file.

        Args:
            output_file: Path to save the site map JSON.
        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.site_map, f, indent=2)

        logger.info(f"Site map saved to {output_file}")


def main() -> None:
    """Main function to run the crawler."""
    logger.info("Starting mikecreighton.com website crawler")

    crawler = WebsiteCrawler()
    site_map = crawler.crawl()
    crawler.save_site_map()

    logger.info(f"Crawling complete. Downloaded {len(site_map)} pages.")


if __name__ == "__main__":
    main()
