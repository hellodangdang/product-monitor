# 24/7 Monitoring on MacBook - Requirements

## What You Need:

### ✅ Computer Must Be:
- **ON** (not sleeping/shut down)
- **LOGGED IN** (your user account must be logged in)
- **Plugged in** (recommended to prevent sleep)

### ✅ Computer Can Be:
- **LOCKED** (screen locked is fine - processes still run)
- **Screen closed** (if using external monitor, or just let it run)
- **Other apps running** (no problem)

### ❌ Computer Cannot Be:
- **Logged out** (processes will be killed)
- **Sleeping** (processes will pause)
- **Shut down**

## Setup for 24/7 Monitoring:

### Option 1: Prevent Sleep (Recommended)
```bash
# Prevent sleep while plugged in (best option)
caffeinate -d

# Or set in System Settings:
# System Settings → Battery → Options → Prevent automatic sleeping when display is off
```

### Option 2: Use Launch Agent (Auto-start on login)
The script will automatically start when you log in, even if computer was restarted.

### Option 3: Keep Screen On
- Just leave it plugged in and don't let it sleep
- You can lock the screen (Cmd+Ctrl+Q) - that's fine!

## Best Practice:

1. **Plug in your MacBook** (so it doesn't sleep)
2. **Lock the screen** (Cmd+Ctrl+Q) - this is fine, processes keep running
3. **Set "Prevent automatic sleeping"** in System Settings → Battery
4. **Run the monitor in headless mode** (already set in your config)
5. **Use the background script**: `./start_monitor.sh`

## Summary:

- ✅ **Locked screen** = OK (processes run)
- ✅ **Logged in** = Required (must be logged into your account)
- ❌ **Logged out** = Not OK (processes stop)
- ❌ **Sleeping** = Not OK (processes pause)

## To Start 24/7 Monitoring:

```bash
# 1. Make sure computer won't sleep
# System Settings → Battery → Prevent automatic sleeping

# 2. Start the monitor
./start_monitor.sh

# 3. Lock your screen (optional)
# Press Cmd+Ctrl+Q

# 4. Done! It will keep running even when locked
```

## Check if Running:

```bash
# Even when screen is locked, you can SSH in or check:
ps aux | grep product_monitor
```

## Alternative: Cloud Server

If you want true 24/7 without keeping your MacBook on:
- Use a cloud server (AWS, DigitalOcean, etc.)
- Costs ~$5-10/month
- Runs 24/7 without your computer

