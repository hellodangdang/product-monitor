# SMS Notification Setup Guide

The script can send you **10 text messages** when the product becomes available! Here's how to set it up:

## Step 1: Get a Twilio Account

1. Go to [https://www.twilio.com](https://www.twilio.com)
2. Sign up for a free account (you get $15.50 free credit)
3. Verify your phone number

## Step 2: Get Your Twilio Credentials

1. After signing up, go to your Twilio Console Dashboard
2. You'll see your **Account SID** and **Auth Token**
3. Copy these values

## Step 3: Get a Twilio Phone Number

1. In Twilio Console, go to **Phone Numbers** → **Manage** → **Buy a number**
2. Choose a number (you can get a free trial number)
3. Copy the phone number (format: +1234567890)

## Step 4: Update Your Config

Edit `config.json` and fill in the SMS notification section:

```json
"sms_notifications": {
  "enabled": true,
  "twilio_account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "twilio_auth_token": "your_auth_token_here",
  "twilio_from_number": "+1234567890",
  "to_number": "+12032982465",
  "message_count": 10
}
```

**Important:**
- `twilio_from_number`: Your Twilio phone number (format: +1234567890)
- `to_number`: Your phone number to receive notifications (format: +1234567890)
- `message_count`: Number of messages to send (default: 10)

## Step 5: Install Twilio

```bash
pip3 install twilio
```

## Step 6: Test It

Run the script and when the product becomes available, you'll receive 10 text messages!

## Cost

- Twilio free trial: $15.50 credit
- SMS cost: ~$0.0075 per message (very cheap!)
- 10 messages = ~$0.075 (less than 10 cents)

## Troubleshooting

**"Twilio not installed" error:**
```bash
pip3 install twilio
```

**"Failed to send SMS" error:**
- Check that your Twilio account is verified
- Verify the phone numbers are in correct format (+1234567890)
- Make sure you have credits in your Twilio account

**Phone number format:**
- Must include country code
- US numbers: +1XXXXXXXXXX
- Example: +12032982465 (not 2032982465)

