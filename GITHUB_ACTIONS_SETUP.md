# GitHub Actions Setup (FREE 24/7 Monitoring!)

## Why GitHub Actions?

✅ **FREE** - 2000 minutes/month for private repos (unlimited for public)  
✅ **True 24/7** - Runs automatically on schedule  
✅ **No server needed** - Runs in GitHub's cloud  
✅ **No maintenance** - GitHub handles everything  
✅ **Easy setup** - Just push code and configure secrets  

## Cost:

- **Public repos:** FREE (unlimited minutes) ⭐ **Recommended for frequent checks**
- **Private repos:** FREE (2000 minutes/month = ~33 hours)
  - Every 5 minutes: ~150 minutes/month ✅ Well within free tier
  - Every 2 minutes: ~10,800 minutes/month ❌ Exceeds by ~8,800 min (~$70/month)
  - Minimum for free tier: ~11 minutes between checks

## Limitations:

- **Recommended minimum interval:** 5 minutes (GitHub's recommendation)
- **Technical minimum:** 1 minute (cron supports it, but not recommended)
- **Free tier limit (private repos):** ~11 minutes minimum to stay within 2000 min/month
- **No browser automation:** Uses HTTP requests instead (simpler, faster)
- **Public repos:** Code is visible (but secrets are hidden) - but unlimited free minutes!

## Setup Steps:

### 1. Create GitHub Repository

```bash
# Initialize git repo (if not already)
cd /path/to/your/crawler
git init
git add .
git commit -m "Initial commit"
```

### 2. Create GitHub Repo

1. Go to github.com
2. Click "New repository"
3. Name it (e.g., "product-monitor")
4. Choose **Public** (for unlimited free minutes) or **Private** (2000 min/month is enough)
5. Don't initialize with README
6. Click "Create repository"

### 3. Push Code

```bash
# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/product-monitor.git

# Push code
git branch -M main
git push -u origin main
```

### 4. Configure GitHub Secrets

1. Go to your repo on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

   **Secret 1 (REQUIRED):**
   - Name: `PRODUCT_URL`
   - Value: `https://www.therow.com/products/sally-black` (or your product URL)
   - ⚠️ **Required** - Monitor will fail if not set

   **Secret 2 (REQUIRED):**
   - Name: `DISCORD_WEBHOOK`
   - Value: `YOUR_DISCORD_WEBHOOK_URL_HERE` (get this from your Discord server settings)
   - ⚠️ **Required** - Monitor will fail if not set

   **Secret 3 (optional):**
   - Name: `MESSAGE_COUNT`
   - Value: `10` (default: 10 if not set)

### 5. Enable GitHub Actions

1. Go to **Actions** tab in your repo
2. Click "I understand my workflows, go ahead and enable them"
3. The workflow will start running automatically!

## How It Works:

1. **Schedule:** Runs every 2 minutes automatically (configurable in `.github/workflows/monitor.yml`)
2. **Check:** Makes HTTP request to product page
3. **Detect:** Looks for "sold out" vs "add to cart" text
4. **Notify:** Sends Discord messages if available
5. **Alert:** Workflow shows as "failed" when product is available (so you notice!)

## Viewing Results:

1. Go to **Actions** tab
2. Click on latest workflow run
3. See logs in real-time
4. If product is available, workflow will "fail" (this is intentional - makes it more visible!)

## Manual Trigger:

You can also trigger manually:
1. Go to **Actions** tab
2. Click "Product Monitor" workflow
3. Click "Run workflow" button

## Advantages Over Cloud Server:

✅ **FREE** (vs $6/month)  
✅ **No server maintenance**  
✅ **Automatic updates** (just push code)  
✅ **Built-in logging** (GitHub Actions logs)  
✅ **No SSH/terminal needed**  

## Disadvantages:

❌ **5 minute minimum** (vs 10 seconds on your MacBook)  
❌ **No browser automation** (uses HTTP requests - simpler but less accurate)  
❌ **Public repos expose code** (but secrets are safe)  

## Testing:

1. Push code to GitHub
2. Go to Actions tab
3. Wait for workflow to run (or trigger manually)
4. Check logs to see if it's working
5. Test with a product that's available to verify notifications

## Updating:

Just edit files and push:
```bash
git add .
git commit -m "Update monitor"
git push
```

GitHub Actions will automatically use the new code!

## Cost Comparison:

| Option | Cost | Check Interval |
|--------|------|----------------|
| **GitHub Actions (Public)** | **FREE** | 2 minutes (unlimited) |
| **GitHub Actions (Private, 5 min)** | **FREE** | 5 minutes |
| **GitHub Actions (Private, 2 min)** | **~$70/month** | 2 minutes |
| MacBook | $0 (electricity) | 10 seconds |
| Cloud Server | $6/month | 10 seconds |

## Recommendation:

**Use GitHub Actions (Public Repo) if:**
- You want FREE 24/7 monitoring with frequent checks (every 2 minutes)
- You're okay with code being public (secrets are still hidden)
- ⭐ **Best option for 2-minute intervals**

**Use GitHub Actions (Private Repo) if:**
- You want FREE 24/7 monitoring
- 5-11 minute checks are acceptable
- You need code to be private

**Use MacBook/Cloud if:**
- You need faster checks (10 seconds)
- You need browser automation
- You want more control

## Next Steps:

1. Create GitHub repo
2. Push code
3. Add secrets
4. Enable Actions
5. Done! It will run automatically every 2 minutes!

**Note:** The workflow is set to run every 2 minutes. For private repos, this exceeds the free tier. Consider:
- Using a **public repo** (unlimited free minutes)
- Changing to 11+ minutes in `.github/workflows/monitor.yml` (fits free tier)
- Or accepting the ~$70/month cost for 2-minute checks

Want help with any step? Let me know!

