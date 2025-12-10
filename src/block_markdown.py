from enum import Enum

from htmlnode import ParentNode, LeafNode
from inline_markdown import text_node_to_html_node, text_to_textnodes
from textnode import TextNode, TextType


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    result = []
    for block in blocks:
        stripped = block.strip()
        if stripped != "":
            result.append(stripped)
    return result

def block_to_block_type(block):
    lines = block.split("\n")
    
    if block.startswith("#"):
        for i in range(1, 7):
            if block.startswith("#" * i + " "):
                return BlockType.HEADING

    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    is_ordered_list = True
    for i, line in enumerate(lines):
        expected_prefix = f"{i + 1}. "
        if not line.startswith(expected_prefix):
            is_ordered_list = False
            break
    if is_ordered_list:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children

def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph_text = " ".join(lines)
    children = text_to_children(paragraph_text)
    return ParentNode("p", children)

def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break

    heading_text = block[level + 1:]
    children = text_to_children(heading_text)
    return ParentNode(f"h{level}", children)

def code_to_html_node(block):
    lines = block.split("\n")
    code_lines = lines[1:-1]
    code_text = "\n".join(code_lines)
    if code_text:
        code_text += "\n"

    code_node = LeafNode(None, code_text)
    return ParentNode("pre", [ParentNode("code", [code_node])])

def quote_to_html_node(block):
    lines = block.split("\n")
    stripped_lines = []
    for line in lines:
        if line.startswith(">"):
            stripped_lines.append(line[1:].lstrip())
        else:
            stripped_lines.append(line)
    quote_text = " ".join(stripped_lines)
    children = text_to_children(quote_text)
    return ParentNode("blockquote", children)

def unordered_list_to_html_node(block):
    lines = block.split("\n")
    list_items = []
    for line in lines:
        item_text = line[2:]
        children = text_to_children(item_text)
        list_items.append(ParentNode("li", children))
    return ParentNode("ul", list_items)

def ordered_list_to_html_node(block):
    lines = block.split("\n")
    list_items = []
    for i, line in enumerate(lines):
        prefix = f"{i + 1}. "
        item_text = line[len(prefix):]
        children = text_to_children(item_text)
        list_items.append(ParentNode("li", children))
    return ParentNode("ol", list_items)

def block_to_html_node(block):
    """Convert a single block to an HTMLNode based on its type."""
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    elif block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    elif block_type == BlockType.CODE:
        return code_to_html_node(block)
    elif block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    elif block_type == BlockType.UNORDERED_LIST:
        return unordered_list_to_html_node(block)
    elif block_type == BlockType.ORDERED_LIST:
        return ordered_list_to_html_node(block)
    else:
        raise ValueError(f"Unknown block type: {block_type}")

def markdown_to_html_node(markdown):
    """Convert a full markdown document to a single parent HTMLNode."""
    blocks = markdown_to_blocks(markdown)
    block_nodes = []
    for block in blocks:
        html_node = block_to_html_node(block)
        block_nodes.append(html_node)
    return ParentNode("div", block_nodes)
