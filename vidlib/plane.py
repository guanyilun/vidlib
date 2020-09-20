"""This module contains useful planes for physics

"""
from manimlib.imports import *


class BoostPlane(NumberPlane):
    CONFIG = {
        "background_line_style": {
            "stroke_color": BLACK,
            "stroke_width": 2,
            "stroke_opacity": 1,
        },
        "x_min": -10,
        "x_max": 10,
        "y_min": -10,
        "y_max": 10,
        "axis_arrow_size": 6,
        "ylabel": "ct",
        "xlabel": "x"
    }
    def __init__(self, rot=0, **kwargs):
        """Plane used for relativity boosting"""
        Axes.__init__(self, **kwargs)
        self.rot = rot
        self.get_x_axis().rotate(rot, about_point=ORIGIN)
        self.get_y_axis().rotate(-rot, about_point=ORIGIN)
        self.init_background_lines()
        self.init_axes_and_labels()

    def init_axes_and_labels(self):
        # axes and label
        xaxis = self.get_vector((self.axis_arrow_size,0))
        yaxis = self.get_vector((0,self.axis_arrow_size))
        xlabel = TexMobject(self.xlabel).next_to(xaxis, DOWN).shift(3*RIGHT)
        ylabel = TexMobject(self.ylabel).next_to(yaxis, LEFT).shift(3*UP)
        axes = VGroup(xaxis, yaxis, xlabel, ylabel)
        self.add_to_back(axes)
