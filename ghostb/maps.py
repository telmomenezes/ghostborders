#   Copyright (c) 2016 Centre Marc Bloch Berlin
#   (An-Institut der Humboldt Universität, UMIFRE CNRS-MAE).
#   All rights reserved.
#
#   Written by Telmo Menezes <telmo@telmomenezes.com>
#
#   This file is part of GhostBorders.
#
#   GhostBorders is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   GhostBorders is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with GhostBorders.  If not, see <http://www.gnu.org/licenses/>.


import mercantile
import urllib.request as urllib2
from PIL import Image
import io
import sys
import os


MAX_TILES = 25
TILE_SIDE = 255


def tile_url(zoom, x, y):
    return "http://a.tile.openstreetmap.org/%s/%s/%s.png" % (zoom, x, y)


def tile_image(zoom, x, y):
    url = tile_url(zoom, x, y)
    try:
        tile = urllib2.urlopen(url).read()
    except IOError:
        print("Unable to download image %s" % url)
        sys.exit(-1)
    return tile


def coords2png(lat0, lng0, lat1, lng1, out_file):
    # find desirable zoom level
    zoom = 0
    while True:
        tiles_list = list(mercantile.tiles(lng0, lat0, lng1, lat1, [zoom]))
        if len(tiles_list) > MAX_TILES:
            zoom -= 1
            break
        zoom += 1
    print('Zoom level %s' % zoom)
    
    # get tiles list
    tiles_list = list(mercantile.tiles(lng0, lat0, lng1, lat1, [zoom]))
    xs = [tile.x for tile in tiles_list]
    x0 = min(xs)
    x1 = max(xs)
    ys = [tile.y for tile in tiles_list]
    y0 = min(ys)
    y1 = max(ys)
    x_tiles = x1 - x0 + 1
    y_tiles = y1 - y0 + 1
    x_width = x_tiles * TILE_SIDE
    y_width = y_tiles * TILE_SIDE

    # create image
    img = Image.new("RGBA", (x_tiles * TILE_SIDE, y_tiles * TILE_SIDE), (0, 0, 0, 0))
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            print("processing tile %s, %s" % (x, y))
            tile = tile_image(zoom, x, y)
            tile_img = Image.open(io.BytesIO(tile))
            img.paste(tile_img, ((x - x0) * TILE_SIDE, (y - y0) * TILE_SIDE))

    # crop image
    top_left = mercantile.bounds(x0, y0, zoom)
    bottom_right = mercantile.bounds(x1, y1, zoom)
    img_lat1 = top_left.north
    img_lng0 = top_left.west
    img_lat0 = bottom_right.south
    img_lng1 = bottom_right.east
    img_lat_delta = img_lat1 - img_lat0
    img_lng_delta = img_lng1 - img_lng0
    pixel_lat_ratio = float(x_width) / img_lat_delta
    pixel_lng_ratio = float(y_width) / img_lng_delta
    left = int(abs(lng0 - img_lng0) * pixel_lng_ratio)
    right = x_width - int(abs(lng1 - img_lng1) * pixel_lng_ratio)
    top = int(abs(lat1 - img_lat1) * pixel_lat_ratio)
    bottom = y_width - int(abs(lat0 - img_lat0) * pixel_lat_ratio)
    img = img.crop((left, top, right, bottom))
            
    img.save(out_file, 'PNG')


def coords2path(lat0, lng0, lat1, lng1):
    filename = '%s_%s_%s_%s.png' % (lat0, lng0, lat1, lng1)
    directory = 'osm_imgs'

    # create osm images directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = '%s/%s' % (directory, filename)
    # create png for these coordinates if it doesn't exist
    if not os.path.exists(filepath):
        print('Generating png...')
        coords2png(lat0, lng0, lat1, lng1, filepath)

    return filepath
