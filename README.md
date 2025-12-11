# Purpose
This script can be used to generate a depthmap image from a STL mesh file.  This can be useful for things like 3d laser engravings

# Usage
The script has a full help, but the simple usage would be
```bash
$ python stltoimg.py ./path/to/file.stl
```
If you only want to see the output, and not save the file, you can add the `--show` flag

You can override the output file name and directory by using the `--output` option

You can also set floor and celing offsets to get a tighter fit to a region of interest in your STL file with the `--bottom-offset` and `--top-offset` options

You can also replace a color value in the depthmap with the `--replace <target> <value>` option.  This can be useful if your resulting depthmap has a black background that a laser cutter might attempt to engrave at full power.  By replacing black with white, the interesting parts of the depth map are left untouched (not inverted), while the "full power" background becomes a "zero power" background.

# Instalation and Requirements

Requirements for the Python script can be found in the requirements.txt file

Requirements can be installed by running
```bash
$ pip install -r requirements.txt
```