#!/bin/bash
# Start monitor in background - survives terminal close

cd "$(dirname "$0")"

# Kill any existing monitor
pkill -f product_monitor.py 2>/dev/null
sleep 1

# Start in background with nohup
nohup python3 product_monitor.py > monitor_output.log 2>&1 &

echo "✅ Monitor started in background!"
echo "📝 View logs: tail -f monitor_output.log"
echo "🛑 Stop: pkill -f product_monitor.py"
echo "📊 Check status: ps aux | grep product_monitor"

