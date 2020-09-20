"""Line related modules"""
from manimlib.imports import *


def p2refp(p, xaxis=None, yaxis=None):
    """Get reference points on axes

    """
    if yaxis is None or xaxis is None:
        dy = p[1]*UP
        dx = p[0]*RIGHT
    else:
        xref = xaxis.copy().shift(p)
        yref = yaxis.copy().shift(p)
        dx = line_intersection(xaxis.get_start_and_end(), yref.get_start_and_end())
        dy = line_intersection(yaxis.get_start_and_end(), xref.get_start_and_end())
    return dx, dy
