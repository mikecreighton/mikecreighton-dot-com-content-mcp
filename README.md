# MikeCreighton.com Content MCP Server

This is a Model Context Protocol (MCP) server that will provide all of the [Mike Creighton Consulting website](https://mikecreighton.com) pages as Resources to any MCP clients.

## Primary Use Case

It's a way for me to collaborate with Claude on marketing strategies, content ideas, content critiques, and content creation. It also acts as an easy way to keep Claude up-to-date on what I'm doing with my consulting practice. Basically: Claude can know my business better.

## Tools

- `list_mikecreighton_website_pages` - Lists all available pages from the website
- `get_mikecreighton_website_page_content` - Gets a specific page's content
- `search_mikecreighton_website_pages` - A simple keyword search across page titles and page descriptions

## Resources

- Each page is available as an individual named Resource in case I want to explictly reference a file within a conversation
- The Resources are defined at runtime in their Markdown format

## Example Queries

- "What has Mike written about lately on his website?"
- "What are the services that Mike offers?"
- "Do you think Mike would be able to help me with designing my marketing website?"
- "I'm new to generative AI, and I need some ideas for my business. Can Mike help me?"
- "I'm trying to build a 0->1 prototype to test out an gen AI-powered idea. I work at an agency and need to help with new business intake... like transforming a client brief into an RFP response starter. Has Mike ever built anything like that?"

## Utils

`download.py`
Crawls mikecreighton.com and downloads all pages as HTML files to the local `html` folder. It uses [`MarkItDown`](https://github.com/microsoft/markitdown) to the convert the HTML files into Markdown files, saving each HTML file's corresponding Markdown file into the local `markdown` folder.

Finally, it creates a map of the website as a JSON object, representing the hierarchy of the original website. Each page consists of the following schema:

```json
{
  "html": "./html/{page_path}/{page}.html",
  "markdown": "./markdown/{page_path}/{page}.md",
  "name": "{title of the page extracted from the <title> tag}",
  "description": "{description of the page extracted from the <description> tag}"
}
```

With each run, the utility will clear out any existing files in the `html` and `markdown` folders. Note that these are _not_ committed to the repo, as the website is updated periodically.