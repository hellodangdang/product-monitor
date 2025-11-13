# Discord Notification Setup (EASIEST!)

Discord webhooks are **much easier** than SMS - just 2 steps!

## Step 1: Create a Discord Webhook

1. Open Discord (app or web)
2. Go to your server (or create a new one)
3. Go to **Server Settings** → **Integrations** → **Webhooks**
4. Click **New Webhook**
5. Give it a name (e.g., "Product Monitor")
6. Choose a channel where you want notifications
7. Click **Copy Webhook URL**

That's it! You now have a webhook URL that looks like:
```
https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz
```

## Step 2: Add to Config

Edit `config.json` and paste your webhook URL:

```json
"discord_notifications": {
  "enabled": true,
  "webhook_url": "https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz",
  "message_count": 10
}
```

## Done! 🎉

That's it! No account setup, no phone numbers, completely free.

When the product becomes available, you'll get **10 Discord messages** in your channel!

## Advantages over SMS:

✅ **Free** - No cost at all  
✅ **Instant** - Messages appear immediately  
✅ **Easy setup** - Just copy/paste a URL  
✅ **No phone needed** - Works on any device with Discord  
✅ **Persistent** - Messages stay in your Discord channel  
✅ **Can @mention** - You can set up @mentions for urgent alerts

## Test It

You can test your webhook by running:
```bash
python3 -c "import requests; requests.post('YOUR_WEBHOOK_URL', json={'content': 'Test message!'})"
```

Replace `YOUR_WEBHOOK_URL` with your actual webhook URL.

