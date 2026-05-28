# Instagram Reel Analytics Dashboard

## Deploy to Render.com (FREE) - 3 Steps

### Step 1: Create GitHub Repo

1. Go to https://github.com/new
2. Name: `ig-reel-dashboard`, Public, click **Create**
3. You'll see commands. Note the repo URL: `https://github.com/YOURNAME/ig-reel-dashboard.git`

### Step 2: Push Code

Open terminal in the `public-app` folder:

```bash
git init
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOURNAME/ig-reel-dashboard.git
git push -u origin main
```

When asked for password: Use a **GitHub Personal Access Token** (not your Google password). Create one at https://github.com/settings/tokens/new with `repo` scope.

### Step 3: Deploy to Render

1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Select your `ig-reel-dashboard` repo
4. Fill in:
   - **Name**: `ig-reel-dashboard`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free
5. Click **Advanced** → Add Environment Variable:
   - Key: `APIFY_TOKEN`
   - Value: `<YOUR_APIFY_TOKEN_HERE>` (get yours from Apify Console > Settings > API)
6. Click **Create Web Service**

Done! Your URL: `https://ig-reel-dashboard.onrender.com`

## Security

- **APIFY_TOKEN** is stored as a Render environment variable - never exposed in code
- Backend proxies all Apify API calls - users never see the token
- Frontend talks only to your backend - no direct external API calls

## Updating

Tell the AI assistant what to change, they'll edit files, you re-push:
```bash
git add -A && git commit -m "update" && git push
```
Render auto-redeploys.
