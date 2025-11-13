#!/bin/bash
# Script to run the product monitor in the background continuously

cd "$(dirname "$0")"

# Kill any existing monitor
pkill -f product_monitor.py 2>/dev/null

# Run in background with nohup (survives terminal close)
nohup python3 product_monitor.py > monitor_output.log 2>&1 &

echo "✅ Monitor started in background!"
echo "📝 Logs: monitor_output.log"
echo "🛑 To stop: pkill -f product_monitor.py"
echo ""
echo "Process ID: $!"

