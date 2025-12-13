"""
Page generation module.

This module handles converting markdown files to HTML pages by:
1. Reading markdown content
2. Converting to HTML via markdown parser
3. Applying HTML template
4. Formatting output with BeautifulSoup
5. Writing to destination file
"""
import os

from bs4 import BeautifulSoup
from block_markdown import markdown_to_html_node


def extract_title(markdown):
    """
    Extract the page title from markdown content.

    Looks for the first H1 heading (line starting with "# ") and returns
    the text after the "#". This title is used in the HTML <title> tag.

    Args:
        markdown: String containing markdown content

    Returns:
        String containing the title text (without the "# " prefix)

    Raises:
        Exception: If no H1 heading is found in the markdown
    """
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("No h1 header found in markdown")

def generate_page(from_path, template_path, dest_path, basepath="/"):
    """
    Generate an HTML page from a markdown file.

    This function orchestrates the entire page generation process:
    1. Reads the markdown source file
    2. Reads the HTML template
    3. Converts markdown to HTML
    4. Replaces template placeholders ({{ Title }}, {{ Content }}, {{ BasePath }})
    5. Formats the HTML with BeautifulSoup for readability
    6. Writes the result to the destination path

    Args:
        from_path: Path to source markdown file
        template_path: Path to HTML template file
        dest_path: Path where generated HTML will be written
        basepath: Base URL path for the site (e.g., "/" or "/repo-name/")
                 Used in <base href="{{ BasePath }}"> tag for relative URL resolution

    Example:
        generate_page(
            "content/index.md",
            "template.html",
            "public/index.html",
            "/my-site/"
        )
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r") as f:
        markdown = f.read()

    with open(template_path, "r") as f:
        template = f.read()

    html_node = markdown_to_html_node(markdown)
    html_content = html_node.to_html()

    title = extract_title(markdown)

    page = template.replace("{{ Title }}", title)
    page = page.replace("{{ Content }}", html_content)
    page = page.replace("{{ BasePath }}", basepath)

    # Format HTML with BeautifulSoup for better readability
    soup = BeautifulSoup(page, 'html.parser')
    formatted_page = soup.prettify()

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w") as f:
        f.write(formatted_page)

def generate_page_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    """
    Recursively generate HTML pages from a directory tree of markdown files.

    Walks through the content directory structure and:
    - Converts all .md files to .html files
    - Preserves the directory structure in the output
    - Recursively processes subdirectories

    This allows you to organize content in nested directories (e.g., blog/posts/2024/)
    and the same structure will be maintained in the generated site.

    Args:
        dir_path_content: Root directory containing markdown files
        template_path: Path to HTML template (same template used for all pages)
        dest_dir_path: Root directory where HTML files will be written
        basepath: Base URL path passed to all generated pages

    Example:
        generate_page_recursive(
            "content",        # Input: content/blog/post1.md
            "template.html",
            "public",         # Output: public/blog/post1.html
            "/"
        )
    """
    for filename in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, filename)
        dest_path = os.path.join(dest_dir_path, filename)

        if os.path.isfile(from_path):
            # Only process markdown files
            if from_path.endswith(".md"):
                # Change .md extension to .html
                dest_path = dest_path[:-3] + ".html"
                generate_page(from_path, template_path, dest_path, basepath)
        else:
            # Recurse into subdirectories
            generate_page_recursive(from_path, template_path, dest_path, basepath)
