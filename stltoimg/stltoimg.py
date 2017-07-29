#!/usr/bin/env python

import argparse
import os

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from reportlab.lib.colors import Color
from reportlab.graphics.shapes import Group
from reportlab.graphics.shapes import Polygon


class SVGSmash(object):
    def __init__(self, path):
        """Populate the SVG object"""
        self.target_color = Color(1, 1, 1, 1)
        self.background_color = Color(0, 0, 0, 1)
        self.path = path
        # self.image = <Base greyscale image from PIL>
        self.drawing = svg2rlg(path)

    def process(self, level, color_value = 0.0):
        """
        Process file into output file
        :param level:
        :param color_value:
        :return:
        """
        if isinstance(level, Group) and not any(
                isinstance(x, Polygon) for x in level.contents):
            for child in level.contents:
                self.process(child, color_value + 1)
            return
        for child in level.contents:
            # This should be a polygon
            if child.fillColor == self.target_color:
                gval = float(color_value) / 255.0
                child.fillColor = Color(gval, gval, gval, 1)
        # Process Image here ? After swapping colors

    @property
    def input_fname(self):
        """Return the input file name"""
        return os.path.basename(self.path)

    @property
    def input_ftype(self):
        """Return the file extension of the file"""
        return self.input_fname[-3:]

    @property
    def size(self):
        """Return the size or Bounding Box of the image"""
        return self.drawing.getBounds()


def cmd_ars():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-u', '--unit', help='Select the units of the input file e.x. mm or in')
    parser.add_argument('-a', '--analysis', help='Analyse the input SVG to determine proper layer height')
    parser.add_argument('-d', '--dpi', help='Select the output image DPI e.x. 600')
    # parser.add_argument('-f', '--format', help='The output file format, default png')
    parser.add_argument('model', help='The STL file to be converted')
    return parser.parse_args()


if __name__ == '__main__':
    print cmd_ars()
