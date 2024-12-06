#!/usr/bin/bash

current_time=$(date +"%Y-%m-%d %H:%M:%S")
sudo systemctl restart tradewise.service
echo "$current_time Successfully Restarted tradewise service"
sudo systemctl restart TradeWise_Socket.service
echo "$current_time Successfully Restarted TradeWise Socket service"


