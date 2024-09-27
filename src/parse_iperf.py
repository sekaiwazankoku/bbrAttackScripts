import os
import pandas as pd
import argparse
import json

from common import MSEC_PER_SEC, ONE_PKT_PER_MS_MBPS_RATE, parse_exp, plot_df, plot_multi_exp, try_except_wrapper


def parse_jdict(fpath):
    with open(fpath, 'r') as f:
        try:
            jdict = json.load(f)
        except json.decoder.JSONDecodeError as e:
            print(f"ERROR: json decode error for file: {fpath}")
            print(e)
            raise e
    return jdict


def parse_iperf_summary(fpath):
    exp = parse_exp(os.path.basename(fpath).removesuffix('.json'))
    jdict = parse_jdict(fpath)

    ret = {
        'min_rtt': jdict['end']['streams'][0]['sender']['min_rtt'],
        'max_rtt': jdict['end']['streams'][0]['sender']['max_rtt'],
        'mean_rtt': jdict['end']['streams'][0]['sender']['mean_rtt'],
        'bits_per_second': jdict['end']['streams'][0]['receiver'][
            'bits_per_second'
        ],
        'retransmits': jdict['end']['streams'][0]['sender']['retransmits'],
        'time_seconds': jdict['end']['streams'][0]['sender']['seconds'],
    }
    Rm = exp['delay'] * 2
    rate = exp['rate']
    num_Rms = ret['time_seconds'] * MSEC_PER_SEC / Rm
    ret['retransmits_per_Rm'] = ret['retransmits'] / num_Rms
    ret['utilization'] = ret['bits_per_second'] / (ONE_PKT_PER_MS_MBPS_RATE * rate * 1e6)
    return ret


def parse_iperf_timeseries(fpath):
    jdict = parse_jdict(fpath)

    records = [
        {
            'start': record['streams'][0]['start'],
            'end': record['streams'][0]['end'],
            'seconds': record['streams'][0]['seconds'],
            'bits_per_second': record['streams'][0][
                'bits_per_second'
            ],
            'retransmits': record['streams'][0]['retransmits'],
            'rtt': record['streams'][0]['rtt'],
        }
        for record in jdict['intervals']
    ]
    return pd.DataFrame(records).sort_values(by='start')


def plot_single_exp(input_file, output_dir):
    # exp = parse_exp(input_file)
    df = parse_iperf_timeseries(input_file)
    df['mbps'] = df['bits_per_second'] / 1e6

    os.makedirs(output_dir, exist_ok=True)
    plot_df(df, 'retransmits',
            os.path.join(output_dir, 'iperf_retransmits.png'),
            xkey='end', xlabel='Time (s)',
            ylabel='# Retransmits',
            title=os.path.basename(input_file))
    plot_df(df, 'mbps',
            os.path.join(output_dir, 'iperf_throughput.png'),
            xkey='end', xlabel='Time (s)',
            ylabel='Throughput (Mbps)',
            title=os.path.basename(input_file))


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

    if(os.path.isdir(args.input)):
        plot_multi_exp(args.input, args.output, '.json', plot_single_exp)
    else:
        plot_single_exp(args.input, args.output)


if(__name__ == "__main__"):
    main()
