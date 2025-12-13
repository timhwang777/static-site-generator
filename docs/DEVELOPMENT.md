# Development Guide

This guide covers everything you need to know to develop and contribute to the static site generator.

## Table of Contents

- [Setup](#setup)
- [Project Architecture](#project-architecture)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Adding Features](#adding-features)

## Setup

### 1. Install uv

The project uses `uv` for dependency management. Install it:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

### 2. Clone and Setup

```bash
git clone https://github.com/timhwang777/static-site-generator.git
cd static-site-generator
uv sync
```

This creates a `.venv/` directory with all dependencies installed.

### 3. IDE Setup

**VS Code:**
1. Open Command Palette (Cmd+Shift+P)
2. Select "Python: Select Interpreter"
3. Choose `.venv/bin/python`

**PyCharm:**
1. Settings → Project → Python Interpreter
2. Add Interpreter → Existing Environment
3. Select `.venv/bin/python`

This enables autocomplete, type hints, and linting.

## Project Architecture

### Core Components

#### 1. TextNode (`src/textnode.py`)
Represents inline text with a type (text, bold, italic, code, link, image).

```python
TextNode("Hello", TextType.TEXT)
TextNode("bold text", TextType.BOLD)
TextNode("link", TextType.LINK, "https://example.com")
```

#### 2. HTMLNode (`src/htmlnode.py`)
Abstract representation of HTML elements.

- `LeafNode` - Elements with no children (e.g., `<b>text</b>`, `<img>`)
- `ParentNode` - Elements with children (e.g., `<div>`, `<p>`)

```python
LeafNode("b", "bold text")
ParentNode("div", [child1, child2])
```

#### 3. Inline Markdown Parser (`src/inline_markdown.py`)
Converts inline markdown syntax to TextNodes:
- `**bold**` → Bold
- `_italic_` → Italic
- `` `code` `` → Code
- `![alt](url)` → Image
- `[text](url)` → Link

#### 4. Block Markdown Parser (`src/block_markdown.py`)
Converts block-level markdown to HTMLNodes:
- Paragraphs
- Headings (h1-h6)
- Code blocks
- Blockquotes
- Lists (ordered/unordered)

#### 5. Page Generator (`src/generate_page.py`)
Orchestrates the conversion:
1. Read markdown file
2. Convert to HTML
3. Apply template
4. Format with BeautifulSoup
5. Write output

### Data Flow

```
Markdown File
    ↓
markdown_to_blocks() → Split into blocks
    ↓
block_to_block_type() → Identify block type
    ↓
text_to_textnodes() → Parse inline markdown
    ↓
text_node_to_html_node() → Convert to HTMLNodes
    ↓
to_html() → Generate HTML string
    ↓
BeautifulSoup.prettify() → Format HTML
    ↓
HTML File
```

## Development Workflow

### Running the Development Server

```bash
./main.sh
```

This:
1. Builds the site with base path `/`
2. Starts HTTP server on port 8888
3. Navigate to http://localhost:8888

Changes to markdown files require rerunning the script.

### Making Code Changes

1. **Create a branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**

3. **Run tests:**
```bash
./test.sh
```

4. **Test manually:**
```bash
./main.sh
# Visit http://localhost:8888 and verify
```

5. **Commit:**
```bash
git add .
git commit -m "Add your feature"
```

### Using uv Commands

**Add a new dependency:**
```bash
uv add package-name
```

**Remove a dependency:**
```bash
uv remove package-name
```

**Update dependencies:**
```bash
uv lock --upgrade
```

**Run Python without activating venv:**
```bash
uv run python script.py
```

**Activate venv manually (optional):**
```bash
source .venv/bin/activate
```

## Code Style

### Conventions

- **Functions:** Use `snake_case`
- **Classes:** Use `PascalCase`
- **Constants:** Use `UPPER_SNAKE_CASE`
- **Indentation:** 4 spaces
- **Line length:** Try to keep under 100 characters

### Example

```python
def process_markdown_block(block: str) -> HTMLNode:
    """
    Convert a markdown block to an HTMLNode.

    Args:
        block: A string containing markdown text

    Returns:
        An HTMLNode representing the block
    """
    block_type = block_to_block_type(block)

    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    # ...
```

### Type Hints

Use type hints for function parameters and return values:

```python
def extract_title(markdown: str) -> str:
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("No h1 header found")
```

## Testing

### Running Tests

**All tests:**
```bash
./test.sh
# or
uv run python -m unittest discover -s src
```

**Specific test file:**
```bash
uv run python -m unittest src.test_htmlnode
```

**Single test:**
```bash
uv run python -m unittest src.test_htmlnode.TestHTMLNode.test_to_html
```

### Writing Tests

Tests are in `src/test_*.py` files. Example:

```python
import unittest
from htmlnode import LeafNode

class TestLeafNode(unittest.TestCase):
    def test_to_html_with_value(self):
        node = LeafNode("p", "Hello world")
        self.assertEqual(node.to_html(), "<p>Hello world</p>")

    def test_to_html_with_props(self):
        node = LeafNode("a", "Click", {"href": "https://example.com"})
        self.assertEqual(
            node.to_html(),
            '<a href="https://example.com">Click</a>'
        )
```

### Test Coverage

Current coverage: 96 tests across:
- `test_textnode.py` - TextNode tests
- `test_htmlnode.py` - HTMLNode tests
- `test_inline_markdown.py` - Inline parsing tests
- `test_block_markdown.py` - Block parsing tests
- `test_generate_page.py` - Page generation tests

## Adding Features

### Example: Adding Support for Strikethrough

1. **Update TextNode:**
```python
# src/textnode.py
class TextType(Enum):
    # ... existing types
    STRIKETHROUGH = "strikethrough"
```

2. **Add parser:**
```python
# src/inline_markdown.py
def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "~~", TextType.STRIKETHROUGH)  # Add this
    # ... rest
```

3. **Add HTML conversion:**
```python
# src/inline_markdown.py
def text_node_to_html_node(text_node):
    # ... existing cases
    elif text_node.text_type == TextType.STRIKETHROUGH:
        return LeafNode("s", text_node.text)
```

4. **Write tests:**
```python
# src/test_inline_markdown.py
def test_strikethrough(self):
    nodes = text_to_textnodes("Text with ~~strikethrough~~")
    self.assertEqual(len(nodes), 2)
    self.assertEqual(nodes[1].text_type, TextType.STRIKETHROUGH)
```

5. **Run tests and verify:**
```bash
./test.sh
./main.sh
```

## Debugging Tips

### Print Debugging

Add print statements to trace execution:

```python
def generate_page(from_path, template_path, dest_path, basepath="/"):
    print(f"Generating page from {from_path} to {dest_path}")
    # ... rest of function
```

### Using Python Debugger

```python
import pdb

def problematic_function():
    pdb.set_trace()  # Execution will pause here
    # ... rest
```

### Check Generated HTML

Look at `public/*.html` files to verify output:

```bash
cat public/index.html
# or
open public/index.html
```

## Common Tasks

### Update Template

Edit `template.html`:
```html
<!doctype html>
<html>
  <head>
    <base href="{{ BasePath }}" />
    <meta charset="utf-8" />
    <title>{{ Title }}</title>
    <link href="index.css" rel="stylesheet" />
  </head>
  <body>
    <article>{{ Content }}</article>
  </body>
</html>
```

Placeholders:
- `{{ Title }}` - Extracted from first `# Heading`
- `{{ Content }}` - Generated HTML from markdown
- `{{ BasePath }}` - Passed via command line for GitHub Pages

### Add CSS Styles

Edit `static/index.css`:
```css
body {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
```

Run `./main.sh` to see changes.

### Add Static Files

1. Place files in `static/` directory
2. Run build script - files automatically copied to `public/`
3. Reference in markdown: `![Image](images/photo.png)`

## Getting Help

- Check [ARCHITECTURE.md](ARCHITECTURE.md) for code structure
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
- Open an issue on GitHub
- Review existing tests for examples

## Resources

- [Python unittest docs](https://docs.python.org/3/library/unittest.html)
- [uv documentation](https://docs.astral.sh/uv/)
- [Markdown syntax](https://www.markdownguide.org/basic-syntax/)
- [BeautifulSoup docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
