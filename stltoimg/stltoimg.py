#!/usr/bin/env python

import argparse
from stl import mesh


def cmd_ars():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--unit', help='Select the units of the input file e.x. mm or in')
    parser.add_argument('-d', '--dpi', help='Select the output image DPI e.x. 600')
    parser.add_argument('-f', '--format', help='The output file format, default png')
    parser.add_argument('model', help='The STL file to be converted')
    return parser.parse_args()


if __name__ == '__main__':
    print cmd_ars()
