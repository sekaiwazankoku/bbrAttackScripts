#!/bin/bash

TRACE_PATH=/home/ubuntu/Projects/Verification/CCmatic-empirical/mahimahi-traces

PORT=$1
delay=$2
pkts_per_ms=$3
alg=$4
buf_size=$5

mm-delay $delay mm-link $TRACE_PATH/${pkts_per_ms}ppms.trace $TRACE_PATH/${pkts_per_ms}ppms.trace -- iperf3 -c $MAHIMAHI_BASE -p $PORT -Z $alg -t 10

# https://fasterdata.es.net/host-tuning/linux/recent-tcp-enhancements/bbr-testing-using-iperf3/
iperf3 -c localhost -p 5201 -t 25
sleep 5
