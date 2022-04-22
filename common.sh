#!/bin/bash

export LOG_DIR="/var/log/sensoriando"
export LOG_FILE="$LOG_DIR/web.log"

# Create directory if not exists
sudo mkdir -p $LOG_DIR

# Create log file if not exists
if [ ! -f $LOG_FILE ]; then
    sudo touch $LOG_FILE
fi

# Functions
log() {
    msg=$1
    date_log=$(date)

    echo $date_log "|" $msg | sudo tee -a $LOG_FILE
}

