# Product Monitor & Auto-Purchase Bot

Automatically monitors a product page and purchases it when it becomes available. Built specifically for The Row's Sally Bag, but can be adapted for any Shopify-based e-commerce site.

## Features

- 🔍 **Continuous Monitoring**: Checks product availability at configurable intervals
- 🛒 **Auto Add to Cart**: Automatically adds product to cart when available
- 📝 **Auto-Fill Forms**: Pre-fills shipping information to speed up checkout
- 🔔 **Logging**: Comprehensive logging of all actions and status changes
- ⚙️ **Configurable**: Easy-to-edit JSON configuration file

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Chrome browser** installed (for Selenium WebDriver)
3. **ChromeDriver** - will be managed automatically via webdriver-manager

## Setup

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create your configuration file**:
   ```bash
   cp config.json.example config.json
   ```

4. **Edit `config.json`** with your information:
   - Add your shipping address details
   - Set your email address
   - Adjust check interval (in seconds) - default is 60 seconds
   - Set `headless: true` if you want to run without showing the browser window
   - Set `exit_after_purchase: true` if you want the script to stop after a successful purchase

## Usage

### Basic Usage

Run the monitor:
```bash
python product_monitor.py
```

Or specify a custom config file:
```bash
python product_monitor.py my_config.json
```

### Running in Background

**On macOS/Linux:**
```bash
nohup python product_monitor.py > output.log 2>&1 &
```

**On Windows (PowerShell):**
```powershell
Start-Process python -ArgumentList "product_monitor.py" -WindowStyle Hidden
```

## How It Works

1. **Monitoring**: The script checks the product page every N seconds (configurable)
2. **Detection**: It looks for "Sold Out" indicators and "Add to Cart" buttons
3. **Purchase Flow**: When available:
   - Adds product to cart
   - Navigates to checkout
   - Fills shipping information
   - **Stops for manual payment review** (for security)

## Security Note

⚠️ **IMPORTANT**: For security reasons, the script does NOT automatically fill payment information. When a product becomes available and the purchase flow starts, you should:

1. Review the checkout page
2. Manually enter your payment information
3. Complete the purchase

If you want full automation (not recommended), you can uncomment and modify the payment section in `product_monitor.py`, but be aware of the security risks of storing payment information in plain text.

## Configuration Options

- `product_url`: The URL of the product to monitor
- `check_interval`: How often to check (in seconds). Lower = faster detection but more requests
- `headless`: Run browser in background (`true`) or visible (`false`)
- `exit_after_purchase`: Stop monitoring after successful purchase (`true`) or continue (`false`)
- `shipping_info`: Your shipping address details
- `payment_info`: Payment details (currently not used for security)

## Troubleshooting

### ChromeDriver Issues

If you encounter ChromeDriver errors, try:
```bash
pip install --upgrade selenium webdriver-manager
```

### Product Not Detected as Available

- The script looks for specific text patterns. If the website changes its wording, you may need to update the detection logic in `product_monitor.py`
- Try running with `headless: false` to see what the script is seeing

### Rate Limiting

If you check too frequently, the website might block you. Increase `check_interval` to 120-300 seconds.

## Logs

All activity is logged to:
- Console output
- `monitor.log` file

## Legal & Ethical Considerations

- Use responsibly and in accordance with the website's Terms of Service
- Be respectful with check intervals (don't spam the server)
- This tool is for personal use only
- Some retailers may prohibit automated purchasing

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions, check the logs in `monitor.log` for detailed error messages.

