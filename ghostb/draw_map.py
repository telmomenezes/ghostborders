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


import matplotlib as mpl
mpl.use('pdf')
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patheffects as path_effects
from matplotlib.patches import Polygon
import math
from mpl_toolkits.basemap import Basemap
from numpy import genfromtxt
import numpy as np
from ghostb.region_defs import *
import ghostb.maps as maps


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


def draw_simple_borders(cols, co, m, xorig, yorig, _, extra):
    thick = extra['thick']
    color = extra['color']
    linestyle = extra['linestyle']
    for i in range(cols):
        x, y = m((co[i][1], co[i][3]), (co[i][0], co[i][2]))
        x = (x[0] - xorig, x[1] - xorig)
        y = (y[0] - yorig, y[1] - yorig)
        line, = m.plot(x, y, color, linewidth=thick, ls=linestyle)
        if linestyle == 'dashed':
            dashes = [20, 20]
            line.set_dashes(dashes)


def rgb2gray(rgb):
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    gray *= 1.25
    return gray


# resolutions:
# c (crude), l (low), i (intermediate), h (high), f (full)
def draw(borders_file, output_file, region, photo_dens_file=None, pop_dens_file=None, top_cities_file=None,
         osm=False, resolution='i', width=50., draw_borders=draw_simple_borders, font_size=30.0, dot_size=30.0,
         extra=None):

    print('drawing to: %s' % output_file)

    co = genfromtxt(borders_file, delimiter=',', skip_header=1)
    cols = co.shape[0]

    cc = region_coords[region] 
    x0 = cc[1]
    y0 = cc[0]
    x1 = cc[3]
    y1 = cc[2]
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    height = width * dy / dx
    m = Basemap(projection='merc', resolution=resolution, llcrnrlat=y0, llcrnrlon=x0, urcrnrlat=y1, urcrnrlon=x1)
    fig = plt.figure(figsize=(width, height))

    if osm:
        osm_img_path = maps.coords2path(y0, x0, y1, x1)
        im = rgb2gray(plt.imread(osm_img_path))
        m.imshow(im, interpolation='lanczos', origin='upper', cmap = plt.get_cmap('gray'))

    xorig, yorig = m(x0, y0)
    dims = m(width, height)
    dims = (abs(dims[0] - xorig), abs(dims[1] - yorig))

    if not osm:
        m.drawlsmask(resolution=resolution, grid=1.25, ocean_color=water_color, land_color=land_color)
        m.drawcoastlines(linewidth=coastline_width, color=coastline_color)
        if draw_rivers:
            m.drawrivers(color=water_color, linewidth=river_width)
        m.fillcontinents(color=land_color, lake_color=water_color)

    # draw population densities
    if pop_dens_file:
        m.dens_info = None
        m.dens = None
        m.readshapefile(pop_dens_file, 'dens')

        min_dens = float("inf")
        max_dens = float("-inf")
        for info in m.dens_info:
            if info['NUTS_ID'][0:2] in region_NUTS_codes[region]:
                d = info['DENSITY']
                if d < 1:
                    d = 1
                d = math.log(float(d))
                if d < min_dens:
                    min_dens = d
                if d > max_dens:
                    max_dens = d

        norm = mpl.colors.Normalize(vmin=min_dens, vmax=max_dens)
        cmap = cm.get_cmap('Greens')
        sm = cm.ScalarMappable(norm=norm, cmap=cmap)

        for xy, info in zip(m.dens, m.dens_info):
            if info['NUTS_ID'][0:2] in region_NUTS_codes[region]:
                d = info['DENSITY']
                if d < 1:
                    d = 1
                d = math.log(float(d))
                poly = Polygon(xy, facecolor=sm.to_rgba(d), alpha=0.9)
                plt.gca().add_patch(poly)
    else:
        m.drawcountries(linewidth=border_width)

    # draw photo densities
    if photo_dens_file is not None:
        dens = genfromtxt(photo_dens_file, delimiter=',', skip_header=1)
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
            weight *= point_size_factor
            m.plot(x, y, 'b.', markersize=weight)

    # draw phantom borders
    draw_borders(cols, co, m, xorig, yorig, dims, extra)

    # draw top cities
    for tcf in top_cities_file:
        with open(tcf, 'r') as f:
            rows = f.read().split('\n')
            for row in rows:
                city = row.split(',')
                name = city[0]
                lat = float(city[2])
                lng = float(city[3])
                x, y = m(lng, lat)
                x -= xorig
                y -= yorig
                m.plot(x, y, '.', color='0.15', markersize=dot_size)
                y += dims[1] * 0.00075
                text = plt.text(x, y, name, color='0.15', ha='center', va='bottom', size=font_size)#, weight='bold')
                text.set_path_effects([path_effects.Stroke(linewidth=15, foreground='white'), path_effects.Normal()])

    plt.savefig(output_file)


def draw_map(borders_file, output_file, region, photo_dens_file=None, pop_dens_file=None, top_cities_file=None,
             osm=False, resolution='i', width=50., thick=10., color='darkred', linestyle='solid', font_size=30.0,
             dot_size=30.0):
    extra = {'thick': thick,
             'color': color,
             'linestyle': linestyle}
    draw(borders_file, output_file, region, photo_dens_file=photo_dens_file, pop_dens_file=pop_dens_file,
         top_cities_file=top_cities_file, osm=osm, resolution=resolution, width=width, draw_borders=draw_simple_borders,
         font_size=font_size, dot_size=dot_size, extra=extra)
