#!/bin/bash

set -e
set -u
# set -x

log_uplink=false
MM_PKT_SIZE=1504  # bytes
# TCP MSS          = 1448 bytes
# Ethernet payload = 1500 bytes (= MSS + 20 [IP] + 32 [TCP])
# https://github.com/zehome/MLVPN/issues/26
# MM_PKT_SIZE      = 1504 bytes (= Ethernet payload + 4 [TUN overhead])
# Ethernet MTU     = 1518 bytes (= Ethernet payload + 18 [Ethernet])
# On the wire      = 1538 bytes (= Ethernet MTU + 20 [Preamble + IPG])

SCRIPT=$(realpath "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")
export SCRIPT_PATH
EXPERIMENTS_PATH=$(realpath $SCRIPT_PATH/../)
GENERICCC_PATH=$(realpath $EXPERIMENTS_PATH/../ccas/genericCC)

RAMDISK_PATH=/mnt/ramdisk
RAMDISK_DATA_PATH=$RAMDISK_PATH/$DATA_DIR
mkdir -p $RAMDISK_DATA_PATH

# Define the attack flag
attack_flag=false

# Check if the first argument is --attack
if [[ $1 == "--attack" ]]; then
    attack_flag=true
    shift  # Shift parameters so $1 becomes pkts_per_ms and others
fi

pkts_per_ms=$1
delay_ms=$2
buf_size_bdp=$3
cca=$4
delay_uplink_trace_file=$5
cbr_uplink_trace_file=$6
downlink_trace_file=$7
port=$8
n_parallel=$9
#tbf_size_bdp=${10}

#attack variables
attack_rate=${11}       # Dynamic attack rate input
queue_size=${12}        # Queue size for attack
delay_budget=${13}      # Max allowable delay for attack

#To check for parameter values:
#echo "attack_flag: $attack_flag"
#echo "pkts_per_ms: $pkts_per_ms"
#echo "delay_ms: $delay_ms"
# and so on for other parameters

is_genericcc=false
if [[ $cca == genericcc_* ]]; then
    is_genericcc=true
fi

log_dmesg=true
if [[ n_parallel -gt 1 ]] || [[ is_genericcc == true ]]; then
    log_dmesg=false
fi

# echo "Delay Box args:"
# echo mahimahi_base: $MAHIMAHI_BASE

# Derivations
bdp_bytes=$(echo "$MM_PKT_SIZE*$pkts_per_ms*2*$delay_ms" | bc)
buf_size_bytes=$(echo "$buf_size_bdp*$bdp_bytes/1" | bc)
exp_tag="rate[$pkts_per_ms]-delay[$delay_ms]-buf_size[$buf_size_bdp]-cca[$cca]"

iperf_log_path=$DATA_PATH/$exp_tag.json
if [[ -f $iperf_log_path ]]; then
    rm $iperf_log_path
fi

uplink_log_path=$RAMDISK_DATA_PATH/$exp_tag.log
if [[ -f $uplink_log_path ]]; then
    rm $uplink_log_path
fi

summary_path=$DATA_PATH/$exp_tag.summary
if [[ -f $summary_path ]]; then
    rm $summary_path
fi

uplink_log_path_delay_box=$RAMDISK_DATA_PATH/$exp_tag.jitter_log
if [[ -f $uplink_log_path_delay_box ]]; then
    rm $uplink_log_path_delay_box
fi

dmesg_log_path=$RAMDISK_DATA_PATH/$exp_tag.dmesg
if [[ $log_dmesg == true ]]; then
    if [[ -f $dmesg_log_path ]]; then
        rm $dmesg_log_path
    fi
fi

genericcc_logfilepath=$RAMDISK_DATA_PATH/$exp_tag.genericcc
if [[ -f $genericcc_logfilepath ]]; then
    rm $genericcc_logfilepath
fi

#for attack logging
attack_log_path=$RAMDISK_DATA_PATH/$exp_tag-attack.log
if [[ -f $attack_log_path ]]; then
    rm $attack_log_path
fi

# Start Server
if [[ $is_genericcc == true ]]; then
    echo "Using genericCC"
    $GENERICCC_PATH/receiver $port &
    server_pid=$!
else
    echo "Using iperf"
    iperf3 -s -p $port &
    server_pid=$!
fi
echo "Started server: $server_pid"

if [[ $log_dmesg == true ]]; then
    # Start dmesg logging for kernel messages
    sudo dmesg --clear
    dmesg --level info --follow --notime 1> $dmesg_log_path 2>&1 &
    dmesg_pid=$!
    echo "Started dmesg logging with: $dmesg_pid"
fi

# Start client (behind emulated delay and link)
echo "Starting client"
export RAMDISK_DATA_PATH
export port
export cca
export iperf_log_path

export uplink_log_path
export cbr_uplink_trace_file
export downlink_trace_file
export buf_size_bytes
export genericcc_logfilepath
export tbf_size_bytes
export pkts_per_ms
export delay_ms

export exp_tag

# echo "Delay box"
# echo delay_ms: $delay_ms
# echo uplink_log_path_delay_box: $uplink_log_path_delay_box
# echo uplink_trace_file: $uplink_trace_file
# echo downlink_trace_file: $downlink_trace_file

# Propagation delay box, then delay box (jittery trace) with inf buffer
if [[ $attack_flag == true ]]; then
    echo "Running attack scenario"
    mm-bbr-attack $attack_rate $queue_size $delay_budget --uplink-log="$uplink_log_path_delay_box" --attack-log="$attack_log_path" \
        $SCRIPT_PATH/bottleneck_box.sh

    # Move attack log
    if [[ -f $attack_log_path ]]; then
        mv $attack_log_path $DATA_PATH
    fi
else 
    echo "Running regular scenario"
    mm-delay $delay_ms \
            mm-link \
            $delay_uplink_trace_file \
            $downlink_trace_file \
            --uplink-log="$uplink_log_path_delay_box" \
            -- $SCRIPT_PATH/bottleneck_box.sh

fi

# Move uplink log
if [[ $log_uplink == true ]]; then
    mv $uplink_log_path_delay_box $DATA_PATH
fi

echo "Sleeping"  # so that iperf and mahimahi have some time to gracefully cleanup any sockets etc.
sleep 5

echo "Killing server"
kill $server_pid

if [[ $log_dmesg == true ]]; then
    echo "Killing dmesg logging"
    kill $dmesg_pid
    # sudo killall dmesg
    mv $dmesg_log_path $DATA_PATH
fi

if [[ $is_genericcc == true ]] && [[ -f $genericcc_logfilepath ]]; then
    mv $genericcc_logfilepath $DATA_PATH
fi

set +e
set +u
# set +x
