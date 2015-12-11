import mercantile
import urllib.request as urllib2
from PIL import Image
import io
import sys


MAX_TILES = 25
TILE_SIDE = 255


def tile_url(zoom, x, y):
    return "http://a.tile.openstreetmap.org/%s/%s/%s.png" % (zoom, x, y)


def tile_image(zoom, x, y):
    url = tile_url(zoom, x, y)
    try:
        tile = urllib2.urlopen(url).read()
    except(Exception, e):
        print("Unable to download image %s" % url)
        sys.exit(-1)
    return tile


def coords2png(lat0, lng0, lat1, lng1):
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
    print('%s, %s, %s, %s' % (x0, y0, x1, y1))
    x_tiles = x1 - x0 + 1
    y_tiles = y1 - y0 + 1
    x_width = x_tiles * TILE_SIDE
    y_width = y_tiles * TILE_SIDE

    # create image
    img = Image.new("RGBA", (x_tiles * TILE_SIDE, y_tiles * TILE_SIDE), (0,0,0,0))
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
    print('%s, %s, %s, %s' % (img_lat0, img_lng0, img_lat1, img_lng1))
    img_lat_delta = img_lat1 - img_lat0
    img_lng_delta = img_lng1 - img_lng0
    pixel_lat_ratio = float(x_width) / img_lat_delta
    pixel_lng_ratio = float(y_width) / img_lng_delta
    left = int(abs(lng0 - img_lng0) * pixel_lng_ratio)
    right = x_width - int(abs(lng1 - img_lng1) * pixel_lng_ratio)
    top = int(abs(lat1 - img_lat1) * pixel_lat_ratio)
    bottom = y_width - int(abs(lat0 - img_lat0) * pixel_lat_ratio)
    print('%s, %s, %s, %s' % (left, top, right, bottom))
    img = img.crop((left, top, right, bottom))
            
    img.save('test.png', 'PNG')


coords2png(52.31, 13.05, 52.69, 13.77)
