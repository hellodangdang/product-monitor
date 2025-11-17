# Product Monitor - GitHub Actions

Automatically monitors a product page and sends Discord notifications when it becomes available. Runs 24/7 for FREE on GitHub Actions.

## Features

- 🔍 **24/7 Monitoring**: Checks product availability every 5 minutes automatically
- 📢 **Discord Notifications**: Sends multiple Discord messages when product becomes available
- 🆓 **FREE**: Uses GitHub Actions (unlimited for public repos, 2000 min/month for private)
- ⚙️ **Easy Setup**: Just configure GitHub Secrets and push code
- 🔔 **No Maintenance**: Runs automatically in the cloud

## How It Works

1. **Schedule**: GitHub Actions runs the monitor every 5 minutes
2. **Check**: Makes HTTP request to product page
3. **Detect**: Looks for "sold out" vs "add to cart" text patterns
4. **Notify**: Sends Discord messages if product is available
5. **Alert**: Workflow shows as "failed" when product is available (makes it more visible!)

## Setup

### 1. Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/product-monitor.git
git push -u origin main
```

### 2. Configure GitHub Secrets

1. Go to your repo on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

   **PRODUCT_URL (REQUIRED):**
   - Value: `https://www.therow.com/products/sally-black` (or your product URL)
   - ⚠️ **Required** - Monitor will fail if not set

   **DISCORD_WEBHOOK (REQUIRED):**
   - Value: Your Discord webhook URL (see `DISCORD_SETUP.md`)
   - ⚠️ **Required** - Monitor will fail if not set

   **MESSAGE_COUNT (optional):**
   - Value: `10` (number of messages to send, default: 10)

### 3. Enable GitHub Actions

1. Go to **Actions** tab in your repo
2. Click "I understand my workflows, go ahead and enable them"
3. The workflow will start running automatically!

## Viewing Results

1. Go to **Actions** tab in your GitHub repo
2. Click on latest workflow run
3. See logs in real-time
4. If product is available, workflow will "fail" (intentional - makes it more visible!)

## Manual Trigger

You can trigger manually:
1. Go to **Actions** tab
2. Click "Product Monitor" workflow
3. Click "Run workflow" button

## Configuration

The monitor uses GitHub Secrets for configuration:

- `PRODUCT_URL`: The product page URL to monitor
- `DISCORD_WEBHOOK`: Your Discord webhook URL
- `MESSAGE_COUNT`: Number of Discord messages to send (default: 10)

## Limitations

- **Minimum interval:** 5 minutes (GitHub Actions limitation)
- **HTTP-based:** Uses HTTP requests instead of browser automation (simpler, faster)
- **Detection:** Looks for text patterns - may need updates if website changes

## Troubleshooting

### Discord Notifications Not Working

- Verify your Discord webhook URL is correct
- Check that the webhook is still active in your Discord server
- Check GitHub Actions logs for error messages

### Product Not Detected as Available

- The script looks for specific text patterns ("sold out", "add to cart", etc.)
- If the website changes its wording, you may need to update `monitor_github_actions.py`

### Rate Limiting

- GitHub Actions runs every 5 minutes, which is respectful to the website
- If you need faster checks, consider running locally (not included in this repo)

## Cost

- **Public repos:** FREE (unlimited minutes)
- **Private repos:** FREE (2000 minutes/month = ~33 hours)
  - Monitor runs ~5 minutes/day = ~150 minutes/month
  - Well within free tier!

## Documentation

- `GITHUB_ACTIONS_SETUP.md` - Detailed setup instructions
- `DISCORD_SETUP.md` - How to create a Discord webhook

## Legal & Ethical Considerations

- Use responsibly and in accordance with the website's Terms of Service
- Be respectful with check intervals
- This tool is for personal use only

## License

This project is provided as-is for educational and personal use.
