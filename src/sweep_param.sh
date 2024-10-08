#!/bin/bash

# set -x
set -e

# https://stackoverflow.com/questions/360201/how-do-i-kill-background-processes-jobs-when-my-shell-script-exits
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

SCRIPT=$(realpath "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")
export SCRIPT_PATH
EXPERIMENTS_PATH=$(realpath $SCRIPT_PATH/../)

TRACE_PATH=$EXPERIMENTS_PATH/mahimahi-traces
DATA_PATH_ROOT=${DATA_PATH_ROOT:-$EXPERIMENTS_PATH/data/uplink-droptail-vm}
DATA_PATH_ROOT=$(realpath -sm $DATA_PATH_ROOT)

start_port=7111

# Main logic:
mkdir -p $DATA_PATH_ROOT

# Choices
# pkts_per_ms=4
# delay_ms=50
# buf_size_bdp=0.5
# cca="rocc"

cca_choices=('rocc_ccmatic' 'cubic' 'bbr' 'rocc' 'reno' 'simple_rocc')
cca_choices=('rocc_ccmatic' 'simple_rocc')
cca_choices=('aitd_combad' 'rocc_ccmatic')
# cca_choices=('rocc_ccmatic')
cca_choices=('aitd_combad' 'rocc_ccmatic' 'cubic' 'bbr' 'rocc' 'reno')
cca_choices=('aitd_combad_rm' 'rocc_ccmatic_rm')
cca_choices=('rocc_ccmatic_rm')
cca_choices=('cubic' 'bbr' 'rocc' 'reno' 'aitd_combad_fi' 'aitd_combad_rm' 'rocc_ccmatic_rm')
cca_choices=('cubic' 'bbr' 'reno' 'rocc' 'belief_cca' 'aitd_combad_fi')
cca_choices=('slow_conv' 'belief_cca' 'belief_opt')
cca_choices=('belief_opt')
cca_choices=('cubic')
cca_choices=('cubic' 'bbr' 'slow_conv' 'belief_cca' 'belief_opt' 'slow_paced')
cca_choices=('bbr' 'cubic' 'reno')
# cca_choices=('slow_conv' 'slow_paced' 'slow_paced2')
cca_choices=('slow_conv' 'slow_paced' 'fast_conv')
# cca_choices=('slow_conv')
cca_choices=('genericcc_markovian' 'genericcc_slow_conv')
cca_choices=('bbr')
# cca_choices=('genericcc_markovian')
cca_choices=('genericcc_slow_conv' 'genericcc_fast_conv')
cca_choices=('bbr' 'cubic' 'genericcc_slow_conv' 'genericcc_fast_conv' 'genericcc_markovian')
# cca_choices=('slow_conv')
# cca_choices=('genericcc_slow_conv')
cca_choices=('bbr2' 'cubic')
# cca_choices=('bbr' 'genericcc_slow_conv' 'genericcc_markovian')
cca_choices=('genericcc_slow_conv' 'genericcc_slow_conv_1' 'genericcc_slow_conv_2' 'genericcc_slow_conv_3' 'cubic' 'bbr')
cca_choices=('genericcc_slow_conv_1' 'genericcc_slow_conv_2' 'genericcc_slow_conv_3' 'genericcc_slow_conv_4' 'genericcc_slow_conv_5')
cca_choices=('cubic' 'bbr' 'genericcc_slow_conv' 'genericcc_slow_conv_1' 'genericcc_slow_conv_2' 'genericcc_slow_conv_3' 'genericcc_slow_conv_4' 'genericcc_slow_conv_5')
cca_choices=('genericcc_slow_conv_1' 'genericcc_slow_conv_2' 'genericcc_slow_conv_3' 'genericcc_slow_conv_4' 'genericcc_slow_conv_5')
cca_choices=('genericcc_slow_conv')
cca_choices=('genericcc_slow_conv' 'genericcc_slow_conv_1' 'genericcc_slow_conv_2' 'genericcc_slow_conv_3')
cca_choices=('genericcc_slow_conv_4' 'genericcc_slow_conv_5')
cca_choices=('cubic' 'bbr' 'genericcc_slow_conv' 'genericcc_slow_conv_1' 'genericcc_slow_conv_2' 'genericcc_slow_conv_3' 'genericcc_markovian' 'genericcc_fast_conv')
cca_choices=('bbr2')
cca_choices=('genericcc_fast_conv')
cca_choices=('genericcc_slow_conv_1' 'genericcc_fast_conv')
cca_choices=('genericcc_slow_conv_1')
cca_choices=('bbr')

buf_size_bdp_choices=(0.125 0.25 0.5 0.75 1 2 4 8 16 32 64)
buf_size_bdp_choices=(0.125 0.25)
buf_size_bdp_choices=(0.5 8)
buf_size_bdp_choices=(0.125 0.25 0.5 0.75 1 2 4 8)
# buf_size_bdp_choices=(8)
buf_size_bdp_choices=(0.125 1 2 8 32)
# buf_size_bdp_choices=(0.125 32)
buf_size_bdp_choices=(0.125 0.25 0.5 1 2 4 8 32)
buf_size_bdp_choices=(0.01)
buf_size_bdp_choices=(0.005 0.01 0.25 0.5 1 2 4 8 32)
buf_size_bdp_choices=(0.125 0.1875 0.25 0.375 0.5 0.75 1 1.5 2 3 4 6 8 12 16 24 32)
# buf_size_bdp_choices=(0.005 0.01 1 32)
buf_size_bdp_choices=(0.03125 0.0625 0.125 0.25 0.5 1 2 4 8 16)
buf_size_bdp_choices=(0.5 8)
buf_size_bdp_choices=(0.5)

# cca_choices=('bbr')
# buf_size_bdp_choices=(64)

# delay_ms_choices=(10 20 40)
delay_ms_choices=(10 40 80)
# delay_ms_choices=(80)
delay_ms_choices=(40)
# delay_ms_choices=(40)

pkts_per_ms_choices=(2 4 8)
# pkts_per_ms_choices=(4 8)
# pkts_per_ms_choices=(8)
pkts_per_ms_choices=(8)

#EXPERIMENT="jitter"
#EXPERIMENT="bimodal_jitter"
#EXPERIMENT="aggregation"
#EXPERIMENT="tbf"
EXPERIMENT="ideal"
#EXPERIMENT="fullaggregation"

export n_flows=1

tbf_size_bdp=false
if [[ $EXPERIMENT == "tbf" ]]; then
    tbf_size_bdp=1
fi

n_parallel=1
#n_parallel=6
#n_parallel=32
#n_parallel=16
i=0
exp_pids=()
for pkts_per_ms in "${pkts_per_ms_choices[@]}"; do
for delay_ms in "${delay_ms_choices[@]}"; do
    if [[ $EXPERIMENT != "ideal" ]] && [[ $EXPERIMENT != "tbf" ]]; then
        python $EXPERIMENTS_PATH/src/trace_generators/${EXPERIMENT}_trace.py $pkts_per_ms $delay_ms $TRACE_PATH
    fi
    # DATA_PATH=$DATA_PATH_ROOT/${EXPERIMENT}_half-rate[${pkts_per_ms}]-delay[${delay_ms}]
    DATA_DIR=rate[${pkts_per_ms}]-delay[${delay_ms}]
    DATA_PATH=$DATA_PATH_ROOT/$DATA_DIR
    mkdir -p $DATA_PATH
    export DATA_DIR
    export DATA_PATH

    for buf_size_bdp in "${buf_size_bdp_choices[@]}"; do
    for cca in "${cca_choices[@]}"; do
        if [[ $((i%n_parallel)) == 0 ]] && [[ $i -gt 0 ]]; then
            wait "${pids[@]}"
        fi
        i=$((i+1))

        echo "--------------------------------------------------------------------------------"
        echo "Running experiment($i): Rate: $pkts_per_ms ppms, Delay: $delay_ms ms, Buffer: $buf_size_bdp BDP, CCA: $cca"

        if [[ $EXPERIMENT == "ideal" ]]; then
            delay_uplink_trace_file=$TRACE_PATH/${pkts_per_ms}ppms.trace
            cbr_uplink_trace_file=$TRACE_PATH/${pkts_per_ms}ppms.trace
        else
            delay_uplink_trace_file=$TRACE_PATH/rate[${pkts_per_ms}]-delay[${delay_ms}]-${EXPERIMENT}[${delay_ms}].trace
            cbr_uplink_trace_file=$TRACE_PATH/${pkts_per_ms}ppms.trace
        fi
        downlink_trace_file=$TRACE_PATH/${pkts_per_ms}ppms.trace

        cmd="$SCRIPT_PATH/run_experiment.sh --attack $pkts_per_ms $delay_ms $buf_size_bdp $cca " # Need too add "--attack" to test attack scenario
        cmd+="$delay_uplink_trace_file $cbr_uplink_trace_file $downlink_trace_file "
        cmd+="$((start_port + i)) $n_parallel $tbf_size_bdp"
        echo $cmd
        # sleep 5
        # cmd="sleep 5"
        export cmd
        sh -c '$cmd' &
        exp_pids+=($!)
        sleep 2
    done
    done

done
done

# https://stackoverflow.com/questions/40377623/bash-wait-command-waiting-for-more-than-1-pid-to-finish-execution
wait "${pids[@]}"
echo "Done"

# set +x
set +e
