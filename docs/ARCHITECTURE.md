# Architecture Documentation

This document explains the internal structure and design of the static site generator.

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Module Breakdown](#module-breakdown)
- [Data Flow](#data-flow)
- [Design Decisions](#design-decisions)

## Overview

The static site generator follows a functional, pipeline-based architecture where markdown content flows through a series of transformations to become formatted HTML.

### High-Level Architecture

```
┌─────────────────┐
│  Markdown Files │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Block Parser   │ (Split into blocks)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Inline Parser  │ (Parse inline syntax)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTML Generator │ (Create HTMLNodes)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Template Engine │ (Apply template)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  BeautifulSoup  │ (Format HTML)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   HTML Files    │
└─────────────────┘
```

## Core Concepts

### 1. TextNode

**Purpose:** Represents a piece of inline text with semantic meaning.

**Design:**
```python
class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text           # The actual text content
        self.text_type = text_type # Type (bold, italic, link, etc.)
        self.url = url            # Optional URL for links/images
```

**Types:**
- `TEXT` - Plain text
- `BOLD` - Bold text
- `ITALIC` - Italic text
- `CODE` - Inline code
- `LINK` - Hyperlink
- `IMAGE` - Image

**Why:**
- Separates parsing from HTML generation
- Easy to test and extend
- Clear semantic meaning

### 2. HTMLNode

**Purpose:** Abstract representation of HTML elements that can be rendered to strings.

**Design:**
```python
class HTMLNode:
    def __init__(self, tag, value, children, props):
        self.tag = tag          # HTML tag name (div, p, etc.)
        self.value = value      # Text content (for leaf nodes)
        self.children = children # Child nodes (for parent nodes)
        self.props = props      # HTML attributes (href, src, etc.)

    def to_html(self):
        """Convert to HTML string"""
        raise NotImplementedError
```

**Subclasses:**

**LeafNode** - No children (e.g., `<b>text</b>`, `<img />`)
```python
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError("Leaf nodes require a value")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
```

**ParentNode** - Has children (e.g., `<div>...</div>`)
```python
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("Parent nodes require a tag")
        if not self.children:
            raise ValueError("Parent nodes require children")

        children_html = "".join(child.to_html() for child in self.children)
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"
```

**Why:**
- Composite pattern for tree structure
- Type-safe HTML generation
- Prevents malformed HTML
- Easy to test without rendering

### 3. Block Types

**Purpose:** Categorize markdown blocks for correct rendering.

**Enum:**
```python
class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
```

**Detection Logic:**
- Headings: Start with `#` (1-6 times)
- Code: Wrapped in triple backticks
- Quote: Lines start with `>`
- Unordered list: Lines start with `- `
- Ordered list: Lines start with `1. `, `2. `, etc.
- Paragraph: Default fallback

## Module Breakdown

### `textnode.py`

**Responsibility:** Define TextNode class and types.

**Key Functions:**
- `TextNode.__init__()` - Create text node
- `TextNode.__eq__()` - Compare nodes for testing
- `TextNode.__repr__()` - String representation

**Dependencies:** None (pure data class)

### `htmlnode.py`

**Responsibility:** Define HTML node abstraction.

**Key Classes:**
- `HTMLNode` - Base class
- `LeafNode` - Terminal nodes
- `ParentNode` - Container nodes

**Key Methods:**
- `to_html()` - Generate HTML string
- `props_to_html()` - Convert dict to HTML attributes

**Dependencies:** None

### `inline_markdown.py`

**Responsibility:** Parse inline markdown syntax.

**Key Functions:**

1. **`split_nodes_delimiter(nodes, delimiter, text_type)`**
   - Split TextNodes by delimiter (e.g., `**` for bold)
   - Returns new list of TextNodes

2. **`extract_markdown_images(text)`**
   - Regex: `!\[([^\[\]]*)\]\(([^\(\)]*)\)`
   - Returns list of (alt_text, url) tuples

3. **`extract_markdown_links(text)`**
   - Regex: `(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)`
   - Negative lookbehind prevents matching images
   - Returns list of (link_text, url) tuples

4. **`split_nodes_image(nodes)` / `split_nodes_link(nodes)`**
   - Split TextNodes on image/link syntax
   - Create IMAGE/LINK type nodes

5. **`text_to_textnodes(text)`**
   - **Main pipeline function**
   - Applies all inline parsing in order:
     ```python
     nodes = [TextNode(text, TextType.TEXT)]
     nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
     nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
     nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
     nodes = split_nodes_image(nodes)
     nodes = split_nodes_link(nodes)
     return nodes
     ```

6. **`text_node_to_html_node(text_node)`**
   - Convert TextNode → HTMLNode (LeafNode)
   - Maps each TextType to appropriate HTML tag

**Dependencies:** `textnode`, `htmlnode`

### `block_markdown.py`

**Responsibility:** Parse block-level markdown.

**Key Functions:**

1. **`markdown_to_blocks(markdown)`**
   - Split on `\n\n` (double newline)
   - Strip whitespace
   - Remove empty blocks

2. **`block_to_block_type(block)`**
   - Analyze block content
   - Return BlockType enum

3. **Block-specific converters:**
   - `paragraph_to_html_node()` - Wrap text in `<p>`
   - `heading_to_html_node()` - Count `#`, create `<h1>` - `<h6>`
   - `code_to_html_node()` - Wrap in `<pre><code>`
   - `quote_to_html_node()` - Strip `>`, wrap in `<blockquote>`
   - `unordered_list_to_html_node()` - Create `<ul><li>` structure
   - `ordered_list_to_html_node()` - Create `<ol><li>` structure

4. **`text_to_children(text)`**
   - Helper: Parse inline markdown within a block
   - Returns list of HTMLNodes

5. **`block_to_html_node(block)`**
   - Determine block type
   - Call appropriate converter
   - Return HTMLNode

6. **`markdown_to_html_node(markdown)`**
   - **Main entry point**
   - Split into blocks
   - Convert each block to HTMLNode
   - Wrap all in `<div>`

**Dependencies:** `htmlnode`, `inline_markdown`

### `generate_page.py`

**Responsibility:** Orchestrate page generation.

**Key Functions:**

1. **`extract_title(markdown)`**
   - Find first line starting with `# `
   - Extract title text
   - Raise exception if not found

2. **`generate_page(from_path, template_path, dest_path, basepath)`**
   - Read markdown file
   - Read template file
   - Convert markdown → HTML (via `markdown_to_html_node()`)
   - Replace template placeholders:
     - `{{ Title }}` - Page title
     - `{{ Content }}` - Generated HTML
     - `{{ BasePath }}` - Base URL path
   - Format HTML with BeautifulSoup
   - Write to destination

3. **`generate_page_recursive(dir_path_content, template_path, dest_dir_path, basepath)`**
   - Recursively process directory tree
   - Convert `.md` files to `.html`
   - Preserve directory structure

**Dependencies:** `block_markdown`, `beautifulsoup4`

### `copystatic.py`

**Responsibility:** Copy static files to output directory.

**Key Functions:**

1. **`copy_files_recursive(source_dir, dest_dir)`**
   - Delete destination if exists
   - Recursively copy directory tree
   - Preserve structure

**Dependencies:** `os`, `shutil`

### `main.py`

**Responsibility:** Entry point, orchestrate build process.

**Flow:**
```python
def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"

    # 1. Copy static files
    copy_files_recursive("./static", "./public")

    # 2. Generate HTML pages
    generate_page_recursive(
        "./content",
        "./template.html",
        "./public",
        basepath
    )
```

**Dependencies:** All modules

## Data Flow

### Example: Converting Markdown to HTML

**Input:** `content/index.md`
```markdown
# Welcome

This is **bold** and this is _italic_.

![Image](images/photo.png)
```

**Step 1: Split into blocks** (`markdown_to_blocks`)
```python
[
    "# Welcome",
    "This is **bold** and this is _italic_.\n\n![Image](images/photo.png)"
]
```

**Step 2: Identify block types** (`block_to_block_type`)
```python
[
    BlockType.HEADING,
    BlockType.PARAGRAPH
]
```

**Step 3: Parse inline markdown** (`text_to_textnodes`)

For "This is **bold** and this is _italic_."
```python
[
    TextNode("This is ", TextType.TEXT),
    TextNode("bold", TextType.BOLD),
    TextNode(" and this is ", TextType.TEXT),
    TextNode("italic", TextType.ITALIC),
    TextNode(".\n\n", TextType.TEXT),
    TextNode("photo", TextType.IMAGE, "images/photo.png")
]
```

**Step 4: Convert to HTMLNodes** (`text_node_to_html_node`)
```python
[
    LeafNode(None, "This is "),
    LeafNode("b", "bold"),
    LeafNode(None, " and this is "),
    LeafNode("i", "italic"),
    LeafNode(None, ".\n\n"),
    LeafNode("img", "", {"src": "images/photo.png", "alt": "photo"})
]
```

**Step 5: Build block nodes**
```python
ParentNode("h1", [LeafNode(None, "Welcome")])
ParentNode("p", [
    LeafNode(None, "This is "),
    LeafNode("b", "bold"),
    # ... etc
])
```

**Step 6: Generate HTML** (`to_html()`)
```html
<div>
<h1>Welcome</h1>
<p>This is <b>bold</b> and this is <i>italic</i>.</p>
<p><img src="images/photo.png" alt="photo"></p>
</div>
```

**Step 7: Apply template**
```html
<!doctype html>
<html>
  <head>
    <base href="/" />
    <title>Welcome</title>
    ...
  </head>
  <body>
    <article>
      <div>
        <h1>Welcome</h1>
        <p>This is <b>bold</b> and this is <i>italic</i>.</p>
        <p><img src="images/photo.png" alt="photo"></p>
      </div>
    </article>
  </body>
</html>
```

**Step 8: Format with BeautifulSoup** (`prettify()`)
```html
<!DOCTYPE html>
<html>
 <head>
  <base href="/"/>
  <title>
   Welcome
  </title>
  ...
 </head>
 <body>
  <article>
   <div>
    <h1>
     Welcome
    </h1>
    <p>
     This is
     <b>
      bold
     </b>
     and this is
     <i>
      italic
     </i>
     .
    </p>
    <p>
     <img alt="photo" src="images/photo.png"/>
    </p>
   </div>
  </article>
 </body>
</html>
```

**Output:** `public/index.html`

## Design Decisions

### Why TextNode?

**Alternative:** Parse markdown directly to HTML strings.

**Chosen approach:** Intermediate TextNode representation.

**Reasons:**
1. **Separation of concerns** - Parsing separate from rendering
2. **Testability** - Can test parsing without HTML
3. **Flexibility** - Easy to add new output formats (JSON, XML, etc.)
4. **Debugging** - Can inspect parse tree

### Why HTMLNode abstraction?

**Alternative:** Generate HTML strings directly.

**Chosen approach:** Object-oriented node tree.

**Reasons:**
1. **Type safety** - Catch errors before rendering
2. **Composability** - Build complex structures easily
3. **Testability** - Test structure without string comparison
4. **Extensibility** - Easy to add new node types

### Why BeautifulSoup for formatting?

**Alternative:** Write custom HTML formatter.

**Chosen approach:** Use BeautifulSoup's `prettify()`.

**Reasons:**
1. **Reliability** - Battle-tested library
2. **Correctness** - Handles edge cases
3. **Readability** - Generated HTML is readable
4. **Maintainability** - Less code to maintain

### Why separate block and inline parsing?

**Alternative:** Single parser for all markdown.

**Chosen approach:** Two-phase parsing (block then inline).

**Reasons:**
1. **Clarity** - Each module has single responsibility
2. **Correctness** - Block structure determines context for inline
3. **Testability** - Test each phase independently
4. **Markdown spec** - Follows markdown's two-phase nature

### Why use `uv` instead of `pip`?

**Alternative:** Traditional `requirements.txt` + `pip`.

**Chosen approach:** `pyproject.toml` + `uv`.

**Reasons:**
1. **Speed** - `uv` is 10-100x faster than pip
2. **Modern** - PEP 621 standard project metadata
3. **Lock file** - `uv.lock` ensures reproducible builds
4. **Developer experience** - `uv run` handles venv automatically

## Performance Considerations

### Current Implementation

- **File I/O:** Reads entire files into memory (suitable for typical sites)
- **Parsing:** Single-pass for most operations
- **Recursion:** Uses recursion for directory traversal (fine for typical depths)

### Optimization Opportunities

If building very large sites:

1. **Streaming:** Process files in chunks
2. **Parallelization:** Generate pages concurrently
3. **Incremental builds:** Only rebuild changed files
4. **Caching:** Cache parsed markdown

Not implemented because:
- Current approach is simple and maintainable
- Performance adequate for typical use cases
- Premature optimization avoided

## Testing Strategy

### Unit Tests

Each module has corresponding test file:
- `test_textnode.py` - TextNode behavior
- `test_htmlnode.py` - HTML generation
- `test_inline_markdown.py` - Inline parsing
- `test_block_markdown.py` - Block parsing
- `test_generate_page.py` - Page generation

### Test Coverage

96+ tests covering:
- Normal cases
- Edge cases (empty input, malformed markdown)
- Error cases (missing required elements)

### Why Comprehensive Tests?

- **Confidence** - Refactor without breaking things
- **Documentation** - Tests show how to use code
- **Regression prevention** - Catch bugs early

## Extension Points

### Adding New Markdown Features

1. **Inline syntax:** Add to `inline_markdown.py`
   - Create new TextType
   - Add delimiter splitting or regex extraction
   - Update `text_node_to_html_node()`

2. **Block syntax:** Add to `block_markdown.py`
   - Create new BlockType
   - Update `block_to_block_type()` detection
   - Add converter function

3. **HTML output:** Modify HTMLNode classes
   - Add new node types if needed
   - Update `to_html()` methods

### Adding New Output Formats

Create new converter module:
```python
# json_output.py
def text_node_to_json(node):
    return {
        "type": node.text_type.value,
        "text": node.text,
        "url": node.url
    }
```

No changes to parsing logic needed!

## Conclusion

The architecture prioritizes:
1. **Simplicity** - Easy to understand and modify
2. **Correctness** - Type-safe, well-tested
3. **Maintainability** - Clear separation of concerns
4. **Extensibility** - Easy to add features

Trade-offs:
- Performance for readability
- Flexibility over optimization
- Explicit over implicit

This makes the codebase accessible to new developers while remaining robust for production use.
