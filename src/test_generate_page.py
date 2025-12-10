import unittest
from generate_page import extract_title


class TestExtractTitle(unittest.TestCase):
    def test_extract_title_simple(self):
        md = "# Hello"
        self.assertEqual(extract_title(md), "Hello")
    
    def test_extract_title_with_whitespace(self):
        md = "#   Hello World   "
        self.assertEqual(extract_title(md), "Hello World")
    
    def test_extract_title_with_other_content(self):
        md = """# My Title

Some paragraph text here.

## A subheading

More content."""
        self.assertEqual(extract_title(md), "My Title")
    
    def test_extract_title_h1_not_first(self):
        md = """Some intro text

# The Real Title

More content."""
        self.assertEqual(extract_title(md), "The Real Title")
    
    def test_extract_title_no_h1_raises(self):
        md = """## Not an h1

Some content

### Also not h1"""
        with self.assertRaises(Exception):
            extract_title(md)
    
    def test_extract_title_empty_raises(self):
        md = ""
        with self.assertRaises(Exception):
            extract_title(md)
    
    def test_extract_title_only_h2_raises(self):
        md = "## This is h2"
        with self.assertRaises(Exception):
            extract_title(md)


if __name__ == "__main__":
    unittest.main()
