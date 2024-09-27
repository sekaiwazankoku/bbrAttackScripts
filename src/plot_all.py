import time
import argparse
import os
from typing import Callable, Dict, List
import matplotlib
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import pandas as pd

from common import ONE_PKT_PER_MS_MBPS_RATE, is_float, parse_exp, MM_PKT_SIZE, try_except_wrapper, CCA_RENAME, ENTRY_NUMBER
from parse_iperf import parse_iperf_summary
from parse_mahimahi import PKT_SIZE, MahimahiLog

from pubplot import Document
from plot_config.figure_type_creator import FigureTypeCreator as FTC


ftc = FTC(paper_use_small_font=True, use_markers=True)  # , num_entries=20)
doc: Document = ftc.get_figure_type()
ftc2 = FTC(pub_type='presentation', use_markers=True)
ppt = ftc2.get_figure_type()

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
EXPERIMENTS_PATH = os.path.join(SCRIPT_DIR, "../")

FIG_SIZE = None  # (3.5, 3)
BIG = 8
SMALL = 8

update_sizes = {
    'font.size': SMALL,
    'axes.titlesize': BIG,
    'axes.labelsize': SMALL,
    'legend.fontsize': SMALL,
    'legend.title_fontsize': BIG,
    'xtick.labelsize': SMALL,
    'ytick.labelsize': SMALL,
    'pdf.fonttype': 42,
    'font.family': 'sans-serif',
    "grid.linewidth": 0.6,
    "grid.linestyle": '--'
}

plt.rcParams.update(update_sizes)

MARKERS = ['^', '*', 'D', 'x', 'o', 's', '.'] * 5

class MyLogFormatter(tck.LogFormatter):
    def _num_to_string(self, x, vmin, vmax):
        if x > 10000:
            s = '%1.0e' % x
        elif x < 1:
            s = '{:g}'.format(x)  # '%1.0e' % x
        else:
            s = self._pprint_val(x, vmax - vmin)
        return s


def parse_mm_log(fpath):
    ml = MahimahiLog(fpath, summary_only=True)
    return ml.summary


def check_and_derive(data: Dict):
    # import ipdb; ipdb.set_trace()
    if('queue_size_bytes' in data):
        assert data['queue_size_bytes'] == data['buf_size_bytes']


def parse_all_data(DATA_PATH: str):
    all_data = []
    start_time = time.time()
    for root, _, files in os.walk(DATA_PATH):

        current_time = time.time()
        if(current_time - start_time > 5):
            print(f"Processed {len(all_data)} runs...")
            start_time = current_time

        exp_files = [f for f in files
                     if f.endswith('.json') or f.endswith('.log')]
        exp_tags = {f.removesuffix('.json').removesuffix('.log')
                    for f in exp_files}

        for exp_tag in exp_tags:
            iperf_path = os.path.join(root, exp_tag + '.json')
            mm_log_path = os.path.join(root, exp_tag + '.log')
            data = {}
            data.update(parse_exp(exp_tag))
            if (os.path.exists(iperf_path)):
                data.update(parse_iperf_summary(iperf_path))
            assert os.path.exists(mm_log_path)
            data.update(parse_mm_log(mm_log_path))
            check_and_derive(data)
            all_data.append(data)

    return pd.DataFrame(all_data)


def plot_figure(fpath: str, plot_function: Callable, *args, **kwargs):
    fig, ax = plt.subplots(figsize=FIG_SIZE)

    plot_function(fig, ax, *args, **kwargs)

    fig.set_tight_layout({'pad': 0.3})
    fig.savefig(fpath, dpi=300)
    plt.close(fig)


def plot_vary(fig: Figure, ax: Axes, df: pd.DataFrame,
              scheme_key: str, x_key: str, y_key: str,
              xlabel="", ylabel="", ytransform=lambda x: x,
              ylim=(None, None), yscale='linear'):

    schemes = sorted(df[scheme_key].unique())
    for i, scheme in enumerate(schemes):
        scheme_df = df[df[scheme_key] == scheme].sort_values(by=[x_key])
        # Tue Seminar Fall 2022 Figure
        # if(scheme not in ['bbr', 'cubic', 'reno', 'rocc']):
        #    continue
        # if(scheme == 'rocc'):
        #     scheme = 'rocc*'
        color = ftc.colors[ENTRY_NUMBER[scheme]]
        marker = ftc.marker_map[color]

        ax.plot(scheme_df[x_key], ytransform(scheme_df[y_key]), label=CCA_RENAME[scheme],
                linestyle='--', marker=marker, color=color)

    ax.grid(True)
    ax.set_xscale('log', base=2)
    ax.set_ylim(ylim[0], ylim[1])
    ax.set_yscale(yscale)
    # ax.xaxis.set_major_formatter(tck.FormatStrFormatter('%g'))
    # ax.xaxis.set_minor_formatter(tck.ScalarFormatter())
    # formatter = tck.LogFormatter(labelOnlyBase=False,
    #                              minor_thresholds=(2, 0.4))
    # formatter = MyLogFormatter(labelOnlyBase=False,
    #                            minor_thresholds=(2, 1))
    # ax.xaxis.set_minor_formatter(formatter)
    # ax.xaxis.set_minor_locator(tck.AutoMinorLocator())
    ax.minorticks_on()

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    legend = ax.legend()
    legend.set_frame_on(False)


@try_except_wrapper
def plot_groups(fpath: str, df: pd.DataFrame, group_key_list: List[str],
                scheme_key: str, x_key: str, y_key: str,
                xlabel="", ylabel="", ytransform=lambda x: x, figsize=(3.48, 3.5), yscale='linear'):
    if (len(group_key_list) == 0):
        return

    # import ipdb; ipdb.set_trace()

    num_groups = df.groupby(group_key_list).count().shape[0]
    pdt = 1
    for gk in group_key_list:
        pdt *= len(df[gk].unique())
    if num_groups != pdt:
        return
    if(len(group_key_list) > 2):
        return

    cols = len(df[group_key_list[0]].unique())
    rows = 1 if len(group_key_list) == 1 else len(df[group_key_list[1]].unique())

    group_rename = {
        'rate': 'C',
        'delay': 'R_m'
    }

    group_units = {
        'rate': 'Mbps',
        'delay': 'msec'
    }

    group_transform = {
        'rate': lambda x: x*12,
        'delay': lambda x: x*2
    }

    use_doc = ppt

    with matplotlib.rc_context(use_doc.style):
        fig, axes = plt.subplots(rows, cols, sharex=True, sharey=True, figsize=(9, 6))
        row = 0
        col = 0
        for group_key, group_df in sorted(df.groupby(group_key_list)):
            ax = axes[row, col] if len(group_key_list) == 2 else axes[col]
            plot_vary(fig, ax, group_df, scheme_key, x_key,
                    y_key, xlabel, ylabel, ytransform,
                    ylim=(0, ytransform(df[y_key]).max()), yscale=yscale)
            ax.label_outer()
            run_config_list = []
            for i in range(len(group_key_list)):
                param = group_rename[group_key_list[i]]
                units = group_units[group_key_list[i]]
                value = int(group_transform[group_key_list[i]](group_key[i]))
                run_config = f"${param} = {value}$ {units}"
                run_config = f"{value}"
                run_config_list.append(run_config)
            ax.set_title("$\\langle" + ", ".join(run_config_list) + "\\rangle$", fontsize=use_doc.footnotesize)
            # ax.set_title(", ".join(
            #     [f"{group_key_list[i]}={[group_key[i]]}"
            #     for i in range(len(group_key_list))]))
            ax.legend().set_visible(False)

            col = (col + 1) % cols
            if(col == 0):
                row += 1
        if(len(axes[-1, :]) == 3):
            axes[-1, 0].set_xlabel(None)
            axes[-1, 2].set_xlabel(None)
            axes[0, 0].set_ylabel(None)
            axes[2, 0].set_ylabel(None)
            # axes[0, 1].legend(loc='lower center', bbox_to_anchor=(0.5, 1), ncol=3)

        # if(len(group_key_list) == 2):
        #     legend =  axes[-1, -1].legend()
        # else:
        #     legend = axes[-1].legend()
        # # legend.set_frame_on(False)
        h, l = axes[-1, -1].get_legend_handles_labels()
        legend = fig.legend(h, l, loc='lower center', bbox_to_anchor=(0.5, 1), ncol=3)

        # fig.set_tight_layout({'pad': 0.3})
        fig.set_tight_layout({'pad': 0.1})
        fig.savefig(fpath, bbox_inches='tight', pad_inches=0.01)
        plt.close(fig)


def plot_group(df, FIGS_PATH):
    rate = int(df['rate'].unique()[0])
    delay = int(df['delay'].unique()[0])

    figs_path = os.path.join(FIGS_PATH, f'rate[{rate}]-delay[{delay}]')
    os.makedirs(figs_path, exist_ok=True)

    rate_ylim = (0, ONE_PKT_PER_MS_MBPS_RATE * rate)
    delay_ylim = (0, ONE_PKT_PER_MS_MBPS_RATE * delay)
    origin = (0, None)

    # # Throughput
    # plot_figure(os.path.join(figs_path, 'iperf_throughput.png'),
    #             plot_vary, df, 'cca', 'buf_size', 'bits_per_second',
    #             'Buffer size [BDP, log scale]', 'Throughput [Mbps]',
    #             ytransform=lambda x: x/1e6, ylim=origin)

    # # Delay
    # plot_figure(os.path.join(figs_path, 'iperf_mean_rtt.png'),
    #             plot_vary, df, 'cca', 'buf_size', 'mean_rtt',
    #             'Buffer size [BDP, log scale]', 'Mean RTT [msec]',
    #             ytransform=lambda x: x/1e3, ylim=origin)

    # plot_figure(os.path.join(figs_path, 'iperf_max_rtt.png'),
    #             plot_vary, df, 'cca', 'buf_size', 'max_rtt',
    #             'Buffer size [BDP, log scale]', 'Max RTT [msec]',
    #             ytransform=lambda x: x/1e3, ylim=origin)

    # plot_figure(os.path.join(figs_path, 'iperf_min_rtt.png'),
    #             plot_vary, df, 'cca', 'buf_size', 'min_rtt',
    #             'Buffer size [BDP, log scale]', 'Min RTT [msec]',
    #             ytransform=lambda x: x/1e3, ylim=origin)

    # plot_figure(os.path.join(figs_path, 'iperf_retransmits.png'),
    #             plot_vary, df, 'cca', 'buf_size', 'retransmits',
    #             'Buffer size [BDP, log scale]', '# Retransmissions',
    #             ylim=(0, None))

    # plot_figure(os.path.join(figs_path, 'iperf_retransmits_per_Rm.png'),
    #             plot_vary, df, 'cca', 'buf_size', 'retransmits_per_Rm',
    #             'Buffer size [BDP, log scale]', '# Retransmissions per Rm',
    #             ylim=(0, None))

    if ('lost_bytes' in df.columns):
        plot_figure(os.path.join(figs_path, 'mm_lost_pkts_per_Rm.png'),
                    plot_vary, df, 'cca', 'buf_size', 'lost_pkts_per_Rm',
                    'Buffer size [BDP, log scale]', 'Lost packets per Rm',
                    ylim=(0, None))

        plot_figure(os.path.join(figs_path, 'mm_lost_bytes.png'),
                    plot_vary, df, 'cca', 'buf_size', 'lost_bytes',
                    'Buffer size [BDP, log scale]', 'Lost bytes',
                    ylim=(0, None))

    if ('mm_throughput_mbps' in df.columns):
        plot_figure(os.path.join(figs_path, 'mm_throughput_mbps.png'),
                    plot_vary, df, 'cca', 'buf_size', 'mm_throughput_mbps',
                    'Buffer size [BDP, log scale]', 'Throughput [Mbps]',
                    ylim=origin)
        # mm_queue_min
        plot_figure(os.path.join(figs_path, 'mm_queue_min.png'),
                    plot_vary, df, 'cca', 'buf_size', 'mm_queue_min',
                    'Buffer size [BDP, log scale]', 'Min queue [BDP]',
                    ylim=(0, None))

        plot_figure(os.path.join(figs_path, 'mm_queue_max.png'),
                    plot_vary, df, 'cca', 'buf_size', 'mm_queue_max',
                    'Buffer size [BDP, log scale]', 'Max queue [BDP]',
                    ylim=(0, None))

        plot_figure(os.path.join(figs_path, 'mm_queue_mean.png'),
                    plot_vary, df, 'cca', 'buf_size', 'mm_queue_mean',
                    'Buffer size [BDP, log scale]', 'Mean queue [BDP]',
                    ylim=(0, None))

    # import ipdb; ipdb.set_trace()


def plot_paper(outpath, df: pd.DataFrame):
    # df = df[df['buf_size'] >= 0.125]
    # fig, [ax1, ax2] = plt.subplots(1, 2)
    # fig, [ax1, ax2] = doc.subfigures(1, 2, yscale=1.4)
    # fig, [ax1, ax2] = ppt.subfigures(1, 2, yscale=1.4)
    fig, [ax1, ax2] = ppt.subfigures(1, 2, xscale=0.8, yscale=1.4*0.8)
    MARKER_SIZE = 5**2  # paper
    MARKER_SIZE = 5**3.5  # ppt

    # Subplot 1
    fdf = df[(df['cca'] == 'genericcc_fast_conv') | (df['cca'] == 'bbr') | (df['cca'] == 'genericcc_slow_conv_3') | (df['cca'] == 'cubic') | (df['cca'] == 'genericcc_markovian') | (df['cca'] == 'bbr3')]
    agg_df = fdf.groupby('cca').agg({'mm_utilization_except_ss': 'min', 'mm_queue_max_except_ss': 'max'}).reset_index()
    for (i, row) in agg_df.iterrows():
        c = ftc.colors[ENTRY_NUMBER[row['cca']]]
        marker = ftc.marker_map[c]
        ax1.scatter(row['mm_queue_max_except_ss'], 100 * row['mm_utilization_except_ss'],
                    label=CCA_RENAME[row['cca']], marker=marker, color=c, s=MARKER_SIZE, linewidget=0.5)
    ax1.set_xlabel('Max peak queue [BDP]')
    ax1.set_ylabel('Min avg utilization [\%]')
    ax1.set_ylim(0, 100)
    # ax1.legend()
    # ax1.grid(True)

    # Subplot 2
    # fdf = df[(df['cca'] == 'bbr') | (df['cca'] == 'genericcc_slow_conv')]
    # fdf = df[(df['cca'] == 'genericcc_fast_conv') | (df['cca'] == 'bbr') | (df['cca'] == 'genericcc_slow_conv_3')]
    fdf = df[(df['cca'] == 'genericcc_fast_conv') | (df['cca'] == 'bbr') | (df['cca'] == 'genericcc_slow_conv_3') | (df['cca'] == 'cubic') | (df['cca'] == 'genericcc_markovian') | (df['cca'] == 'bbr3')]
    # fdf = df[(df['cca'] == 'bbr') | (df['cca'] == 'genericcc_slow_conv_3')]
    fdf = fdf[fdf['buf_size'] <= 1]
    fdf = fdf.sort_values(by=['bdp_bytes', 'lost_pkts_per_Rm_except_ss'])
    # import ipdb; ipdb.set_trace()
    for group, group_df in fdf.groupby('cca'):
        # xx = group_df['bdp_bytes']/PKT_SIZE
        # yy = group_df['lost_pkts_per_Rm_except_ss']
        gdf = group_df[['bdp_bytes', 'lost_pkts_per_Rm_except_ss']].groupby('bdp_bytes').mean().reset_index()
        xx = gdf['bdp_bytes']/PKT_SIZE
        yy = gdf['lost_pkts_per_Rm_except_ss']
        c = ftc.colors[ENTRY_NUMBER[group]]
        ax2.scatter(xx, yy, label='__no_label__',  # CCA_RENAME[group],
                    color=c, marker=ftc.marker_map[c], s=MARKER_SIZE, linewidths=0.5)
        # ax2.plot(xx, yy, label='__no_label__',  # CCA_RENAME[group],
        #          color=c, marker=ftc.marker_map[c])
    ax2.set_xlabel('BDP [Packets, $\log_{10}$]')
    ax2.set_ylabel('Avg pkts lost per $R_m$')
    ax2.set_xscale('log')
    # ax2.legend()
    # ax2.grid()
    ax2.set_yscale('symlog')
    ax2.set_ylim(0, None)
    fig.set_tight_layout({'pad': 0.1, 'w_pad': 0.5})

    legend = fig.legend(bbox_to_anchor=(0.5, 1), loc='lower center', ncol=3)

    fig.savefig(os.path.join(outpath), bbox_inches='tight', pad_inches=0.03)


@try_except_wrapper
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input', required=True,
        type=str, action='store',
        help='directory storing data files used to plot.')
    parser.add_argument(
        '-o', '--output', required=True,
        type=str, action='store',
        help='directory path where plots should be stored')
    parser.add_argument(
        '--group', action='store_true'
    )
    parser.add_argument(
        '--paper', action='store_true'
    )
    args = parser.parse_args()

    DATA_PATH = args.input
    FIGS_PATH = args.output

    df = parse_all_data(DATA_PATH)
    df = df[df['cca'] != 'genericcc_slow_conv']
    os.makedirs(FIGS_PATH, exist_ok=True)

    if(args.paper):
        plot_paper(os.path.join(FIGS_PATH, 'empirical-util_qdel_loss.svg'), df)
        return

    # df = df[df['cca'] != 'fast_conv']
    if(args.group):
        # plot_groups(os.path.join(FIGS_PATH, 'throughput-summary.png'),
        #             df, ['rate', 'delay'], 'cca', 'buf_size', 'bits_per_second',
        #             'Buffer size [BDP, log scale]', 'Throughput [Mbps]',
        #             ytransform=lambda x: x/1e6)

        # plot_groups(os.path.join(FIGS_PATH, 'utilization-summary.png'),
        #             df, ['rate', 'delay'], 'cca', 'buf_size', 'utilization',
        #             'Buffer size [BDP, log scale]', 'Utilization %',
        #             ytransform=lambda x: x*100)

        # plot_groups(os.path.join(FIGS_PATH, 'retransmits_per_Rm-summary.png'),
        #             df, ['rate', 'delay'], 'cca', 'buf_size', 'retransmits_per_Rm',
        #             'Buffer size [BDP, log scale]', '# Rtx per Rm')

        plot_groups(os.path.join(FIGS_PATH, 'mm_throughput-summary.png'),
                    df, ['rate', 'delay'], 'cca', 'buf_size', 'mm_throughput_mbps',
                    'Buffer size [BDP, $\\log_2$]', 'Throughput [Mbps]')

        plot_groups(os.path.join(FIGS_PATH, 'mm_utilization-summary.png'),
                    df, ['rate', 'delay'], 'cca', 'buf_size', 'mm_utilization',
                    'Buffer size [BDP, $\\log_2$]', 'Utilization [\%]',
                    ytransform=lambda x: x*100)

        plot_groups(os.path.join(FIGS_PATH, 'mm_utilization_except_ss-summary.pdf'),
                    df, ['rate', 'delay'], 'cca', 'buf_size', 'mm_utilization_except_ss',
                    'Buffer size [BDP, $\\log_2$]', 'Avg utilization [\%]',
                    ytransform=lambda x: x*100)

        filter_df = df[df['cca'] != 'genericcc_fast_conv']
        yscale='linear'
        ylabel='Avg \# pkts lost per Rm'
        # filter_df = df
        # yscale='symlog'
        # ylabel='Avg \# pkts lost per Rm [$\\symlog_{10}$]'
        plot_groups(os.path.join(FIGS_PATH, 'mm_lost_pkts_per_Rm-summary.png'),
                    filter_df, ['rate', 'delay'], 'cca', 'buf_size', 'lost_pkts_per_Rm',
                    'Buffer size [BDP, $\\log_2$]', 'Avg. pkts lost per $R_m$')

        plot_groups(os.path.join(FIGS_PATH, 'mm_lost_pkts_per_Rm_except_ss-summary.pdf'),
                    filter_df, ['rate', 'delay'], 'cca', 'buf_size', 'lost_pkts_per_Rm_except_ss',
                    'Buffer size [BDP, $\\log_2$]', ylabel, figsize=(3.33, 3.5), yscale=yscale)

        plot_groups(os.path.join(FIGS_PATH, 'mm_queue_min-summary.png'),
                    df, ['rate', 'delay'], 'cca', 'buf_size', 'mm_queue_min',
                    'Buffer size [BDP, $\\log_2$]', 'Min queue [BDP]')

        plot_groups(os.path.join(FIGS_PATH, 'mm_queue_max-summary.png'),
                    df, ['rate', 'delay'], 'cca', 'buf_size', 'mm_queue_max',
                    'Buffer size [BDP, $\\log_2$]', 'Peak queue [BDP]')

        plot_groups(os.path.join(FIGS_PATH, 'mm_queue_max_except_ss-summary.pdf'),
                    df, ['rate', 'delay'], 'cca', 'buf_size', 'mm_queue_max_except_ss',
                    'Buffer size [BDP, $\\log_2$]', 'Peak queue [BDP]')

        plot_groups(os.path.join(FIGS_PATH, 'mm_queue_mean-summary.png'),
                    df, ['rate', 'delay'], 'cca', 'buf_size', 'mm_queue_mean',
                    'Buffer size [BDP, $\\log_2$]', 'Mean queue [BDP]')

    else:
        for group, group_df in df.groupby(['rate', 'delay']):
            plot_group(group_df, FIGS_PATH)


if (__name__ == '__main__'):
    main()