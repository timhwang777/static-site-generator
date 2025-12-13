# Deployment Guide

This guide covers deploying your static site to GitHub Pages and other platforms.

## Table of Contents

- [GitHub Pages Deployment](#github-pages-deployment)
- [Testing Deployments](#testing-deployments)
- [Custom Domain Setup](#custom-domain-setup)
- [Alternative Platforms](#alternative-platforms)
- [Troubleshooting](#troubleshooting)

## GitHub Pages Deployment

### Automatic Deployment (Recommended)

The project includes a GitHub Actions workflow that automatically builds and deploys your site.

#### Initial Setup

1. **Push your code to GitHub:**
```bash
git remote add origin https://github.com/timhwang777/repo-name.git
git push -u origin main
```

2. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Navigate to **Settings** → **Pages**
   - Under "Build and deployment", select **Source**: "GitHub Actions"
   - Save

3. **Workflow triggers automatically:**
   - On every push to `main` branch
   - Builds site with correct base path
   - Deploys to GitHub Pages

4. **Access your site:**
   - URL: `https://yourusername.github.io/repo-name/`
   - Check deployment status in **Actions** tab

#### How It Works

The workflow file (`.github/workflows/deploy.yml`):

```yaml
on:
  push:
    branches:
      - main
  workflow_dispatch: # Manual trigger option

jobs:
  build-and-deploy:
    steps:
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Build site
        run: |
          # Normalizes base path (e.g., /repo-name/)
          if [ -n "$BASE_PATH" ] && [ "$BASE_PATH" != "/" ]; then
            BASE_PATH="${BASE_PATH%/}/"
          fi
          uv run python src/main.py "$BASE_PATH"

      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

**Key features:**
- ✅ Uses `uv` for fast dependency installation
- ✅ Caches dependencies for faster builds
- ✅ Automatically determines correct base path
- ✅ Deploys to GitHub Pages

### Manual Deployment

If you prefer to deploy manually:

1. **Build locally:**
```bash
./build.sh
```

2. **Commit the public/ directory** (modify `.gitignore` first)

3. **Configure GitHub Pages:**
   - Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `main`
   - Folder: `/public`

**Note:** Automatic deployment is preferred as it keeps the repository clean.

## Testing Deployments

### Testing on a Dev Branch

The workflow supports testing deployments from development branches.

#### Option 1: Manual Workflow Trigger

1. **Go to Actions tab** on GitHub
2. **Click "Deploy to GitHub Pages"** workflow
3. **Click "Run workflow"** button
4. **Select your dev branch** from dropdown
5. **Click "Run workflow"**

This builds and deploys your dev branch to GitHub Pages without automatic triggers.

#### Option 2: Add Branch to Workflow

Edit `.github/workflows/deploy.yml`:

```yaml
on:
  push:
    branches:
      - main
      - dev/feature-name  # Add your dev branch
```

**Important:** GitHub Pages can only host one site per repository. Deploying from a dev branch will **replace** the production site temporarily.

For separate dev/production URLs, consider:
- Using a separate repository for dev
- Using a different platform (Netlify, Vercel) for dev

### Local Testing

Always test locally before deploying:

```bash
# Build for GitHub Pages path
./build.sh

# Start local server
cd public
uv run python -m http.server 8888

# Visit http://localhost:8888/static-site-generator/
# Note the /static-site-generator/ path to simulate GitHub Pages
```

## Custom Domain Setup

### Using a Custom Domain

1. **Add domain to GitHub Pages:**
   - Repository Settings → Pages
   - Custom domain: `yourdomain.com`
   - Save

2. **Configure DNS with your domain provider:**

For apex domain (`yourdomain.com`):
```
Type: A
Name: @
Value: 185.199.108.153
       185.199.109.153
       185.199.110.153
       185.199.111.153
```

For subdomain (`www.yourdomain.com` or `blog.yourdomain.com`):
```
Type: CNAME
Name: www (or blog)
Value: yourusername.github.io
```

3. **Update base path:**

Edit `src/main.py` or pass `/` as base path:
```bash
python src/main.py /
```

4. **Enable HTTPS:**
   - GitHub Pages → Enforce HTTPS (checkbox)
   - Wait a few minutes for certificate

## Alternative Platforms

### Netlify

1. **Install Netlify CLI:**
```bash
npm install -g netlify-cli
```

2. **Build site:**
```bash
python src/main.py /
```

3. **Deploy:**
```bash
netlify deploy --dir=public --prod
```

**Or via GitHub integration:**
- Connect repository to Netlify
- Build command: `uv run python src/main.py /`
- Publish directory: `public`

### Vercel

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Create `vercel.json`:**
```json
{
  "buildCommand": "uv run python src/main.py /",
  "outputDirectory": "public"
}
```

3. **Deploy:**
```bash
vercel --prod
```

### Cloudflare Pages

1. **Connect repository** to Cloudflare Pages
2. **Build settings:**
   - Build command: `uv run python src/main.py /`
   - Build output: `public`
3. **Deploy**

## Troubleshooting

### CSS/Images Not Loading

**Problem:** Assets return 404 errors.

**Solution:**
- Verify base path is correct
- Check that paths in markdown are relative (no leading `/`)
- Ensure static files copied to `public/`

Example:
```markdown
<!-- ❌ Wrong -->
![Image](/images/photo.png)

<!-- ✅ Correct -->
![Image](images/photo.png)
```

### Links Not Working

**Problem:** Links to other pages don't work.

**Solution:**
- Use relative paths in markdown
- Don't use absolute paths starting with `/`

```markdown
<!-- ❌ Wrong -->
[Contact](/contact)

<!-- ✅ Correct -->
[Contact](contact)
```

### Workflow Failing

**Problem:** GitHub Actions workflow fails.

**Common causes:**

1. **Missing dependencies:**
   - Ensure `uv.lock` is committed
   - Check `pyproject.toml` is valid

2. **Syntax errors in code:**
   - Run tests locally: `./test.sh`
   - Check Python syntax

3. **Permissions:**
   - Settings → Actions → General
   - Workflow permissions: "Read and write permissions"
   - Allow GitHub Actions to create and approve pull requests

**Debug steps:**
```bash
# Test workflow locally
uv run python src/main.py /test-path/

# Check for errors
./test.sh
```

### Build Produces Wrong Base Path

**Problem:** URLs don't include repository name.

**Solution:**

The workflow automatically gets the base path from GitHub Pages. If you need to override:

1. Check `.github/workflows/deploy.yml`
2. Verify the `BASE_PATH` environment variable

For local testing with the same path:
```bash
./build.sh  # Uses /static-site-generator/
```

### Page Shows Old Content

**Problem:** Deployment succeeded but shows old content.

**Solutions:**

1. **Clear browser cache:**
   - Hard refresh: Cmd+Shift+R (Mac) or Ctrl+F5 (Windows)

2. **Check deployment:**
   - Actions tab → Verify workflow completed
   - Pages settings → See deployment history

3. **Wait a few minutes:**
   - GitHub Pages caching can delay updates

### Deployment URL 404

**Problem:** GitHub Pages URL returns 404.

**Checklist:**
- [ ] Settings → Pages shows green success message
- [ ] Deployment completed in Actions tab
- [ ] `public/index.html` exists
- [ ] Using correct URL format: `username.github.io/repo-name`

## Base Path Explanation

GitHub Pages serves repositories at a subdirectory:
- User site: `username.github.io` → base path `/`
- Project site: `username.github.io/repo-name` → base path `/repo-name/`

The `<base href="/repo-name/">` tag in `template.html` ensures all relative URLs resolve correctly.

**How it works:**

```html
<!-- template.html -->
<base href="/static-site-generator/" />
<link href="index.css" rel="stylesheet" />
```

The browser resolves `index.css` relative to the base:
- Result: `/static-site-generator/index.css` ✅

Without the base tag:
- Result: `/index.css` ❌ (wrong path)

## Environment-Specific Builds

### Production (GitHub Pages)
```bash
./build.sh  # Base path: /static-site-generator/
```

### Development (Local)
```bash
./main.sh  # Base path: /
```

### Custom
```bash
uv run python src/main.py /custom-path/
```

## Monitoring Deployments

### GitHub Actions Dashboard

- **Actions** tab shows all workflow runs
- Click on a run to see detailed logs
- Green checkmark = success
- Red X = failure

### Deployment Environments

- **Settings** → **Environments**
- View deployment history
- See active deployments
- Track by environment (`github-pages`, `github-pages-dev`)

## Best Practices

1. ✅ **Always test locally** before pushing
2. ✅ **Use relative paths** in markdown content
3. ✅ **Commit `uv.lock`** for reproducible builds
4. ✅ **Check Actions logs** if deployment fails
5. ✅ **Use workflow_dispatch** for manual testing
6. ✅ **Keep `main` branch stable** - test in dev branches

## Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Custom Domain Setup](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [uv Documentation](https://docs.astral.sh/uv/)
