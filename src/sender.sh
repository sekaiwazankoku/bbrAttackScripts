#!/bin/bash

set -e
set -u

DURATION=120  # seconds
OVERLAP_DURATION=30  # seconds

SCRIPT=$(realpath "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")
EXPERIMENTS_PATH=$(realpath $SCRIPT_PATH/../)
GENERICCC_PATH=$(realpath $EXPERIMENTS_PATH/../ccas/genericCC)
echo "Before launch_sender"
launch_sender() {
    duration=$1
    flow_genericcc_logfilepath=$2
    flow_iperf_log_path=$3
    delay=$4
    echo "Beginning of launch sender"
    is_genericcc=false
    if [[ $cca == genericcc_* ]]; then
        is_genericcc=true
        short_cca=$(echo $cca | sed 's/genericcc_//g')

        cc_params=""
        if [[ $short_cca == "markovian" ]]; then
            cc_params="delta_conf=do_ss:auto:0.5"
        # elif [[ $short_cca == "slow_conv" ]] || [[ $short_cca == "fast_conv" ]]; then
        else
            cc_params="logfilepath=$flow_genericcc_logfilepath"
        fi
    fi

    iperf_cca=$cca
    if [[ $cca == "bbr3" ]]; then
        # They renamed bbr3 to bbr.
        # Only run this in the appropriate VM.
        HOSTNAME="$(hostname)"
        if [[ $HOSTNAME != "bbrv3-testbed" ]]; then
            exit 1
        fi
        iperf_cca="bbr"
        echo "if statement inside the launch_sender: if cca=bbr"

    fi

    # Sender command
    sender_cmd="iperf3 -c $MAHIMAHI_BASE -p $port --congestion $iperf_cca "
    sender_cmd+="-t $duration --json --logfile $flow_iperf_log_path"
    # ^^ The base does not change when we start a new nested shell, so we can
    # actually execute $MAHIMAHI_BASE now itself.
    if [[ $is_genericcc == true ]]; then
        sender_cmd="mm-delay $delay $GENERICCC_PATH/sender serverip=$MAHIMAHI_BASE serverport=$port "
        sender_cmd+="offduration=0 onduration=${duration}000 "
        sender_cmd+="cctype=$short_cca $cc_params "
        sender_cmd+="traffic_params=deterministic,num_cycles=1"
    fi

    # https://unix.stackexchange.com/questions/356534/how-to-run-string-with-values-as-a-command-in-bash
    eval "$sender_cmd &"
}

if [[ n_flows -eq 1 ]]; then
    echo "If n_flows -eq 1 statement"

    launch_sender $DURATION $genericcc_logfilepath $iperf_log_path 0
    wait

else
    for i in $(seq 1 $n_flows); do
        flow_tag="flow[$i]-"

        flow_genericcc_logfilepath=$RAMDISK_DATA_PATH/$flow_tag$exp_tag.genericcc
        if [[ -f $flow_genericcc_logfilepath ]]; then
            rm $flow_genericcc_logfilepath
        fi

        flow_iperf_log_path=$RAMDISK_DATA_PATH/$flow_tag$exp_tag.json
        if [[ -f $flow_iperf_log_path ]]; then
            rm $flow_iperf_log_path
        fi

        launch_sender $(( OVERLAP_DURATION*n_flows )) $flow_genericcc_logfilepath $flow_iperf_log_path 0
        # Different RTT
        # launch_sender $(( OVERLAP_DURATION*n_flows )) $flow_genericcc_logfilepath $flow_iperf_log_path $(( (delay_ms-1)*i ))
        echo "Flow $i started"
        echo "Sleeping for $OVERLAP_DURATION seconds"
        sleep $OVERLAP_DURATION
    done

    # Once all flows have completed
    wait

    # Move all the logs from RAMDISK to DATA_PATH
    for i in $(seq 1 $n_flows); do
        flow_tag="flow[$i]-"

        genericcc_logfilepath=$RAMDISK_DATA_PATH/$flow_tag$exp_tag.genericcc
        if [[ -f $genericcc_logfilepath ]]; then
            mv $genericcc_logfilepath $DATA_PATH
        fi

        iperf_log_path=$RAMDISK_DATA_PATH/$flow_tag$exp_tag.json
        if [[ -f $iperf_log_path ]]; then
            mv $iperf_log_path $DATA_PATH
        fi
    done
fi
echo "End of sender.sh"

set +u
set +e
