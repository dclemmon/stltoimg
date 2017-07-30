#!/usr/bin/env python

import argparse
import os
import time

from PIL.ImageChops import lighter
from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from reportlab.lib.colors import Color
from reportlab.graphics.shapes import Group
from reportlab.graphics.shapes import Polygon
from reportlab.graphics.shapes import Drawing


class SVGSmash(object):
    def __init__(self, path):
        """Populate the SVG object"""
        self.target_color = Color(1, 1, 1, 1)
        self.background_color = Color(0, 0, 0, 1)
        self.path = path
        self.drawing = svg2rlg(path)
        self.image = Image.new('L', size=self.size)
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
            print 'Processing Layer' + str(int(color_value))
            print 'Drawing:',
            level.asDrawing(*self.size)
            print 'Scale:',
            level.renderScale = 1
            print 'Render:',
            img = renderPM.drawToPIL(level, bg=self.background_color)
            print 'Convert:',
            img = img.convert('L')
            print 'Compare'
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
        return int(self.drawing.width), int(self.drawing.height)


def cmd_ars():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-u', '--unit', help='Select the units of the input file e.x. mm or in')
    # parser.add_argument('-a', '--analysis', help='Analyse the input SVG to determine proper layer height')
    # parser.add_argument('-d', '--dpi', help='Select the output image DPI e.x. 600')
    # parser.add_argument('-f', '--format', help='The output file format, default png')
    parser.add_argument('model', help='The SVG file to be converted')
    return parser.parse_args()


if __name__ == '__main__':
    args = cmd_ars()
    print args
    svg = SVGSmash(args.model)
    svg.image.save("{fname}.png".format(fname=svg.input_fname))
