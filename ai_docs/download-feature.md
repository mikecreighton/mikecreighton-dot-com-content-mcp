# MikeCreighton.com Downloader

`download.py`
The script will crawl mikecreighton.com and download all pages as HTML files to the local `html` folder.
It will use [`MarkItDown`](https://github.com/microsoft/markitdown) to the convert the HTML file into a Markdown file. MarkItDown is a lightweight Python utility for converting various files to Markdown for use with LLMs and related text analysis pipelines.
It will save each HTML file's corresponding Markdown file into the local `markdown` folder.

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
  "base": "{page_path}/{page}", // Used for resource listing in the MCP server
  "html": "./html/{page_path}/{page}.html", // Used to reference the corresponding local HTML file
  "markdown": "./markdown/{page_path}/{page}.md", // Used to reference the corresponding local Markdown file
  "name": "{title of the page extracted from the <title> tag}",
  "description": "{description of the page extracted from the <meta name='description'> tag}"
}
```

Note that it is important to extract the page title and meta description content values for use in this JSON file.

## Files

Files will look like:

original URL: https://mikecreighton.com/
- base: `index`
- `./html/index.html` 
- `./markdown/index.md`

original URL: https://mikecreighton.com/writing/help-your-ide-help-you/
- base: `writing/help-your-ide-help-you`
- `./html/writing/help-your-ide-help-you.html`
- `./markdown/writing/help-your-ide-help-you.md`

original URL: https://mikecreighton.com/writing/
- base: `writing`
- `./html/writing.html`
- `./markdown/writing.md`
