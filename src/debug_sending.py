import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as interp
from common import MM_PKT_SIZE, try_except_wrapper
from parse_dmesg import GenericccLog
from parse_mahimahi import MahimahiLog


@try_except_wrapper
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input', required=True,
        type=str, action='store',
        help='path to mahimahi trace')
    parser.add_argument(
        '-o', '--output', required=True,
        type=str, action='store',
        help='path output figure')
    args = parser.parse_args()

    mm_path = f"{args.input}.log"
    gccc_path = f"{args.input}.genericcc"

    ml = MahimahiLog(mm_path)
    mm_arrival_df = ml.arrival_df
    mm_arrival_df['cum_packets'] = mm_arrival_df['cum_bytes'] / MM_PKT_SIZE

    gccc = GenericccLog(gccc_path)
    gccc_df = gccc.df

    # import ipdb; ipdb.set_trace()
    os.makedirs(args.output, exist_ok=True)

    fig, ax = plt.subplots()
    ax.plot(gccc_df['time'], gccc_df['expected_cum_sent'],
            label='CCA expectation')
    ax.plot(gccc_df['time'], gccc_df['cum_segs_sent'], label='Sent by sender')
    ax.plot(mm_arrival_df['time'],
            mm_arrival_df['cum_packets'], label='Arrive at MM')
    ax.legend()
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Cummulative packets')
    fig.set_tight_layout(True)
    out_path = os.path.join(args.output, "cum_packets-debug.pdf")
    print(out_path)
    fig.savefig(out_path)
    plt.close(fig)

    actual_sent = interp.interp1d(gccc_df['time'], gccc_df['cum_segs_sent'])
    expected_sent = interp.interp1d(gccc_df['time'], gccc_df['expected_cum_sent'])
    at_mm = interp.interp1d(mm_arrival_df['time'], mm_arrival_df['cum_packets'])

    times = np.linspace(1000, 59000, 10000)
    expected_actual = expected_sent(times) - actual_sent(times)
    actual_mm = actual_sent(times) - at_mm(times)
    fig, ax = plt.subplots()
    ax.plot(times, expected_actual, label='CCA Expectation - Sent by sender')
    ax.plot(times, actual_mm, label='Sent by sender - Arrive at MM')
    ax.legend()
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Packets')
    fig.set_tight_layout(True)
    out_path = os.path.join(args.output, "cum_packets-debug-diff.pdf")
    print(out_path)
    fig.savefig(out_path)
    plt.close(fig)


if(__name__ == '__main__'):
    main()