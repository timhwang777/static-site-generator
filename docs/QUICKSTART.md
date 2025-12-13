# Quick Start Guide

Get your static site generator up and running in 5 minutes!

## Step 1: Install uv

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Via pip (any platform)
```bash
pip install uv
```

### Verify installation
```bash
uv --version
```

## Step 2: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/timhwang777/static-site-generator.git
cd static-site-generator

# Install dependencies (automatic via uv)
uv sync
```

That's it! Dependencies are installed and you're ready to go.

## Step 3: Run the Development Server

```bash
./main.sh
```

Visit http://localhost:8888 in your browser to see your site!

## Step 4: Edit Content

Open `content/index.md` in your favorite text editor:

```markdown
# My Awesome Site

Welcome to my site built with a static site generator!

Here's some **bold text** and _italic text_.

![My Photo](images/photo.png)

[Visit my GitHub](https://github.com/yourusername)
```

Save the file, run `./main.sh` again, and refresh your browser.

## Step 5: Add More Pages

Create new markdown files in `content/`:

```bash
# Create a new page
touch content/about.md
```

Edit `content/about.md`:
```markdown
# About Me

This is my about page!
```

Run `./main.sh` and visit http://localhost:8888/about.html

## Step 6: Organize with Directories

```bash
# Create a blog directory
mkdir -p content/blog

# Add a blog post
cat > content/blog/my-first-post.md << 'EOF'
# My First Blog Post

This is my first post!

It will be available at /blog/my-first-post.html
EOF
```

The directory structure is preserved in the generated site!

## Step 7: Add Images

1. Place images in `static/images/`:
```bash
cp ~/Pictures/photo.jpg static/images/
```

2. Reference in markdown:
```markdown
![My Photo](images/photo.jpg)
```

## Step 8: Customize Styling

Edit `static/index.css`:

```css
body {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f5f5;
}

h1 {
  color: #333;
  border-bottom: 2px solid #007acc;
}
```

Rebuild and see your changes!

## Step 9: Deploy to GitHub Pages

### First Time Setup

1. **Create a GitHub repository** (if you haven't already)

2. **Push your code:**
```bash
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/repo-name.git
git push -u origin main
```

3. **Enable GitHub Pages:**
   - Go to repository Settings
   - Pages section
   - Source: "GitHub Actions"
   - Save

4. **Wait for deployment:**
   - Check Actions tab
   - Once complete, visit: `https://yourusername.github.io/repo-name/`

### Subsequent Deployments

Just push to main:
```bash
git add .
git commit -m "Update content"
git push
```

GitHub Actions automatically rebuilds and deploys!

## Common Tasks

### Add a New Blog Post

```bash
# Create file
cat > content/blog/$(date +%Y-%m-%d)-post-title.md << 'EOF'
# Post Title

Content here
EOF

# Build and view
./main.sh
```

### Test Production Build Locally

```bash
# Build with GitHub Pages path
./build.sh

# Serve
cd public
python -m http.server 8888

# Visit http://localhost:8888/static-site-generator/
```

### Run Tests

```bash
./test.sh
```

Should show:
```
Ran 96 tests in 0.002s
OK
```

### Update Dependencies

```bash
# Add new package
uv add package-name

# Remove package
uv remove package-name

# Update all packages
uv lock --upgrade
uv sync
```

## Markdown Cheat Sheet

### Headings
```markdown
# H1 Heading
## H2 Heading
### H3 Heading
```

### Text Formatting
```markdown
**bold text**
_italic text_
`inline code`
```

### Links and Images
```markdown
[Link Text](https://example.com)
![Image Alt](images/photo.png)
```

### Lists
```markdown
- Unordered item 1
- Unordered item 2

1. Ordered item 1
2. Ordered item 2
```

### Blockquotes
```markdown
> This is a quote
> It can span multiple lines
```

### Code Blocks
````markdown
```
function hello() {
  console.log("Hello!");
}
```
````

## Troubleshooting

### Port 8888 Already in Use
```bash
# Find and kill the process
lsof -ti:8888 | xargs kill

# Or use a different port
cd public && python -m http.server 9000
```

### CSS Not Loading
- Check that path is relative (no leading `/`)
- Rebuild the site: `./main.sh`
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+F5 (Windows)

### Tests Failing
```bash
# Reinstall dependencies
uv sync

# Run tests again
./test.sh
```

### Changes Not Showing
- Make sure you rebuilt: `./main.sh`
- Clear browser cache
- Check you're viewing the right URL

## Next Steps

- Read [DEVELOPMENT.md](DEVELOPMENT.md) to understand the code
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options
- Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Customize `template.html` for your design
- Add more markdown features
- Contribute improvements!

## Getting Help

- Check the [README](../README.md)
- Browse the [docs/](.) folder
- Open an issue on GitHub
- Read the inline code comments

## Useful Resources

- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Python unittest](https://docs.python.org/3/library/unittest.html)

Happy site building! 🚀
