"""
Static site generator main entry point.

This script orchestrates the entire site generation process:
1. Copy static assets (CSS, images) to public directory
2. Convert all markdown files to HTML pages
3. Apply template and base path configuration

Usage:
    python src/main.py [basepath]

    basepath: Optional base URL path for the site (default: "/")
              Examples:
              - "/" for root deployment (username.github.io)
              - "/repo-name/" for GitHub Pages project site
              - "/blog/" for subdirectory deployment

Examples:
    # Local development
    python src/main.py /

    # GitHub Pages deployment
    python src/main.py /static-site-generator/
"""
import sys

from copystatic import copy_files_recursive
from generate_page import generate_page_recursive

# Directory paths - modify these if you change project structure
dir_path_static = "./static"      # Static assets (CSS, images)
dir_path_public = "./public"      # Generated site output
dir_path_content = "./content"    # Markdown source files
template_path = "./template.html" # HTML template


def main():
    """
    Main build process.

    Steps:
    1. Parse command line arguments for basepath
    2. Copy all static files to public directory
    3. Recursively generate HTML pages from markdown files
    """
    # Default to root path
    basepath = "/"

    # Override with command line argument if provided
    if len(sys.argv) > 1:
        basepath = sys.argv[1]

    # Step 1: Copy static assets (CSS, images, etc.)
    # This deletes and recreates the public directory
    copy_files_recursive(dir_path_static, dir_path_public)

    # Step 2: Generate HTML pages from markdown
    # Processes all .md files in content directory recursively
    generate_page_recursive(dir_path_content, template_path, dir_path_public, basepath)


if __name__ == "__main__":
    main()
