#!/usr/bin/env python3
"""
Simple product monitor for GitHub Actions.
Uses HTTP requests instead of browser automation.
"""

import os
import requests
import time
from datetime import datetime

# Get configuration from environment variables (GitHub Secrets)
PRODUCT_URL = os.getenv('PRODUCT_URL', '')
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK', '')
MESSAGE_COUNT = int(os.getenv('MESSAGE_COUNT', '10'))

def check_availability(url):
    """Check if product is available using HTTP request."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        page_content = response.text.lower()
        
        # Check for sold out indicators
        sold_out_indicators = [
            'sold out',
            'join the waitlist',
            'out of stock',
            'unavailable'
        ]
        
        # Check for available indicators (more flexible patterns)
        available_indicators = [
            'add to shopping bag',
            'add to cart',
            'add to bag',  # Common variation
            'buy now',
            'purchase',  # Alternative wording
            'add to',  # More flexible
        ]
        
        # PRIORITY: Check for "add to shopping bag" FIRST (most specific and common for The Row)
        # This is the primary indicator for availability on The Row
        if 'add to shopping bag' in page_content:
            # Find the position of "add to shopping bag"
            bag_pos = page_content.find('add to shopping bag')
            # Check if it's disabled - look for "disabled" near the button
            disabled_pos = page_content.find('disabled', bag_pos)
            # If "disabled" appears very close after "add to shopping bag", it might be disabled
            # But if there's distance or no "disabled", it's available
            if disabled_pos == -1 or disabled_pos > bag_pos + 100:  # Allow reasonable distance
                # Double-check: make sure it's not in a "sold out" context
                context_start = max(0, bag_pos - 200)
                context_end = min(len(page_content), bag_pos + 200)
                context = page_content[context_start:context_end]
                # If context doesn't strongly indicate sold out, it's available
                strong_sold_out = any(so in context for so in ['sold out', 'out of stock'])
                if not strong_sold_out:
                    return True
        
        # Look for other available indicators (prioritize more specific ones first)
        specific_patterns = ['add to cart', 'add to bag', 'buy now']
        for indicator in specific_patterns:
            if indicator in page_content:
                indicator_pos = page_content.find(indicator)
                disabled_pos = page_content.find('disabled', indicator_pos)
                if disabled_pos == -1 or disabled_pos > indicator_pos + 50:
                    return True
        
        # Only check for sold out if we haven't found available indicators
        # (Some pages might mention "sold out" in descriptions but still have add buttons)
        for indicator in sold_out_indicators:
            if indicator in page_content:
                # Make sure it's a strong sold out signal (not just mentioned in text)
                # Check if it's near button-related text
                sold_out_pos = page_content.find(indicator)
                button_nearby = any(btn in page_content[max(0, sold_out_pos-50):sold_out_pos+50] 
                                   for btn in ['button', 'btn', 'add to'])
                if button_nearby:
                    return False
        
        # Check for more general patterns
        general_patterns = ['purchase', 'add to']
        for indicator in general_patterns:
            if indicator in page_content:
                # Make sure it's not in a "sold out" context
                context_start = max(0, page_content.find(indicator) - 100)
                context_end = min(len(page_content), page_content.find(indicator) + 100)
                context = page_content[context_start:context_end]
                # If context doesn't contain sold out indicators, it's likely available
                if not any(so_ind in context for so_ind in sold_out_indicators):
                    return True
        
        # If we can't find clear indicators, assume sold out for safety
        return False
        
    except Exception as e:
        print(f"Error checking availability: {e}")
        return False

def send_discord_notification(webhook_url, message, count=10):
    """Send Discord notifications."""
    if not webhook_url:
        print("Discord webhook not configured")
        return
    
    print(f"Sending {count} Discord notifications...")
    
    for i in range(count):
        try:
            payload = {
                "content": message,
                "username": "Product Monitor Bot"
            }
            response = requests.post(webhook_url, json=payload, timeout=5)
            if response.status_code == 204:
                print(f"✅ Discord notification {i+1}/{count} sent")
            else:
                print(f"⚠️  Discord notification {i+1}/{count} - Status: {response.status_code}")
            if i < count - 1:
                time.sleep(0.5)
        except Exception as e:
            print(f"❌ Failed to send Discord notification {i+1}/{count}: {e}")

def main():
    """Main monitoring function."""
    # Validate required secrets
    if not PRODUCT_URL:
        print("❌ ERROR: PRODUCT_URL secret is not set!")
        print("Please add PRODUCT_URL to your GitHub Secrets.")
        exit(1)
    
    if not DISCORD_WEBHOOK:
        print("❌ ERROR: DISCORD_WEBHOOK secret is not set!")
        print("Please add DISCORD_WEBHOOK to your GitHub Secrets.")
        exit(1)
    
    print("=" * 60)
    print("GitHub Actions Product Monitor")
    print("=" * 60)
    print(f"Product URL: [CONFIGURED]")  # Don't expose URL in logs
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check availability
    print("Checking product availability...")
    is_available = check_availability(PRODUCT_URL)
    
    if is_available:
        print("✅ PRODUCT IS AVAILABLE!")
        print("=" * 60)
        
        # Send notifications
        product_name = PRODUCT_URL.split('/products/')[-1].replace('-', ' ').title()
        notification_message = (
            f"🚨 ALERT: {product_name} is NOW AVAILABLE!\n\n"
            f"🔗 {PRODUCT_URL}\n\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        send_discord_notification(DISCORD_WEBHOOK, notification_message, MESSAGE_COUNT)
        
        print("=" * 60)
        print("✅ Notifications sent!")
        
        # Exit with error code to make GitHub Actions show as failed (so you notice)
        exit(1)  # This makes the workflow show as "failed" so it's more visible
    else:
        print("❌ Product is SOLD OUT")
        print("Will check again in 5 minutes...")
        exit(0)

if __name__ == '__main__':
    main()

