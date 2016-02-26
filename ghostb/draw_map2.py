import matplotlib as mpl
mpl.use('pdf')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import math
from mpl_toolkits.basemap import Basemap
from numpy import genfromtxt
from ghostb.region_defs import *
import ghostb.maps as maps
from ghostb.locmap import LocMap
import numpy as np


# Some constants
# colors
land_color = 'white'
water_color = 'skyblue'
coastline_color = 'grey'
border_color = 'black'
phantom_border_color = 'red'
# widths
border_width = 2.
coastline_width = 3.
phantom_border_width_factor = 10.
river_width = 1.5
point_size_factor = 10.
# options
draw_rivers = True


# resolutions:
# c (crude), l (low), i (intermediate), h (high), f (full)
def draw_map2(borders_file, output_file, region, photo_dens_file=None,
              pop_dens_file=None, osm=False, resolution='i', width=50.):

    co = genfromtxt(borders_file, delimiter=',', skip_header=1)
    cols = co.shape[0]

    if photo_dens_file is not None:
        dens = genfromtxt(photo_dens_file, delimiter=',', skip_header=1)

    cc = region_coords[region] 
    x0 = cc[1]
    y0 = cc[0]
    x1 = cc[3]
    y1 = cc[2]
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    height = width * dy / dx

    plt.figure(figsize=(width, height))
    m = Basemap(projection='merc', resolution=resolution, llcrnrlat=y0, llcrnrlon=x0, urcrnrlat=y1, urcrnrlon=x1)

    if osm:
        osm_img_path = maps.coords2path(y0, x0, y1, x1)
        im = plt.imread(osm_img_path)
        m.imshow(im, interpolation='lanczos', origin='upper')

    xorig, yorig = m(x0, y0)

    if not osm:
        m.drawlsmask(resolution=resolution, grid=1.25, ocean_color=water_color, land_color=land_color)
        m.drawcoastlines(linewidth=coastline_width, color=coastline_color)
        if draw_rivers:
            m.drawrivers(color=water_color, linewidth=river_width)
        m.fillcontinents(color=land_color, lake_color=water_color)

    # draw population densities
    if pop_dens_file:
        s = m.readshapefile(pop_dens_file, 'dens')

        min_dens = float("inf")
        max_dens = float("-inf")
        for info in m.dens_info:
            if info['NUTS_ID'][0:2] in region_NUTS_codes[region]:
                d = info['DENSITY']
                if d < 1:
                    d = 1
                d = math.log(float(d))
                #d = float(d)
                if d < min_dens:
                    min_dens = d
                if d > max_dens:
                    max_dens = d

        norm = mpl.colors.Normalize(vmin=min_dens, vmax=max_dens)
        cmap = cm.Greens
        sm = cm.ScalarMappable(norm=norm, cmap=cmap)

        for xy, info in zip(m.dens, m.dens_info):
            if info['NUTS_ID'][0:2] in region_NUTS_codes[region]:
                d = info['DENSITY']
                if d < 1:
                    d = 1
                d = math.log(float(d))
                #d = float(d)
                poly = Polygon(xy, facecolor=sm.to_rgba(d), alpha=0.9)
                plt.gca().add_patch(poly)
    else:
        m.drawcountries(linewidth=border_width)

    # draw photo densities
    if photo_dens_file is not None:
        max_photo_dens = float("-inf")
        for i in range(len(dens)):
            pdens = math.log(dens[i][2])
            if pdens > max_photo_dens:
                max_photo_dens = pdens
    
        for i in range(len(dens)):
            x, y = m(dens[i][1], dens[i][0])
            x -= xorig
            y -= yorig
            weight = math.log(dens[i][2]) / max_photo_dens
            if weight < 0.001:
                weight = 0.001
            color = (0, 0, 1.0)
            weight *= point_size_factor
            #poly = m.ellipse(x, y, radius, radius, 20, facecolor=color, edgecolor='none', alpha=0.8)
            m.plot(x, y, 'b.', markersize=weight)

    # draw phantom borders
    for i in range(cols):
        max_weight = co[i][7]
        if max_weight > 0.75:
            x, y = m((co[i][1], co[i][3]), (co[i][0], co[i][2]))
            x = (x[0] - xorig, x[1] - xorig)
            y = (y[0] - yorig, y[1] - yorig)
            weight = co[i][4] * phantom_border_width_factor
            mean_dst = co[i][5]
            std_dst = co[i][6]
            color = 'black'
            if std_dst < 25.0:
                if mean_dst > 50.0:
                    color = 'red'
                else:
                    color = 'blue'
            m.plot(x, y, color, linewidth=weight)

    plt.savefig(output_file)
