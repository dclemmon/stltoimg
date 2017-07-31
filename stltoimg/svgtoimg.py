#!/usr/bin/env python

import argparse
import io
import numpy as np
import os

from PIL.ImageChops import lighter
from PIL import Image
from reportlab.graphics import renderPS
from reportlab.lib.colors import Color
from reportlab.graphics.shapes import Group
from reportlab.graphics.shapes import Polygon
from reportlab.graphics.shapes import Drawing
from svglib.svglib import svg2rlg


class SVGSmash(object):
    def __init__(self, path, dpi=72):
        """Populate the SVG object"""
        self.path = path
        self.dpi = dpi
        self.scaleValue = dpi/72.0
        self.target_color = Color(1, 1, 1, 1)
        self.background_color = Color(0, 0, 0, 1)
        self.parentdir = os.path.dirname(path)
        self.drawing = svg2rlg(path)
        self.image = Image.new('RGB', size=self.size)
        self.process(self.drawing)

    def process(self, level, color_value=0.0, neighbors=0):
        """
        Process file into output file
        :param level:
        :param color_value:
        :return:
        """
        if isinstance(level, Drawing):
            for child in level.contents:
                self.process(child,
                             color_value,
                             neighbors=len(level.contents))
        elif isinstance(level, Group) and not any(
                isinstance(x, Polygon) for x in level.contents):
            # a group of groups
            for child in level.contents:
                color_value += 1
                self.process(child,
                             color_value,
                             neighbors=len(level.contents))
        elif isinstance(level, Group) and any(
                isinstance(x, Polygon) for x in level.contents):
            for child in level.contents:
                # This should be a polygon
                if child.fillColor == self.target_color:
                    gval = float(color_value) / float(neighbors)
                    child.fillColor = Color(gval, gval, gval, 1)
            # Group color correction is complete, convert to image and add to base
            level.asDrawing(*self.size)
            level.renderScale = self.scaleValue
            ps_str = renderPS.drawToString(
                level)
            img = Image.open(io.BytesIO(ps_str))
            data = np.array(img)
            r1, g1, b1 = 255, 255, 255
            r2, g2, b2 = 0, 0, 0
            red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            data[:, :, :3][mask] = [r2, g2, b2]
            img = Image.fromarray(data)
            self.image = lighter(self.image, img)

    @property
    def input_fname(self):
        """Return the input file name"""
        return os.path.basename(self.path).rsplit('.', 1)[0]

    @property
    def input_ftype(self):
        """Return the file extension of the file"""
        return self.input_fname[-3:]

    @property
    def size(self):
        """Return the size or Bounding Box of the image"""
        return [int(x * self.scaleValue) for x in [self.drawing.width, self.drawing.height]]


def cmd_ars():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-u', '--unit', help='Select the units of the input file e.x. mm or in')
    # parser.add_argument('-a', '--analysis', help='Analyse the input SVG to determine proper layer height')
    parser.add_argument('-d', '--dpi', help='Select the output image DPI e.x. 600')
    # parser.add_argument('-f', '--format', help='The output file format, default png')
    parser.add_argument('model', help='The SVG file to be converted')
    return parser.parse_args()


if __name__ == '__main__':
    args = cmd_ars()
    print args
    svg = SVGSmash(args.model, dpi=int(args.dpi))
    svg.image.save("{path}/{fname}.png".format(path=svg.parentdir,
                                               fname=svg.input_fname))
    print svg.input_fname
