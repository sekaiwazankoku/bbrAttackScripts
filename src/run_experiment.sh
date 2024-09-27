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

pkts_per_ms=$1
delay_ms=$2
buf_size_bdp=$3
cca=$4
delay_uplink_trace_file=$5
cbr_uplink_trace_file=$6
downlink_trace_file=$7
port=$8
n_parallel=$9
tbf_size_bdp=${10}

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

tbf_size_bytes=false
if [[ $tbf_size_bdp != false ]]; then
    tbf_size_bytes=$(echo "$tbf_size_bdp*$bdp_bytes/1" | bc)
    exp_tag+="-tbf_size_bdp[$tbf_size_bdp]"
fi

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
    # Start dmesg logging
    # https://unix.stackexchange.com/questions/390184/dmesg-read-kernel-buffer-failed-permission-denied
    # Run dmesg without sudo. Now we can have concurrent isolated experiments.
    # Ideally we want to do `dmesg --follow-new`, some versions don't have that :(
    sudo dmesg --clear
    dmesg --level info --follow --notime 1> $dmesg_log_path 2>&1 &
    dmesg_pid=$!
    echo "Started dmesg logging with: $dmesg_pid"

    # sudo -b dmesg -l info -W -t 1> $dmesg_log_path 2>&1
    # echo "Started dmesg logging"
    # # Due to -b flag, sudo immediately returns.
    # # There is no way to obtain the child's pid.
    # # (https://stackoverflow.com/questions/9315829/how-to-get-the-pid-of-command-running-with-sudo)
    # # Faced issues without the -b flag as well.
    # # (https://stackoverflow.com/questions/26109878/running-a-program-in-the-background-as-sudo)
    # # We are then resorting to kill all dmesg processes.
    # # This is not ideal on a shared machine.
    # # Currently tests are in an isolated VM, so this is fine.
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
if [[ $tbf_size_bdp == false ]]; then
    if [[ $log_uplink == true ]]; then
        mm-delay $delay_ms \
                    mm-link \
                    $delay_uplink_trace_file \
                    $downlink_trace_file \
                    --uplink-log="$uplink_log_path_delay_box" \
                    -- $SCRIPT_PATH/bottleneck_box.sh
    else
        mm-delay $delay_ms \
                    mm-link \
                    $delay_uplink_trace_file \
                    $downlink_trace_file \
                    -- $SCRIPT_PATH/bottleneck_box.sh
    fi

    if [[ $log_uplink == true ]]; then
        mv $uplink_log_path_delay_box $DATA_PATH
    fi
else
    echo "Not launching delay box as bottleneck is TBF only"
    mm-delay $delay_ms $SCRIPT_PATH/bottleneck_box.sh
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