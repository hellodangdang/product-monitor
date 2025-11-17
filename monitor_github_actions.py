#!/usr/bin/env python3
"""
Simple product monitor for GitHub Actions.
Uses HTTP requests instead of browser automation.
"""

import os
import requests
import time
from datetime import datetime, timedelta

# Get configuration from environment variables (GitHub Secrets)
PRODUCT_URL = os.getenv('PRODUCT_URL', '')
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK', '')
MESSAGE_COUNT = int(os.getenv('MESSAGE_COUNT', '10'))
NOTIFICATION_COOLDOWN_MINUTES = int(os.getenv('NOTIFICATION_COOLDOWN_MINUTES', '15'))  # Default: 15 minutes of active notifications, then cooldown

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
        # IMPORTANT: If "add to shopping bag" exists and is not disabled, it's AVAILABLE
        # even if "sold out" appears elsewhere on the page (might be for other products)
        if 'add to shopping bag' in page_content:
            # Find ALL positions of "add to shopping bag" (might appear multiple times)
            bag_positions = []
            start = 0
            while True:
                pos = page_content.find('add to shopping bag', start)
                if pos == -1:
                    break
                bag_positions.append(pos)
                start = pos + 1
            
            # Check each occurrence
            for bag_pos in bag_positions:
                # Check if this specific button is disabled
                # Look for "disabled" in a reasonable window after the button text
                disabled_pos = page_content.find('disabled', bag_pos)
                
                # Check the immediate context around this button
                context_start = max(0, bag_pos - 150)
                context_end = min(len(page_content), bag_pos + 300)
                context = page_content[context_start:context_end]
                
                # Check if this specific button is disabled
                # Look for patterns like "disabled" or "sold out" very close to the button
                button_disabled = (
                    'disabled' in context and 
                    context.find('disabled') < (bag_pos - context_start + 100)
                )
                
                # Check if "sold out" is in the immediate button context (not just anywhere on page)
                sold_out_in_context = any(
                    so in context and 
                    abs(context.find(so) - (bag_pos - context_start)) < 100
                    for so in ['sold out', 'out of stock']
                )
                
                # If button is not disabled and not in a sold out context, it's AVAILABLE
                if not button_disabled and not sold_out_in_context:
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
    print("=" * 60)
    print("DISCORD NOTIFICATION DEBUG:")
    print(f"  Webhook URL provided: {'Yes' if webhook_url else 'No'}")
    print(f"  Webhook URL length: {len(webhook_url) if webhook_url else 0}")
    print(f"  Message count: {count}")
    print(f"  Message length: {len(message)}")
    print("=" * 60)
    
    if not webhook_url:
        print("❌ ERROR: Discord webhook not configured!")
        print("   DISCORD_WEBHOOK secret is missing or empty")
        return
    
    print(f"Sending {count} Discord notifications...")
    
    success_count = 0
    for i in range(count):
        try:
            payload = {
                "content": message,
                "username": "Product Monitor Bot"
            }
            print(f"  Attempting to send notification {i+1}/{count}...")
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            print(f"  Response status: {response.status_code}")
            if response.status_code == 204:
                print(f"✅ Discord notification {i+1}/{count} sent successfully")
                success_count += 1
            else:
                print(f"⚠️  Discord notification {i+1}/{count} - Status: {response.status_code}")
                print(f"   Response text: {response.text[:200]}")
            if i < count - 1:
                time.sleep(0.5)
        except Exception as e:
            print(f"❌ Failed to send Discord notification {i+1}/{count}: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
    
    print("=" * 60)
    print(f"SUMMARY: {success_count}/{count} notifications sent successfully")
    print("=" * 60)

def should_send_notification():
    """Check if we should send notification based on cooldown period.
    
    Logic: Send notifications for first 15 minutes, then cooldown.
    This means: if first notification was less than 15 minutes ago, keep sending.
    After 15 minutes, enter cooldown period.
    """
    # Read first notification time from cache file (when we first detected availability)
    cache_file = '.last_notification'
    
    if not os.path.exists(cache_file):
        # Never sent before, so send it (this is the first detection)
        print("📝 Cache file not found - this is the first detection")
        return True, None
    
    try:
        with open(cache_file, 'r') as f:
            first_notification_str = f.read().strip()
        
        if not first_notification_str:
            print("📝 Cache file is empty - this is the first detection")
            return True, None
        
        first_notification = datetime.fromisoformat(first_notification_str)
        time_since_first = datetime.now() - first_notification
        
        print(f"📝 Cache file found - first notification was {time_since_first.total_seconds() / 60:.1f} minutes ago")
        
        # If less than 15 minutes since first notification, keep sending
        if time_since_first < timedelta(minutes=NOTIFICATION_COOLDOWN_MINUTES):
            # Still in active notification period (first 15 minutes)
            minutes_remaining = (timedelta(minutes=NOTIFICATION_COOLDOWN_MINUTES) - time_since_first).total_seconds() / 60
            print(f"✅ Still in active period - {minutes_remaining:.1f} minutes remaining")
            return True, first_notification
        else:
            # Cooldown period active (more than 15 minutes since first notification)
            minutes_elapsed = time_since_first.total_seconds() / 60
            print(f"⏸️  Cooldown active - {minutes_elapsed:.1f} minutes since first notification")
            return False, first_notification
    except Exception as e:
        # If we can't parse the time, send notification to be safe
        print(f"⚠️  Warning: Could not read last notification time: {e}")
        return True, None

def save_notification_time():
    """Save current time as first notification time to cache file.
    Only saves if file doesn't exist (first detection).
    """
    cache_file = '.last_notification'
    try:
        # Only save if file doesn't exist (first time detecting availability)
        if not os.path.exists(cache_file):
            with open(cache_file, 'w') as f:
                f.write(datetime.now().isoformat())
            print(f"✅ Saved notification time to cache file: {datetime.now().isoformat()}")
        else:
            print(f"ℹ️  Cache file already exists, not overwriting")
    except Exception as e:
        print(f"⚠️  Warning: Could not save notification time: {e}")
        print(f"   This is okay - cache save may fail if multiple runs happen simultaneously")

def clear_notification_time():
    """Clear notification time when product goes sold out."""
    cache_file = '.last_notification'
    try:
        if os.path.exists(cache_file):
            os.remove(cache_file)
    except Exception as e:
        print(f"Warning: Could not clear notification time: {e}")

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
    print(f"Message count: {MESSAGE_COUNT} (from MESSAGE_COUNT secret)")
    print(f"Active notification period: {NOTIFICATION_COOLDOWN_MINUTES} minutes")
    print("=" * 60)
    
    # Check availability
    print("Checking product availability...")
    is_available = check_availability(PRODUCT_URL)
    
    if is_available:
        print("✅ PRODUCT IS AVAILABLE!")
        print("=" * 60)
        
        # Check if we should send notification (cooldown check)
        should_send, first_notification = should_send_notification()
        
        if not should_send and first_notification:
            minutes_elapsed = (datetime.now() - first_notification).total_seconds() / 60
            print(f"⏸️  Notification cooldown active")
            print(f"   First notification: {minutes_elapsed:.1f} minutes ago")
            print(f"   Active period ended ({NOTIFICATION_COOLDOWN_MINUTES} minutes)")
            print("   (Product is available, but cooldown period active)")
            exit(0)  # Exit successfully - product available but cooldown active
        
        # Send notifications
        product_name = PRODUCT_URL.split('/products/')[-1].replace('-', ' ').title()
        notification_message = (
            f"🚨 ALERT: {product_name} is NOW AVAILABLE!\n\n"
            f"🔗 {PRODUCT_URL}\n\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        send_discord_notification(DISCORD_WEBHOOK, notification_message, MESSAGE_COUNT)
        
        # Save notification time to cache (only on first notification)
        # This tracks when we first detected availability
        if first_notification is None:
            # This is the first time detecting availability
            save_notification_time()
            print("=" * 60)
            print("✅ Notifications sent! (First detection)")
            print(f"   Will continue sending notifications for next {NOTIFICATION_COOLDOWN_MINUTES} minutes")
            print(f"   Cache file saved for next run")
        else:
            # Still in active period
            minutes_elapsed = (datetime.now() - first_notification).total_seconds() / 60
            minutes_remaining = NOTIFICATION_COOLDOWN_MINUTES - minutes_elapsed
            print("=" * 60)
            print("✅ Notifications sent!")
            print(f"   Active period: {minutes_elapsed:.1f} minutes elapsed, {minutes_remaining:.1f} minutes remaining")
            print(f"   Cache file exists, will continue checking")
        
        # Exit with error code to make GitHub Actions show as failed (so you notice)
        exit(1)  # This makes the workflow show as "failed" so it's more visible
    else:
        print("❌ Product is SOLD OUT")
        # Clear notification time when product goes sold out
        # This allows fresh notifications when it becomes available again
        clear_notification_time()
        print("Will check again in 2 minutes...")
        exit(0)

if __name__ == '__main__':
    main()

