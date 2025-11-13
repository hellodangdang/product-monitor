# Running Monitor with MacBook Lid Closed (Clamshell Mode)

## Quick Answer:

**It depends on your setup:**

### ✅ Will Work If:
- MacBook is **plugged in** (AC power)
- You have an **external display** connected (or use headless mode)
- OR you configure it to not sleep when lid is closed

### ❌ Won't Work If:
- MacBook is **not plugged in** (will sleep)
- No external display AND not configured for clamshell mode

## Setup for Clamshell Mode:

### Option 1: Use External Display (Easiest)
1. Plug in your MacBook
2. Connect external monitor/keyboard/mouse
3. Close the lid
4. MacBook will stay awake and monitor will keep running

### Option 2: Configure to Stay Awake When Closed (No External Display Needed)
```bash
# Prevent sleep when lid is closed (while plugged in)
sudo pmset -a disablesleep 1

# To revert later:
sudo pmset -a disablesleep 0
```

**Warning:** This keeps your MacBook fully awake even when lid is closed. Make sure it's plugged in and well-ventilated.

### Option 3: Use Headless Mode (Already Set)
Your config already has `headless: true`, so no display is needed. But macOS will still sleep when lid closes unless configured.

## Current Status Check:

Run this to check your settings:
```bash
pmset -g | grep -E "(sleep|displaysleep)"
```

## Recommended Setup:

1. **Plug in your MacBook** (required)
2. **Set headless mode** (already done: `headless: true`)
3. **Configure to not sleep when lid closed:**
   ```bash
   sudo pmset -a disablesleep 1
   ```
4. **Close the lid** - monitor will keep running

## To Test:

1. Make sure monitor is running: `ps aux | grep product_monitor`
2. Close the lid
3. Wait 1-2 minutes
4. Open lid and check: `tail -20 monitor_output.log`

If you see new log entries from while the lid was closed, it's working!

## Revert Settings:

If you want to go back to normal sleep behavior:
```bash
sudo pmset -a disablesleep 0
```

## Important Notes:

- **Ventilation**: Make sure MacBook has good airflow when lid is closed
- **Heat**: Monitor generates some heat - keep it well-ventilated
- **Battery**: Keep it plugged in to avoid battery drain
- **Sleep**: The `disablesleep` setting prevents ALL sleep, not just when lid is closed

