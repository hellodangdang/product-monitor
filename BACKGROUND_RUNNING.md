# Running the Monitor in Background Continuously

## Current Setup Issues:
- ❌ Stops if you close terminal
- ❌ Stops if you close browser (unless headless)
- ❌ Stops if computer sleeps

## Solutions:

### Option 1: Run with nohup (Simple)
```bash
./run_background.sh
```
This will run in background and survive terminal close.

### Option 2: Use headless mode (No browser window)
Edit `config.json`:
```json
"headless": true
```
Then run:
```bash
nohup python3 product_monitor.py > monitor_output.log 2>&1 &
```

### Option 3: Use screen/tmux (Best for long-term)
```bash
# Install screen (if not installed)
brew install screen

# Start a screen session
screen -S product_monitor

# Run the script
python3 product_monitor.py

# Detach: Press Ctrl+A, then D
# Reattach: screen -r product_monitor
```

### Option 4: macOS Launch Agent (Runs on startup)
Create `~/Library/LaunchAgents/com.productmonitor.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.productmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/yijiedang/Documents/GitHub/crawler/product_monitor.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/yijiedang/Documents/GitHub/crawler</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/yijiedang/Documents/GitHub/crawler/monitor_output.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/yijiedang/Documents/GitHub/crawler/monitor_error.log</string>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.productmonitor.plist
```

## Important Notes:

1. **Computer must be on**: The script needs your computer running (or use a cloud server/VPS)

2. **Browser**: 
   - If `headless: false` - browser window must stay open
   - If `headless: true` - no browser window needed (runs in background)

3. **Sleep mode**: macOS sleep will pause the script. To prevent sleep:
   ```bash
   caffeinate -d
   ```

4. **Check if running**:
   ```bash
   ps aux | grep product_monitor
   ```

5. **View logs**:
   ```bash
   tail -f monitor.log
   # or
   tail -f monitor_output.log
   ```

## Recommended Setup for 24/7 Monitoring:

1. Set `headless: true` in config.json
2. Use screen or launch agent
3. Keep computer on (or use a VPS/cloud server)
4. Monitor logs regularly

