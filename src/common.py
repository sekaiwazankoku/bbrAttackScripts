import os
import matplotlib.pyplot as plt
from typing import Any, Callable, Dict, Literal


# TCP MSS          = 1448 bytes
# Ethernet payload = 1500 bytes (= MSS + 20 [IP] + 32 [TCP])
# https://github.com/zehome/MLVPN/issues/26
# MM_PKT_SIZE      = 1504 bytes (= Ethernet payload + 4 [TUN overhead])
# Ethernet MTU     = 1518 bytes (= Ethernet payload + 18 [Ethernet])
# On the wire      = 1538 bytes (= Ethernet MTU + 20 [Preamble + IPG])

MM_PKT_SIZE = 1504
WIRE = 1538
PKT_TO_WIRE = WIRE / MM_PKT_SIZE
MSEC_PER_SEC = 1000
ONE_PKT_PER_MS_MBPS_RATE = WIRE * 8 * MSEC_PER_SEC / 1e6


def is_float(element: Any) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False


def plot_df(df, ykey, fpath, xkey='time',
            xlabel="", ylabel="",
            yscale: Literal['linear', 'log', 'symlog', 'logit'] = 'linear',
            title=""):
    fig, ax = plt.subplots()
    ax.plot(df[xkey], df[ykey])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_yscale(yscale)
    ax.set_title(title)
    fig.set_tight_layout(True)
    fig.savefig(fpath)
    plt.close(fig)
    # return fig, ax


def parse_exp(exp_tag):
    ret = {}
    for param_tag in exp_tag.split('-'):
        param_name = param_tag.split('[')[0]
        param_val = param_tag.split('[')[1][:-1]
        ret[param_name] = float(param_val) if(is_float(param_val)) else param_val

    bdp_bytes = MM_PKT_SIZE * ret['rate'] * 2 * ret['delay']
    buf_size_bytes = bdp_bytes * ret['buf_size']
    ret['bdp_bytes'] = bdp_bytes
    ret['buf_size_bytes'] = int(buf_size_bytes)

    return ret


def try_except(function: Callable):
    try:
        return function()
    except Exception:
        import sys
        import traceback

        import ipdb
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        ipdb.post_mortem(tb)


def try_except_wrapper(function):
    def func_to_return(*args, **kwargs):
        def func_to_try():
            return function(*args, **kwargs)
        return try_except(func_to_try)
    return func_to_return


def plot_multi_exp(input_dir: str, output_dir: str,
                   ext: str, plot_single_exp: Callable):
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if (filename.endswith(ext)):
                fpath = os.path.join(root, filename)
                dirpath = fpath.replace(ext, '')
                rel_path = os.path.relpath(dirpath, input_dir)
                this_out_dir = os.path.join(output_dir, rel_path)
                plot_single_exp(fpath, this_out_dir)

CCA_RENAME = {
    'bbr': 'BBRv1',
    'cubic': 'Cubic',
    'genericcc_markovian': 'Copa',
    'genericcc_slow_conv': 'cc_probe_slow',
    # 'genericcc_fast_conv': 'cc_qdel',
    'genericcc_fast_conv': 'Synth-LinearLoss',
    'bbr2': 'BBRv2',
    'bbr3': 'BBRv3',
    'genericcc_slow_conv_1': 'cc_probe_slow_1',
    'genericcc_slow_conv_2': 'cc_probe_slow_2',
    # 'genericcc_slow_conv_3': 'cc_probe_slow_3',
    'genericcc_slow_conv_3': 'Synth-ConstLoss',
    # 'genericcc_slow_conv_4': 'man_4',
    # 'genericcc_slow_conv_5': 'man_5',
}

order = [
    'cubic',
    'genericcc_slow_conv_3',
    'genericcc_fast_conv',
    'genericcc_markovian',
    'genericcc_slow_conv_1',
    'genericcc_slow_conv_2',
    'bbr',
    'bbr2',
    'bbr3',
    'genericcc_slow_conv',
]

ENTRY_NUMBER: Dict[str, int] = {
    x: i for i, x in enumerate(order)
}
