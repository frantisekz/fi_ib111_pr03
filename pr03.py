#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
IB111 Project03
================
Image color optimalization
Author: František Zatloukal

"""

import sys
import os

from math import sqrt, ceil, floor
from PIL import Image

class Tile(object):
    """
    Represents single part
    """

    def __init__(self, image, number, position, coords, filename=None):
        self.image = image
        self.number = number
        self.position = position
        self.coords = coords
        self.filename = filename

    @property
    def row(self):
        return self.position[0]

    @property
    def column(self):
        return self.position[1]

    @property
    def basename(self):
        """
        gets filename without path and extension
        """
        return get_basename(self.filename)

    def generate_filename(self, directory=os.getcwd(), prefix='tile',
                          format='jpg', path=True):
        """
        returns filename
        """
        filename = prefix + '_{col:03d}_{row:03d}.{ext}'.format(col=self.column, row=self.row, ext=format)
        if not path:
            return filename
        return os.path.join(directory, filename)

    def save(self, filename=None, format='jpeg'):
        """
        saves image to a file
        """
        if not filename:
            filename = self.generate_filename(format=format)
        self.image.save(filename, format)
        self.filename = filename

    def __repr__(self):
        """
        Shows tile number and filename
        """
        if self.filename:
            return '<Tile #{} - {}>'.format(self.number,
                                            os.path.basename(self.filename))
        return '<Tile #{}>'.format(self.number)

def get_basename(filename):
    """
    returns filename without path and extension
    """
    return os.path.splitext(os.path.basename(filename))[0]

def get_total_size(tiles):
    """
    returns total size of tiles
    """
    columns, rows = calc_cols_rows(len(tiles))
    tile_size = tiles[0].image.size
    return (tile_size[0] * columns, tile_size[1] * rows)

def calc_cols_rows(n):
    """
    returns a tuple(num_columns, num_rows)
    """
    num_columns = ceil(sqrt(float(n)))
    num_rows = ceil(float(n) / float(num_columns))
    return (num_columns, num_rows)

def divide_image(filename, number_tiles):
    """
    splits image into tiles.
    returns tuple of tiles
    """
    img = Image.open(filename)
    img_width, img_height = img.size
    cols, rows = calc_cols_rows(number_tiles)
    tile_width, tile_height = int(floor(img_width / cols)), int(floor(img_height / rows))

    count = 1
    tiles = []
    for ycord in range(0, img_height, tile_height):
        for xcord in range(0, img_width, tile_width):
            area = (xcord, ycord, xcord + tile_width, ycord + tile_height)
            image = img.crop(area)
            position = (int(floor(xcord / tile_width)) + 1,
                        int(floor(ycord / tile_height)) + 1)
            coords = (xcord, ycord)
            tile = Tile(image, count, position, coords)
            tiles.append(tile)
            count += 1
    save_tiles(tiles, prefix=get_basename(filename), directory=os.path.dirname(filename))
    return tuple(tiles)

def join(tiles):
    """
    joins tiles to a single image
    returns image
    """
    img = Image.new('RGB', get_total_size(tiles), None)
    for tile in tiles:
        img.paste(tile.image, tile.coords)
    return img

def save_tiles(tiles, prefix='', directory=os.getcwd(), format='jpg'):
    """
    writes tiles to disk as images
    returns tuple of Tiles
    """
    for tile in tiles:
        tile.save(filename=tile.generate_filename(prefix=prefix, directory=directory, format=format))
    return tuple(tiles)

def avg_color(image, width, height):
    """
    Computes average color of given image
    """
    red = 0
    green = 0
    blue = 0
    for xcord in range(0, width):
        for ycord in range(0, height):
            red_tmp, green_tmp, blue_tmp = image.getpixel((xcord, ycord))
            red = (red + red_tmp) / 2
            green = (green + green_tmp) / 2
            blue = (blue + blue_tmp) / 2
    return (red, green, blue)


if len(sys.argv) < 3:
    print("At least 3 arguments are needed to run this app")
    print("./pr03.py [image_path] [color_count]")
    sys.exit()

if sys.argv[2] == 0:
    print("Color count must be bigger than zero!")
    sys.exit()

parts = divide_image(sys.argv[1], int(sys.argv[2]))
compressed_parts = list(parts)
i = 0

for part in parts:
    thumb = Image.open(part.filename)
    thumb_width, thumb_height = part.image.size
    average_color = avg_color(part.image, thumb_width, thumb_height)
    print("Average color for part: " + part.filename + " is: ", end="")
    print(average_color)
    compressed_parts[i].image = Image.new('RGB', (int(thumb_width), int(thumb_height)), (int(average_color[0]), int(average_color[1]), int(average_color[2])))
    i += 1

to_join = tuple(compressed_parts)

#merge images back
result = join(to_join)
result.save(sys.argv[1] + "_compressed", "jpeg")
for file in os.listdir("."):
    if file.endswith(".jpg") and file != sys.argv[1]:
        os.system("rm " + file)
