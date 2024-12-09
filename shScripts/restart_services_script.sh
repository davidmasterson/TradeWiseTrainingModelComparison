#!/bin/bash

# Get current time
current_time="$(date +'%Y-%m-%d %H:%M:%S')"

# Restart TradeWise service
sudo systemctl restart tradewise.service
echo "$current_time Successfully Restarted tradewise service"

# Stop TradeWise Socket service
sudo systemctl stop TradeWise_Socket.service
echo "$current_time Successfully stopped TradeWise Socket service"

# Activate Conda environment
sudo systemctl start TradeWise_Socket.service
echo "$current_time Successfully started TradeWise Socket service"

