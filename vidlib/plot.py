from manimlib import *

import numpy as np
from scipy import interpolate as sinterp

from vidlib.utils import *


class MyAxes(Axes):
    """An Axes class that works more like plt.axes"""
    CONFIG = {
        "axis_config": {
            "include_tip": True,
            "numbers_to_exclude": [0],
            "color": BLACK
        }
    }
    def plot(self, x, y, fmt='-', c=None, alpha=None, x_range=None, **kwargs):
        if fmt == '-':
            f = sinterp.interp1d(x, y, kind='cubic')
            if x_range is None: x_range = [min(x), max(x)]
            if c: kwargs['color'] = c2hex(c)
            if alpha: kwargs['stroke_opacity'] = alpha
            return self.get_graph(f, x_range=x_range, **kwargs)
        else:
            raise NotImplemented
    def loglog(self, x, y, **kwargs):
        return self.plot(np.log10(x), np.log10(y), **kwargs)

    def set_xlabel(self, label, **kwargs):
        return self.get_x_axis_label(label, edge=DOWN, direction=DOWN, **kwargs)

    def set_ylabel(self, label, **kwargs):
        return self.get_y_axis_label(label, edge=LEFT, direction=LEFT, rotate=90, **kwargs)

    def get_axis_label(self, label_tex, axis, edge, direction, buff=MED_SMALL_BUFF, rotate=0, **kwargs):
        label = Tex(label_tex, **kwargs)
        if rotate: label.rotate(rotate*DEGREES)
        label.next_to(
            axis.get_edge_center(edge), direction,
            buff=buff
        )
        label.shift_onto_screen(buff=MED_SMALL_BUFF)
        return label


class MplAxisWrapper(CoordinateSystem, VGroup):
    CONFIG = {
        "height": FRAME_HEIGHT - 2,
        "width": FRAME_WIDTH - 2,
        "tick_direction": "out",
        "npl": 200  # number of points per line
    }
    def __init__(self, ax, **kwargs):
        """Take an mpl axis instance to produce a VGroup that look like it
        """
        super().__init__(**kwargs)

        # make x-axis
        self._ax = ax
        xlim = ax.get_xlim()
        xmajorticks = filter_by_lim(np.array(ax.get_xaxis().get_majorticklocs()), xlim)  # major ticks
        xminorticks = filter_by_lim(np.array(ax.get_xaxis().get_minorticklocs()), xlim)
        # combine ticks
        xticks = np.sort(np.concatenate([xmajorticks, xminorticks]))
        xaxis = MyNumberLine(xticks=xticks, x_range=xlim, width=self.width,
                             numbers_with_elongated_ticks=xmajorticks,
                             xscale=ax.get_xscale(), numbers_to_exclude=xminorticks,
                             tick_direction=self.tick_direction)
        xaxis.shift(-xaxis.n2p(xlim[0]))
        self.xlim  = xlim
        self.xaxis = xaxis

        # make y-axis
        ylim = ax.get_ylim()
        ymajorticks = filter_by_lim(np.array(ax.get_yaxis().get_majorticklocs()), ylim)  # major ticks
        yminorticks = filter_by_lim(np.array(ax.get_yaxis().get_minorticklocs()), ylim)
        yminorticks = filter_by_lim(yminorticks, ylim)
        # combine ticks
        yticks = np.sort(np.concatenate([ymajorticks, yminorticks]))
        yaxis = MyNumberLine(xticks=yticks, x_range=ylim, width=self.height,
                             line_to_number_direction=UP,
                             numbers_with_elongated_ticks=ymajorticks,
                             xscale=ax.get_yscale(), numbers_to_exclude=yminorticks,
                             tick_direction=self.tick_direction)
        yaxis.shift(-yaxis.n2p(ylim[0]))
        yaxis.rotate(90 * DEGREES, about_point=ORIGIN)
        self.ylim  = ylim
        self.yaxis = yaxis
        self.axes = VGroup(xaxis, yaxis)
        self.add(*self.axes)

        # parse x,y labels
        self.xlabel = self.get_x_axis_label(ax.get_xlabel(),
                                            edge=DOWN, direction=DOWN, color=BLACK)
        self.ylabel = self.get_y_axis_label(ax.get_ylabel(),
                                            edge=LEFT, direction=LEFT, rotate=90, color=BLACK)
        self.add(self.xlabel, self.ylabel)

        # parse lines
        lines = []
        for line in ax.get_lines():
            # import ipdb; ipdb.set_trace()
            line_color = line.get_color()
            line_x, line_y = line.get_data()
            t = np.linspace(0, 1, len(line_x))
            # import ipdb; ipdb.set_trace()
            _, mask_x = filter_by_lim(line_x, xlim, return_mask=True)
            _, mask_y = filter_by_lim(line_y, ylim, return_mask=True)
            line_x = line_x[mask_x * mask_y]
            line_y = line_y[mask_x * mask_y]
            t = t[mask_x * mask_y]
            fx = sinterp.interp1d(t, line_x, kind='cubic')
            fy = sinterp.interp1d(t, line_y, kind='cubic')
            # line_x = line_x[mask_x*mask_y]
            # line_y = line_y[mask_x*mask_y]
            t = np.linspace(0, 1, len(line_x))
            fx = sinterp.interp1d(t, line_x, kind='cubic')
            fy = sinterp.interp1d(t, line_y, kind='cubic')
            graph = ParametricCurve(
                lambda t: self.c2p(fx(t), fy(t)),
                t_range=[0, 1, 1/self.npl],
                color=line_color,
            )
            lines.append(graph)
        self.lines = VGroup(*lines)
        self.add(self.lines)
        self.center()

    def get_axis_label(self, label_tex, axis, edge, direction, buff=MED_SMALL_BUFF, rotate=0, **kwargs):
        label = Tex(label_tex, **kwargs)
        if rotate: label.rotate(rotate*DEGREES)
        label.next_to(
            axis.get_edge_center(edge), direction,
            buff=buff
        )
        label.shift_onto_screen(buff=MED_SMALL_BUFF)
        return label

    def get_axes(self):
        return self.axes

    def coords_to_point(self, *coords):
        origin = self.xaxis.number_to_point(self.xlim[0])
        result = origin.copy()
        for axis, coord in zip(self.get_axes(), coords):
            result += (axis.number_to_point(coord) - origin)
        return result

    def point_to_coords(self, point):
        return tuple([
            axis.point_to_number(point)
            for axis in self.get_axes()
        ])


class MyNumberLine(NumberLine):
    CONFIG = {
        "color": BLACK,
        "tick_direction": "out",
        "xticks": None,
        "xscale": 'linear',
        "include_tip": True,
        "include_numbers": True,
        "tick_size": 0.025,
        "longer_tick_multiple": 2,
        "decimal_number_config": {
            "num_decimal_places": 0,
            "font_size": 24,
            "color": BLACK,
        },
        "tip_config": {
            "width": 0.1,
            "length": 0.1,
        },
        "line_to_number_direction": DOWN,
    }

    def get_tick_range(self):
        return self.xticks

    def get_tick(self, x, size=None, direction=None):
        if size is None:
            size = self.tick_size
        if not direction: direction = self.tick_direction
        result = Line(size * DOWN, size * UP)
        if direction == 'inout':
            offset = 0
        elif direction == 'in':
            offset = -size * self.line_to_number_direction
        elif direction == 'out':
            offset = size * self.line_to_number_direction
        result.rotate(self.get_angle())
        result.move_to(self.number_to_point(x) + offset)
        result.match_style(self)
        return result

    def number_to_point(self, number):
        if self.xscale == 'linear':
            alpha = float(number - self.x_min) / (self.x_max - self.x_min)
        elif self.xscale == 'log':
            alpha = (np.log10(number)-np.log10(self.x_min))/(np.log10(self.x_max)-np.log10(self.x_min))
        else: raise NotImplemented
        return interpolate(self.get_start(), self.get_end(), alpha)

    def point_to_number(self, point):
        start, end = self.get_start_and_end()
        unit_vect = normalize(end - start)
        proportion = fdiv(
            np.dot(point - start, unit_vect),
            np.dot(end - start, unit_vect),
        )
        if self.xscale == 'linear':
            return interpolate(self.x_min, self.x_max, proportion)
        elif self.xscale == 'log':
            return 10**(interpolate(np.log10(self.x_min), np.log10(self.x_max), proportion))

    def get_unit_size(self):
        if self.xscale == 'linear':
            return self.get_length() / (self.x_max - self.x_min)
        elif self.xscale == 'log':
            return self.get_length() / (np.log(self.x_max) - np.log(self.x_min))
