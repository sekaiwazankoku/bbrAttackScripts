import pprint
from typing import Callable

import numpy as np
from pubplot.axes import PubAxes

from plot_config.figure_type_creator import FigureTypeCreator


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
        assert False


def try_except_wrapper(function):
    def func_to_return(*args, **kwargs):
        def func_to_try():
            return function(*args, **kwargs)
        return try_except(func_to_try)
    return func_to_return


@try_except_wrapper
def test_paper(pub_type="paper"):
    ftc = FigureTypeCreator(
        pub_type=pub_type,
        # colors=sns.color_palette('tab10'),
        # paper_use_small_font=True'
    )
    doc = ftc.get_figure_type()
    fig, ax = doc.subfigures()
    assert isinstance(ax, PubAxes)

    for n in range(10):
        xx = np.linspace(0, 100, 1000)
        yy = [x * 2 + 50 * n for x in xx]
        ax.plot(xx, yy, label=f"Legend label {n}")
    ax.set_xlabel('X label')
    ax.set_ylabel('Y label')
    # legend = ax.legend(title="Title")
    # legend.set_frame_on(False)

    pprint.pprint(fig.rc.__dict__)
    # ext = "pdf" if pub_type == 'paper' else "png"
    ext = "pdf"
    fig.savefig(f'tmp/{pub_type}.{ext}', bbox_inches='tight', pad_inches=0.01)


if(__name__ == "__main__"):
    test_paper()
    test_paper('presentation')
