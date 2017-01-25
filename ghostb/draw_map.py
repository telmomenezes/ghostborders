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
from PIL import Image
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


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class DrawMap(object):
    # resolutions:
    # c (crude), l (low), i (intermediate), h (high), f (full)
    def __init__(self, borders_file, output_file, region, photo_dens_file=None, pop_dens_file=None,
                 top_cities_file=None, osm=False, resolution='i', width=50., thick=10., color='darkred',
                 linestyle='solid', font_size=30.0, dot_size=30.0, label_offset=0.00075, extra_height=0.):

        self.output_file = output_file
        self.osm = osm
        self.resolution = resolution
        self.pop_dens_file = pop_dens_file
        self.photo_dens_file = photo_dens_file
        self.region = region
        self.top_cities_file = top_cities_file
        self.font_size = font_size
        self.dot_size = dot_size
        self.label_offset = label_offset
        self.thick = thick
        self.color = color
        self.linestyle = linestyle
        self.font_size = font_size

        mpl.rc('font', family='Arial')

        self.co = genfromtxt(borders_file, delimiter=',', skip_header=1)
        self.cols = self.co.shape[0]

        self.cc = region_coords[region]
        self.x0 = self.cc[1]
        self.y0 = self.cc[0]
        self.x1 = self.cc[3]
        self.y1 = self.cc[2]
        self.dx = abs(self.x1 - self.x0)
        self.dy = abs(self.y1 - self.y0)

        self.width = width
        self.base_height = width * self.dy / self.dx
        self.height = self.base_height + self.base_height * extra_height
        self.m = Basemap(projection='merc', resolution=resolution,
                         llcrnrlat=self.y0, llcrnrlon=self.x0, urcrnrlat=self.y1, urcrnrlon=self.x1)
        self.fig = plt.figure(figsize=(width, self.height))
        self.ax = self.fig.add_subplot(111)

        self.xorig, self.yorig = self.m(self.x0, self.y0)
        self.dims = self.m(self.width, self.height)
        self.dims = (abs(self.dims[0] - self.xorig), abs(self.dims[1] - self.yorig))

    def draw_borders(self):
        for i in range(self.cols):
            x, y = self.m((self.co[i][1], self.co[i][3]), (self.co[i][0], self.co[i][2]))
            x = (x[0] - self.xorig, x[1] - self.xorig)
            y = (y[0] - self.yorig, y[1] - self.yorig)
            line, = self.m.plot(x, y, self.color, linewidth=self.thick, ls=self.linestyle)
            if self.linestyle == 'dashed':
                dashes = [20, 20]
                line.set_dashes(dashes)

    def draw_population_densities(self):
        self.m.dens_info = None
        self.m.dens = None
        self.m.readshapefile(self.pop_dens_file, 'dens')

        min_dens = float("inf")
        max_dens = float("-inf")
        for info in self.m.dens_info:
            if info['NUTS_ID'][0:2] in region_NUTS_codes[self.region]:
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

        for xy, info in zip(self.m.dens, self.m.dens_info):
            if info['NUTS_ID'][0:2] in region_NUTS_codes[self.region]:
                d = info['DENSITY']
                if d < 1:
                    d = 1
                d = math.log(float(d))
                poly = Polygon(xy, facecolor=sm.to_rgba(d), alpha=0.9)
                plt.gca().add_patch(poly)

    def draw_photo_densities(self):
        dens = genfromtxt(self.photo_dens_file, delimiter=',', skip_header=1)
        max_photo_dens = float("-inf")
        for i in range(len(dens)):
            pdens = math.log(dens[i][2])
            if pdens > max_photo_dens:
                max_photo_dens = pdens

        for i in range(len(dens)):
            x, y = self.m(dens[i][1], dens[i][0])
            x -= self.xorig
            y -= self.yorig
            weight = math.log(dens[i][2]) / max_photo_dens
            if weight < 0.001:
                weight = 0.001
            weight *= point_size_factor
            self.m.plot(x, y, 'b.', markersize=weight)

    def draw_top_cities(self):
        for tcf in self.top_cities_file:
            with open(tcf, 'r') as f:
                rows = f.read().split('\n')
                for row in rows:
                    city = row.split(',')
                    name = city[0]
                    lat = float(city[2])
                    lng = float(city[3])
                    if lat >= region_coords[self.region][0] \
                            and lat <= region_coords[self.region][2] \
                            and lng >= region_coords[self.region][1] \
                            and lng <= region_coords[self.region][3]:
                        x, y = self.m(lng, lat)
                        x -= self.xorig
                        y -= self.yorig
                        self.m.plot(x, y, '.', color='0.15', markersize=self.dot_size)
                        y += self.dims[1] * self.label_offset
                        text = plt.text(x, y, name, color='0.15', ha='center', va='bottom', size=self.font_size)
                        text.set_path_effects(
                            [path_effects.Stroke(linewidth=15, foreground='white'), path_effects.Normal()])

    def draw(self):
        print('drawing to: %s' % self.output_file)

        if self.osm:
            osm_img_path = maps.coords2path(self.y0, self.x0, self.y1, self.x1)
            im = rgb2gray(plt.imread(osm_img_path))
            self.m.imshow(im, interpolation='lanczos', origin='upper', cmap = plt.get_cmap('gray'), alpha=0.75)
        else:
            # drawlsmaks stopped working for some reason...
            # self.m.drawlsmask(resolution=self.resolution, grid=1.25, ocean_color=water_color, land_color=land_color)
            self.m.drawcoastlines(linewidth=coastline_width, color=coastline_color)
            self.m.drawmapboundary(fill_color=water_color)
            self.m.fillcontinents(color=land_color, lake_color=water_color)
            # if draw_rivers:
            #     self.m.drawrivers(color=water_color, linewidth=river_width)
            #     self.m.fillcontinents(color=land_color, lake_color=water_color)

        # draw population densities
        if self.pop_dens_file:
            self.draw_population_densities()
        else:
            self.m.drawcountries(linewidth=border_width)

        # draw photo densities
        if self.photo_dens_file is not None:
            self.draw_photo_densities()

        # draw phantom borders
        self.draw_borders()

        # draw top cities
        self.draw_top_cities()

        # clear border
        ax = plt.gca()
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.savefig(self.output_file, bbox_inches='tight')

        # crop remaining border
        im = Image.open(self.output_file)
        w, h = im.size
        im.crop((5, 1, w - 1, h - 1)).save(self.output_file)
