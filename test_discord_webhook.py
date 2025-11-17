#!/usr/bin/env python3
"""
Quick test script to verify Discord webhook is working.
Run this locally to test your webhook before debugging GitHub Actions.
"""

import requests
import os

# Get webhook from environment or paste it here
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK', 'YOUR_WEBHOOK_URL_HERE')

def test_webhook(webhook_url):
    """Test Discord webhook."""
    if not webhook_url or webhook_url == 'YOUR_WEBHOOK_URL_HERE':
        print("❌ Please set DISCORD_WEBHOOK environment variable or edit this script")
        return False
    
    try:
        payload = {
            "content": "🧪 TEST: Discord webhook is working! ✅",
            "username": "Product Monitor Bot"
        }
        response = requests.post(webhook_url, json=payload, timeout=5)
        
        if response.status_code == 204:
            print("✅ Discord webhook is working!")
            print("   Check your Discord channel for the test message.")
            return True
        else:
            print(f"❌ Discord webhook failed!")
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

if __name__ == '__main__':
    print("Testing Discord webhook...")
    print("=" * 60)
    test_webhook(WEBHOOK_URL)

