#!/bin/bash

clear
while true; do
    date
    echo ""
    echo "--------------------"
    get_gdq_schd.py
    echo "------------------"
    echo""
    sleep $((60*30))
done

