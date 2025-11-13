#!/usr/bin/env python3
"""
Test script to send a test SMS notification.
"""

import json
import sys

try:
    from twilio.rest import Client
except ImportError:
    print("❌ Twilio not installed. Run: pip3 install twilio")
    sys.exit(1)

def test_sms():
    """Send a test SMS message."""
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found!")
        return False
    
    sms_config = config.get('sms_notifications', {})
    account_sid = sms_config.get('twilio_account_sid')
    auth_token = sms_config.get('twilio_auth_token')
    from_number = sms_config.get('twilio_from_number')
    to_number = sms_config.get('to_number')
    
    # Check if configured
    if not account_sid or not auth_token or not from_number or not to_number:
        print("❌ SMS notifications not fully configured!")
        print("\nPlease fill in these fields in config.json:")
        print(f"  - twilio_account_sid: {'✅' if account_sid else '❌ MISSING'}")
        print(f"  - twilio_auth_token: {'✅' if auth_token else '❌ MISSING'}")
        print(f"  - twilio_from_number: {'✅' if from_number else '❌ MISSING'}")
        print(f"  - to_number: {'✅' if to_number else '❌ MISSING'}")
        return False
    
    print("=" * 60)
    print("Testing SMS Notification")
    print("=" * 60)
    print(f"From: {from_number}")
    print(f"To: {to_number}")
    print("=" * 60)
    
    try:
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Send test message
        message = client.messages.create(
            body="🧪 TEST: Product Monitor SMS notifications are working! 🎉",
            from_=from_number,
            to=to_number
        )
        
        print(f"✅ Test SMS sent successfully!")
        print(f"Message SID: {message.sid}")
        print(f"\n📱 Check your phone ({to_number}) for the test message!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")
        print("\nCommon issues:")
        print("  - Check that your Twilio account has credits")
        print("  - Verify phone numbers are in correct format (+1234567890)")
        print("  - Make sure your Twilio account is verified")
        return False

if __name__ == '__main__':
    success = test_sms()
    sys.exit(0 if success else 1)

