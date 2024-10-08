from typing import Any, Dict, Literal, Union

import seaborn as sns
from cycler import cycler
from pubplot import Document
from pubplot.document_classes import usenix

from .util import in2pt

# https://scottplot.net/cookbook/4.1/colors/#category-10
# https://www.nature.com/articles/nmeth.1618.pdf
wong_color_palette = [
    '#000000',
    '#E69F00',
    '#56B4E9',
    '#009E73',
    '#F0E442',
    '#0072B2',
    '#D55E00',
    '#CC79A7',
]


class FigureTypeCreator():
    """
    Good colors:
    > sns.color_palette("colorblind")
    > sns.color_palette("tab10")
    > palettable.colorbrewer.qualitative.Paired_12.hex_colors
    https://seaborn.pydata.org/tutorial/color_palettes.html
    """

    """
    Note: I use sns.color_palette("tab10") as the default color scheme. I am
    not colorblind, but I can't differentiate between some of the colorblind
    colors (or they are very hard to see on white background), whereas I can
    differentiate tab10. Optimize for common case, most people aren't
    colorblind. I will have linestyles/markers/hatches anyway, so hopefully
    isn't a big concern.
    """

    """
    TODO: consider building a document class based on
    https://www.overleaf.com/learn/latex/Beamer
    """

    def __init__(self,
                 pub_type: Union[Literal['paper'],
                                 Literal['presentation']] = 'paper',
                 document_class=usenix,
                 colors=sns.color_palette('tab10'),
                 use_markers: bool = False,
                 use_grid: bool = True,
                 paper_use_small_font: bool = False,
                 num_entries: int = 10
                 ):

        self.pub_type = pub_type
        self.document_class = document_class
        self.num_entries = num_entries
        self.use_markers = use_markers
        self.use_grid = use_grid
        self.paper_use_small_font = paper_use_small_font
        self.colors = list(colors)[:self.num_entries]  # type:ignore
        self.num_entries = len(self.colors)

        # https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html
        # The permutation is based on best visuals with wong colors
        # I don't include dotted as that is hard to see.
        available_linestyles = ['solid', 'dashdot', 'dashed']
        self.linestyles = self.get_entries(
            available_linestyles, self.num_entries)

        # https://matplotlib.org/stable/api/markers_api.html
        available_markers = ['o', '^', 's', '*', 'X', 'd']
        self.markers = self.get_entries(available_markers, self.num_entries)

        # https://matplotlib.org/stable/gallery/shapes_and_collections/hatch_style_reference.html
        available_hatches = ['', '//', '\\\\', '||', '--', '++', 'xx']
        self.hatches = self.get_entries(available_hatches, self.num_entries)

        # Map from colors to hatches, markers and line styles
        # Useful when using manual colors for lines/objects
        colors = self.colors
        self.hatch_map = {colors[i]: hatch for i,
                          hatch in enumerate(self.hatches)}
        self.marker_map = {colors[i]: marker for i,
                           marker in enumerate(self.markers)}
        self.ls_map = {colors[i]: ls for i, ls in enumerate(self.linestyles)}

    @staticmethod
    def get_entries(cycle_list, num_entries):
        n = len(cycle_list)
        m = int(num_entries / n) + 1
        return (cycle_list * m)[:num_entries]

    def get_cycler(self):
        cycling = (cycler('color', self.colors)
                   + cycler('ls', self.linestyles))
        if(self.use_markers):
            cycling += cycler('marker', self.markers)
        return cycling

    def get_figure_type(self, *args, **kwargs):
        style = {
            # Conferences require this.
            'pdf.fonttype': 42,
            # https://matplotlib.org/stable/tutorials/intermediate/tight_layout_guide.html
            # There are bugs/caveats in this parameter ^^
            # 'figure.autolayout': True,

            # Use for each figure:
            # fig.set_layout_engine('tight', pad=0.3)  # newer api TODO verify.
            # fig.set_tight_layout({'pad': 0.3})
            # Use smallest padding that works? matplotlib recommands > 0.3.

            'axes.prop_cycle': self.get_cycler(),
        }
        style.update(self.get_custom_style())
        style.update(self.get_line_sizes())
        style.update(self.get_font_sizes())
        doc = Document(self.document_class, style=style, *args, **kwargs)

        self.presentation_config(doc)
        self.paper_small_font(doc)

        return doc

    def get_custom_style(self):
        ret= {
            # https://matplotlib.org/3.5.1/gallery/ticks/auto_ticks.html
            # 'axes.xmargin': 0,
            # 'axes.ymargin': 0,
            # 'axes.autolimit_mode': 'round_numbers'
        }
        if(self.pub_type == 'paper'):
            ret.update({
                'xtick.minor.visible': True,
                'ytick.minor.visible': True,
            })

        return ret

    def get_line_sizes(self):
        ret: Dict[str, Any] = {}

        if(self.use_grid):
            ret.update(
                {
                    "axes.grid": True,
                    "grid.linestyle": '--'
                })

        if(self.pub_type == 'paper'):
            ret.update({
                'axes.linewidth': 0.5,
                'xtick.major.width': 0.5,
                'ytick.major.width': 0.5,

                'xtick.minor.width': 0.4,
                'ytick.minor.width': 0.4,

                'lines.linewidth': 1,  # 0.8
                'lines.markersize': 3,
                'lines.markeredgewidth': 0.5,
                'legend.handlelength': 2.5,

                'hatch.linewidth': 0.5,

                "grid.linewidth": 0.25,
            })

        elif(self.pub_type == 'presentation'):
            ret.update({
                'axes.linewidth': 1.5,
                'xtick.major.width': 1.5,
                'ytick.major.width': 1.5,

                'xtick.minor.width': 1,
                'ytick.minor.width': 1,

                'lines.linewidth': 2.5,
                # 'lines.markersize': 1.5,
                # 'legend.handlelength': 2.5,

                # 'hatch.linewidth': 0.5,

                'grid.linewidth': 1,

                'xtick.major.size': 8,
                'xtick.minor.size': 4,
                'ytick.major.size': 8,
                'ytick.minor.size': 4,
            })
        else:
            raise NotImplementedError

        return ret

    def get_font_sizes(self):
        ret: Dict[str, Any] = {
            'font.family': 'sans-serif',
            'text.latex.preamble':
                "\n".join(
                    [r'\usepackage[cm]{sfmath}',
                     r'\usepackage{amsmath}']),
        }

        # For paper, pubplot automatically sets the appropriate font sizes.

        if(self.pub_type == 'presentation'):
            # big_size = 32
            # small_size = 28
            big_size = 28
            small_size = 24
            ret.update({
                'font.size': big_size,
                'axes.titlesize': big_size,
                'axes.labelsize': big_size,
                'legend.fontsize': small_size,
                'legend.title_fontsize': big_size,
                'xtick.labelsize': small_size,
                'ytick.labelsize': small_size,
            })
        return ret

    def presentation_config(self, doc: Document):
        if(self.pub_type == 'presentation'):
            # Used for setting figure sizes
            ppt_sizes = {
                # The main text box in default ppt layout
                "columnwidth": in2pt(11.5),
                "textwidth": in2pt(11.5)
                # "columnwidth": in2pt(13.33),
                # "textwidth": in2pt(7.5)
            }
            doc.__dict__.update(ppt_sizes)

    def paper_small_font(self, doc: Document):
        if(self.paper_use_small_font):
            assert self.pub_type == 'paper'
            doc.update_style({
                'font.size': doc.footnotesize,
                'axes.titlesize': doc.footnotesize,
                'axes.labelsize': doc.footnotesize,
                'legend.title_fontsize': doc.footnotesize,
                'legend.fontsize': doc.scriptsize,
                'xtick.labelsize': doc.scriptsize,
                'ytick.labelsize': doc.scriptsize
            })
