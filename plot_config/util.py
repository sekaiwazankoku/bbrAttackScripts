def in2pt(inches):
    return inches * 72.27

# ----------------------------------------------------------------------------
# Deprecated (pubplot manages these now)


def pt2in(pt):
    return pt/72.27


def get_fig_size(col=1, height_frac=1, full=False):
    # https://jwalton.info/Embed-Publication-Matplotlib-Latex/
    width = LATEX_LINE_WIDTH_IN * col
    if(full):
        width = LATEX_TEXT_WIDTH_IN
    height = (width * GOLDEN_RATIO) * height_frac
    return (width, height)


# Constants (two column publication format)
LATEX_TEXT_WIDTH_PT = 505.89
LATEX_TEXT_WIDTH_IN = pt2in(LATEX_TEXT_WIDTH_PT)
LATEX_LINE_WIDTH_PT = 241.02039
LATEX_LINE_WIDTH_IN = pt2in(LATEX_LINE_WIDTH_PT)
GOLDEN_RATIO = (5**.5 - 1) / 2