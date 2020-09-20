"""Modules related to three dimensions"""
from manimlib.imports import *


class PointCloud(VGroup):
    def __init__(self, xs, ys, zs, ss, opacity=1):
        super().__init__()
        dots = []
        for x,y,z,s in zip(xs, ys, zs, ss):
            dots.append(
                Dot(fill_opacity=opacity).move_to(
                    x*OUT+y*UP+z*RIGHT
                ).scale(s)
            )
        self.add(dots)
