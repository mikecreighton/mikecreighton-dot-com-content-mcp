# MikeCreighton.com Content MCP Server

This is a Model Context Protocol (MCP) server that will provide all of the mikecreighton.com website pages as resources to any MCP clients.

## Utils

`download.py`
Crawls mikecreighton.com and downloads all pages as HTML files to the local `html` folder. It will use [`MarkItDown`](https://github.com/microsoft/markitdown) to the convert the HTML file into a Markdown file, saving each HTML file's corresponding Markdown file into the local `markdown` folder.

**Example of MarkItDown Python API Usage**

```python
from markitdown import MarkItDown

md = MarkItDown(enable_plugins=False)
result = md.convert("test.html")
print(result.text_content)
```

Finally, it will create a map of the website as a JSON object, representing the hierarchy of the original website. Each page consists of the following schema:

```json
{
  "file": "./html/{page_path}/{page}.html",
  "markdown": "./markdown/{page_path}/{page}.md",
  "name": "{title of the page extracted from the <title> tag}",
  "description": "{description of the page extracted from the <description> tag}"
}
```