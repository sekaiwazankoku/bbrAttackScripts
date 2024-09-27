import os
import argparse
from typing import Dict, List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from common import is_float, plot_df, plot_multi_exp, try_except, parse_exp, ONE_PKT_PER_MS_MBPS_RATE, MSEC_PER_SEC

from pubplot import Document
from plot_config.figure_type_creator import FigureTypeCreator as FTC


ftc = FTC(paper_use_small_font=True, use_markers=False)
doc: Document = ftc.get_figure_type()
ppt: Document = FTC(pub_type='presentation', use_markers=False).get_figure_type()


def parse_params(line: str, prefix):
    # rocc flow 9 cwnd 217 pacing 3039897 rtt 203873 mss 1448 timestamp 96884319441 interval 207681
    # rocc pkts_acked 212 hist_us 206728 pacing 2997871 loss_mode 1 app_limited 0 rs_limited 0

    record = {}
    params = line.removeprefix(prefix)
    param_list = params.split(' ')
    for param_name, param_val in zip(param_list[::2], param_list[1::2]):
        record[param_name] = float(param_val) if(is_float(param_val)) else param_val
    return record


class DmesgLog:

    prefix = 'rocc '
    fpath: str
    df: pd.DataFrame
    # summary: Dict[str, Any] = {}

    def __init__(self, fpath):
        self.fpath = fpath
        self.parse_dmesg_log()

    def parse_dmesg_log(self):
        with open(self.fpath, 'r') as f:
            lines = f.read().split('\n')
            # Skip first 2 lines, these are sometimes from the last run.
            lines = lines[2:]

        records = []
        record = None
        skipped_line = False
        for line in lines:
            if(line.startswith('rocc flow ')):
                # save previous record if any and start a new one
                if(record is not None):
                    records.append(record)
                record = {}
                record.update(parse_params(line, self.prefix))

            elif (line.startswith('rocc pkts_acked ') or
                  line.startswith('rocc min_c ')):
                # # Sometimes the first line in dmesg is from previous run
                # if(not skipped_line):
                #     if(record is None):
                #         skipped_line = True
                #         continue
                assert record is not None
                record.update(parse_params(line, self.prefix))

        df = pd.DataFrame(records)

        # timestamp is in us
        start_tstamp = df['timestamp'].min()
        df['time'] = (df['timestamp'] - start_tstamp)/1e3
        # time is in ms

        df['rate'] = df['pacing'] / df['mss']

        self.df = df


class GenericccLog:

    prefix = 'INFO '
    fpath: str
    df: pd.DataFrame
    # summary: Dict[str, Any] = {}

    def __init__(self, fpath):
        self.fpath = fpath
        self.parse_genericcc_log()
        self.exp = parse_exp(os.path.basename(fpath).removesuffix('.genericcc'))

    def parse_genericcc_log(self):
        with open(self.fpath, 'r') as f:
            lines = f.read().split('\n')

        records = []
        record = None
        skipped_line = False
        for line in lines:
            if(line.startswith('INFO new ')):
                # save previous record if any and start a new one
                if(record is not None):
                    records.append(record)
                record = {}
                record.update(parse_params(line, 'INFO new '))

            elif(line.startswith('INFO ')):
                assert record is not None
                record.update(parse_params(line, self.prefix))

            elif(line.startswith('ERROR ')):
                print(line)

        df = pd.DataFrame(records)
        self.df = df

        df['rate'] = df['sending_rate']


def plot_single_exp(fpath, output_dir):
    if(fpath.endswith('.dmesg')):
        dl = DmesgLog(fpath)
        df = dl.df
    elif(fpath.endswith('.genericcc')):
        dl = GenericccLog(fpath)
        df = dl.df
    else:
        raise ValueError(f'Unknown file type {fpath}')

    # trace_end_ms = df['time'].max()
    # begin_ms = trace_end_ms - 5000
    # end_ms = begin_ms + 2000
    # filtered_df = df[np.logical_and(df['time'] >= begin_ms, df['time'] <= end_ms)]
    filtered_df = df
    # import ipdb; ipdb.set_trace()

    os.makedirs(output_dir, exist_ok=True)
    plot_df(filtered_df,
            'cwnd', os.path.join(output_dir, "cca_cwnd.pdf"),
            xlabel='Time (ms)', ylabel='cwnd (packets)')
    plot_df(filtered_df,
            'rate', os.path.join(output_dir, "cca_rate.pdf"),
            xlabel='Time (ms)', ylabel='rate (packets/sec)')
    plot_df(filtered_df,
            'min_c', os.path.join(output_dir, "cca_min_c.pdf"),
            xlabel='Time (ms)', ylabel='min_c (packets/sec)')
    plot_df(filtered_df,
            'max_c', os.path.join(output_dir, "cca_max_c.pdf"),
            xlabel='Time (ms)', ylabel='max_c (packets/sec)',
            yscale='log')
    if('min_c_lambda' in filtered_df.columns):
        plot_df(filtered_df,
                'min_c_lambda', os.path.join(output_dir, "cca_min_c_lambda.pdf"),
                xlabel='Time (ms)', ylabel='min_c_lambda (packets/sec)')
    if('bq_belief1' in filtered_df.columns):
        plot_df(filtered_df,
                'bq_belief1', os.path.join(output_dir, "cca_inflight.pdf"),
                xlabel='Time (ms)', ylabel='inflight (packets)')
    if('bq_belief2' in filtered_df.columns):
        plot_df(filtered_df,
                'bq_belief2', os.path.join(output_dir, "cca_bq_belief2.pdf"),
                xlabel='Time (ms)', ylabel='bq_belief2 (packets)')
    if('state' in filtered_df.columns):
        plot_df(filtered_df,
                'state', os.path.join(output_dir, "cca_state.pdf"),
                xlabel='Time (ms)', ylabel='state (enum)')
    if('prev_measured_sending_rate' in filtered_df.columns):
        plot_df(filtered_df,
            'prev_measured_sending_rate', os.path.join(output_dir, "cca_measured_sending_rate.pdf"),
            xlabel='Time (ms)', ylabel='Measured sending rate (packets/sec)')
    if('cum_segs_lost' in filtered_df.columns):
        plot_df(filtered_df,
            'cum_segs_lost', os.path.join(output_dir, "cca_cum_segs_lost.pdf"),
            xlabel='Time (ms)', ylabel='Cum. segments lost')
    # loss_name = 'loss_mode'
    # if('loss_mode' not in filtered_df.columns):
    #     loss_name = 'loss_happened'
    # plot_df(filtered_df,
    #         loss_name, os.path.join(args.output, "cca_loss.pdf"),
    #         xlabel='Time (ms)', ylabel='loss (bool)')


def plot_multi_flow_single_metric(output_dir, cca, metric, ylabel, dl_list):
    figpath = os.path.join(output_dir, f"{metric}-multiflow.svg")

    fig, ax = plt.subplots()
    # fig, ax = ppt.subfigures()
    fig, ax = ppt.subfigures(1, 1, xscale=0.8, yscale=0.8)
    dl_list.sort(key=lambda dl: dl.exp["flow"])
    # import ipdb; ipdb.set_trace()

    min_wall_time = np.inf
    for dl in dl_list:
        # compute min wall time
        df = dl.df
        if ("wall_time" in df.columns):
            min_wall_time = min(min_wall_time, df["wall_time"].min())
    if(min_wall_time == np.inf):
        min_wall_time = 0

    for dl in dl_list:
        df = dl.df
        wall_time = 10000 * (dl.exp["flow"]-1) + df["time"]
        if("wall_time" in df.columns):
            wall_time = df["wall_time"]
        # import ipdb; ipdb.set_trace()
        df["sending_rate_mbps"] = df["rate"] * ONE_PKT_PER_MS_MBPS_RATE / MSEC_PER_SEC
        df["delivered_rate_mbps"] = df["cum_segs_delivered"].diff() / df["time"].diff() * ONE_PKT_PER_MS_MBPS_RATE
        df["sent_rate_mbps"] = df["cum_segs_sent"].diff() / df["time"].diff() * ONE_PKT_PER_MS_MBPS_RATE
        df["loss_rate_mbps"] = df["cum_segs_lost"].diff() / df["time"].diff() * ONE_PKT_PER_MS_MBPS_RATE
        wt_secs = (wall_time-min_wall_time)/1000
        # ax.plot(wt_secs, rate, '.')
        ax.plot(wt_secs, df[metric], alpha=0.5)
        ax.set_xlabel("Time [s]")
        ax.set_ylabel(ylabel)
        # ax.set_title(cca)
        # fig.set_tight_layout(True)
        fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
        fig.savefig(figpath)
        # plt.close(fig)


def plot_multi_flow_multi_metric(input_dir, output_dir):
    data_files = []
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith('.genericcc'):
                fpath = os.path.join(root, filename)
                data_files.append(fpath)

    dfs: Dict[(str, float), List[GenericccLog]] = {}
    for fpath in data_files:
        if(fpath.endswith('.genericcc')):
            dl = GenericccLog(fpath)
        else:
            raise ValueError(f'Unknown file type {fpath}')
        dfs.setdefault((dl.exp["cca"], dl.exp["buf_size"]), []).append(dl)


    os.makedirs(output_dir, exist_ok=True)
    for (cca, buf_size), dl_list in dfs.items():
        dl = dl_list[0]
        exp = dl.exp
        if(int(buf_size) == buf_size):
            buf_size = int(buf_size)
        this_output_dir = os.path.join(output_dir, f"rate[{int(exp['rate'])}]-delay[{int(exp['delay'])}]-buf_size[{buf_size}]-cca[{cca}]")
        os.makedirs(this_output_dir, exist_ok=True)
        plot_multi_flow_single_metric(this_output_dir, cca, "sending_rate_mbps", "Sending rate [Mbps]", dl_list)
        plot_multi_flow_single_metric(this_output_dir, cca, "delivered_rate_mbps", "Throughput [Mbps]", dl_list)
        plot_multi_flow_single_metric(this_output_dir, cca, "loss_rate_mbps", "Loss rate [Mbps]", dl_list)
        plot_multi_flow_single_metric(this_output_dir, cca, "sent_rate_mbps", "Sent rate [Mbps]", dl_list)


def plot_multi_flow(input_dir, output_dir):
    expr_dirs = set()
    for root, folder, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith('.genericcc'):
                expr_dirs.add(root)
                break

    print(expr_dirs)
    for expr_dir in expr_dirs:
        basename = os.path.basename(expr_dir)
        this_output_dir = os.path.join(output_dir, basename)
        plot_multi_flow_multi_metric(expr_dir, this_output_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input', required=True,
        type=str, action='store',
        help='path to dmesg trace')
    parser.add_argument(
        '-o', '--output', required=True,
        type=str, action='store',
        help='path output directory')
    parser.add_argument(
        '-m', '--multi', action='store_true',
        help='the input path is output of experiment with multiple flows')
    args = parser.parse_args()

    if args.multi:
        assert os.path.isdir(args.input)
        # Only genericcc supported right now
        plot_multi_flow(args.input, args.output)
        return

    if(os.path.isdir(args.input)):
        plot_multi_exp(args.input, args.output, '.dmesg', plot_single_exp)
        plot_multi_exp(args.input, args.output, '.genericcc', plot_single_exp)
    else:
        plot_single_exp(args.input, args.output)


if(__name__ == "__main__"):
    try_except(main)