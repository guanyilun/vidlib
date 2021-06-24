from manimlib.constants import *

def filter_by_lim(values, lim, return_mask=False):
    if not return_mask:
        return values[(values > lim[0]) * (values < lim[1])]
    else:
        mask = (values > lim[0]) * (values < lim[1])
        return values[mask], mask

def c2hex(c):
    import matplotlib as mpl
    if '#' not in c: return mpl.colors.to_hex(c)
    else: return c

def p2refp(p, xaxis=None, yaxis=None):
    """Get reference points on axes"""
    if yaxis is None or xaxis is None:
        dy = p[1]*UP
        dx = p[0]*RIGHT
    else:
        xref = xaxis.copy().shift(p)
        yref = yaxis.copy().shift(p)
        dx = line_intersection(xaxis.get_start_and_end(), yref.get_start_and_end())
        dy = line_intersection(yaxis.get_start_and_end(), xref.get_start_and_end())
    return dx, dy
