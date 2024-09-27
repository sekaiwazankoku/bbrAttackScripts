#!/bin/bash

input=$1
output_dir=$2

mkdir -p $output_dir

mm-throughput-graph 10 $input.log > $output_dir/throughput-cbr_box.svg
mm-throughput-graph 10 $input.jitter_log > $output_dir/throughput-delay_box.svg
mm-delay-graph $input.log > $output_dir/delay-cbr_box.svg
mm-delay-graph $input.jitter_log > $output_dir/delay-delay_box.svg
