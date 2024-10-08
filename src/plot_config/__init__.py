import matplotlib.ticker as tck

from .figure_type_creator import FigureTypeCreator


class MyLogFormatter(tck.LogFormatter):
    def _num_to_string(self, x, vmin, vmax):
        if x > 10000:
            s = '%1.0e' % x
        elif x < 1:
            s = '{:g}'.format(x)  # '%1.0e' % x
        else:
            s = self._pprint_val(x, vmax - vmin)
        return s
