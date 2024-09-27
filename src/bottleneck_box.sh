#!/bin/bash

# set -x
set -e
set -u

# echo "CBR box"
# echo uplink_log_path: $uplink_log_path
# echo downlink_trace_file: $downlink_trace_file
# echo buf_size_bytes: $buf_size_bytes
# echo port: $port
# echo cca: $cca
# echo iperf_log_path: $iperf_log_path

log_uplink=true
DURATION=60  # seconds

SCRIPT=$(realpath "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")

if [[ $tbf_size_bytes == false ]]; then
    # CBR Box with finite buffer
    if [[ $log_uplink == true ]]; then
        mm-link \
            $cbr_uplink_trace_file \
            $downlink_trace_file \
            --uplink-queue=droptail \
            --uplink-log="$uplink_log_path" \
            --uplink-queue-args="bytes=$buf_size_bytes" -- \
            sh -c '$SCRIPT_PATH/sender.sh'
    else
        mm-link \
            $cbr_uplink_trace_file \
            $downlink_trace_file \
            --uplink-queue=droptail \
            --uplink-queue-args="bytes=$buf_size_bytes" -- \
            sh -c '$SCRIPT_PATH/sender.sh'
    fi
else
    # TBF Box with finite buffer
    if [[ $log_uplink == true ]]; then
        mm-tbf \
            $pkts_per_ms $tbf_size_bytes \
            $pkts_per_ms $tbf_size_bytes \
            --uplink-queue=droptail \
            --uplink-log="$uplink_log_path" \
            --uplink-queue-args="bytes=$buf_size_bytes" -- \
            sh -c '$SCRIPT_PATH/sender.sh'
    else
        mm-tbf \
            $pkts_per_ms $tbf_size_bytes \
            $pkts_per_ms $tbf_size_bytes \
            --uplink-queue=droptail \
            --uplink-queue-args="bytes=$buf_size_bytes" -- \
            sh -c '$SCRIPT_PATH/sender.sh'
    fi
fi

if [[ $log_uplink == true ]]; then
    mv $uplink_log_path $DATA_PATH
fi

# set +x
set +e
set +u