#!/usr/bin/env python3
"""
Test script to send a test Discord notification.
"""

import json
import requests
import sys

def test_discord():
    """Send a test Discord message."""
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found!")
        return False
    
    discord_config = config.get('discord_notifications', {})
    webhook_url = discord_config.get('webhook_url')
    
    if not webhook_url:
        print("❌ Discord webhook URL not configured!")
        print("Please add your webhook URL to config.json")
        return False
    
    print("=" * 60)
    print("Testing Discord Notification")
    print("=" * 60)
    print(f"Webhook: {webhook_url[:50]}...")
    print("=" * 60)
    
    try:
        # Send test message
        payload = {
            "content": "🧪 TEST: Product Monitor Discord notifications are working! 🎉",
            "username": "Product Monitor Bot"
        }
        
        response = requests.post(webhook_url, json=payload, timeout=5)
        
        if response.status_code == 204:
            print("✅ Test Discord message sent successfully!")
            print("\n📢 Check your Discord channel for the test message!")
            return True
        else:
            print(f"❌ Failed to send Discord message. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Failed to send Discord message: {e}")
        return False

if __name__ == '__main__':
    success = test_discord()
    sys.exit(0 if success else 1)

