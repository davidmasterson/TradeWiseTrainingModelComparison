#!/bin/bash

# Get current time
current_time="$(date +'%Y-%m-%d %H:%M:%S')"

echo "Creating websocket connection"
python_script="/home/ubuntu/TradeWiseTrainingModelComparison/WebsocketUtility/websocket_runner.py"
python_executable="/home/ubuntu/miniconda3/envs/tf-env/bin/python3"

if [[ -f $python_script ]]; then
    if [[ -x $python_executable ]]; then
        $python_executable $python_script
        if [[ $? -eq 0 ]]; then
            echo "$current_time - Successfully sent all end-of-day report emails."
        else
            echo "$current_time - Failed to send report emails due to an error in the script." >&2
        fi
    else
        echo "$current_time - Python executable is not found or not executable: $python_executable" >&2
    fi
else
    echo "$current_time - Script file not found: $python_script" >&2
fi