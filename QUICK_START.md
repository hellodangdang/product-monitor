# Quick Start Guide

## Step 1: Install Xcode Command Line Tools (if needed)

If you see errors about "No developer tools were found", run:
```bash
xcode-select --install
```
Follow the prompts to install. This is required for Python packages.

## Step 2: Install Python Dependencies

Once Xcode tools are installed, run:
```bash
pip3 install -r requirements.txt
```

Or if that doesn't work:
```bash
python3 -m pip install selenium webdriver-manager requests
```

## Step 3: Configure Your Information

Edit `config.json` and fill in your details:

**Required fields:**
- `email`: Your email address
- `first_name`: Your first name
- `last_name`: Your last name  
- `address1`: Your street address
- `city`: Your city
- `state`: Your state (e.g., "California", "New York")
- `zip`: Your ZIP code
- `phone`: Your phone number

**Optional settings:**
- `check_interval`: How often to check (seconds). Default: 60
- `headless`: Set to `true` to run browser in background, `false` to see it
- `exit_after_purchase`: Set to `true` to stop after buying, `false` to keep monitoring

## Step 4: Run the Monitor

```bash
python3 product_monitor.py
```

The script will:
- Open Chrome browser
- Check the product page every 60 seconds (or your configured interval)
- When available, add to cart and fill shipping info
- Stop for you to enter payment and complete purchase

## Troubleshooting

**"ChromeDriver" errors:**
- The script automatically downloads ChromeDriver, but if it fails, you may need to install it manually

**"Module not found" errors:**
- Make sure dependencies are installed: `pip3 install selenium webdriver-manager requests`

**Browser doesn't open:**
- Set `"headless": false` in config.json to see the browser

**Want to run in background:**
```bash
nohup python3 product_monitor.py > monitor_output.log 2>&1 &
```

## Current Status

✅ Chrome browser: Installed  
✅ Config file: Created (needs your info)  
⏳ Dependencies: Need to install (Step 2)  
⏳ Configuration: Needs your details (Step 3)

