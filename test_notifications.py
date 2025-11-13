#!/usr/bin/env python3
"""
Test script to send notifications as if product became available.
"""

import json
import requests
import time

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Get product info
product_url = config.get('product_url', '')
product_name = product_url.split('/products/')[-1].replace('-', ' ').title() if '/products/' in product_url else 'Product'

# Create notification message
notification_message = f"🚨 ALERT: {product_name} is NOW AVAILABLE!\n\n🔗 {product_url}\n\n⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"

print("=" * 60)
print("Testing Notifications (Simulating Product Available)")
print("=" * 60)
print(f"Product: {product_name}")
print(f"URL: {product_url}")
print("=" * 60)

# Test Discord notifications
discord_config = config.get('discord_notifications', {})
webhook_url = discord_config.get('webhook_url')
message_count = discord_config.get('message_count', 10)

if webhook_url:
    print(f"\n📢 Sending {message_count} Discord notifications...")
    for i in range(message_count):
        try:
            payload = {
                "content": notification_message,
                "username": "Product Monitor Bot"
            }
            response = requests.post(webhook_url, json=payload, timeout=5)
            if response.status_code == 204:
                print(f"✅ Discord notification {i+1}/{message_count} sent")
            else:
                print(f"⚠️  Discord notification {i+1}/{message_count} - Status: {response.status_code}")
            if i < message_count - 1:
                time.sleep(0.5)
        except Exception as e:
            print(f"❌ Failed to send Discord notification {i+1}/{message_count}: {e}")
    print("\n✅ Discord test complete! Check your Discord channel.")
else:
    print("\n⚠️  Discord webhook not configured")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)

