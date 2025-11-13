#!/bin/bash
# Test script to verify monitor works when screen is locked

echo "=" * 60
echo "Testing Locked Screen Functionality"
echo "=" * 60

# Check if plugged in
echo ""
echo "📌 Power Status:"
pmset -g batt | grep -E "(AC Power|Battery Power)"

# Check sleep settings
echo ""
echo "📌 Sleep Settings:"
pmset -g | grep -E "(sleep|displaysleep)" | head -3

# Start monitor in background
echo ""
echo "🚀 Starting monitor in background..."
cd "$(dirname "$0")"
./start_monitor.sh

# Wait a bit
sleep 3

# Check if running
echo ""
echo "📊 Monitor Status:"
if ps aux | grep -v grep | grep product_monitor > /dev/null; then
    echo "✅ Monitor is RUNNING"
    echo ""
    echo "Now you can:"
    echo "1. Lock your screen (Cmd+Ctrl+Q)"
    echo "2. Wait 30 seconds"
    echo "3. Unlock and check: tail -f monitor_output.log"
    echo ""
    echo "The monitor should keep running even when locked!"
else
    echo "❌ Monitor is NOT running"
fi

echo ""
echo "To check logs while locked, SSH in or unlock and run:"
echo "  tail -f monitor_output.log"

