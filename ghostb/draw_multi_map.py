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


import sys
import matplotlib.pyplot as plt
from ghostb.draw_map import DrawMap
import ghostb.geo as geo


def check_scale(borders, i):
    return int(borders) & (2 << i) > 0


def draw_natural_scale(x, y, size, color):
    p = plt.plot(x, y, 'b.', markersize=size * 1.5, c='white')
    p[0].set_zorder(300)
    p = plt.plot(x, y, 'b.', markersize=size, c=color)
    p[0].set_zorder(300)


class DrawMultiMap(DrawMap):
    def __init__(self, borders_file, output_file, region, photo_dens_file=None, pop_dens_file=None,
                 top_cities_file=None, osm=False, resolution='i', width=50., thick=10., color='darkred',
                 linestyle='solid', font_size=30.0, dot_size=30.0, label_offset=0.00075, sep=1.0, intervals=100,
                 scale_sizes='', natural_scales=''):
        self.sep = sep
        self.intervals = intervals

        if len(scale_sizes) == 0:
            self.scale_sizes = []
        else:
            self.scale_sizes = [float(token) for token in scale_sizes.split(',')]
        if len(natural_scales) == 0:
            self.natural_scales = []
        else:
            self.natural_scales = [float(token) for token in natural_scales.split(',')]

        extra_height = (len(self.scale_sizes) + 1) * 0.035

        DrawMap.__init__(self, borders_file, output_file, region, photo_dens_file, pop_dens_file, top_cities_file, osm,
                         resolution, width, thick, color, linestyle, font_size, dot_size, label_offset, extra_height)

        self.width_c = self.cc[3] - self.cc[1]
        self.height_c = self.cc[2] - self.cc[0]
        self.width_km = geo.distance({'lat': self.cc[0], 'lng': self.cc[1]},
                                     {'lat': self.cc[0], 'lng': self.cc[3]})
        self.height_km = geo.distance({'lat': self.cc[0], 'lng': self.cc[1]},
                                      {'lat': self.cc[2], 'lng': self.cc[1]})

        print('width: %s; height: %s' % (self.width_c, self.height_c))
        print('width: %skm; height: %skm' % (self.width_km, self.height_km))

    def scale_color(self, scale):
        color = 'limegreen'
        if self.intervals == 2:
            if scale > 0:
                color = 'darkred'
        else:
            if scale == 1:
                color = 'dodgerblue'
            elif scale > 1:
                color = 'darkred'
        return color

    def draw_border(self, x, y, borders, scale):
        if check_scale(borders, scale):
            color = self.scale_color(scale)

            # horizontal border translation
            delta = self.sep * self.dims[0] * scale
            xi = (x[0] + delta, x[1] + delta)
            yi = (y[0], y[1])
            self.m.plot(xi, yi, color, linewidth=self.thick)

    def draw_scale_label(self, scale, natural_scale_km, size_km=None):
        color = self.scale_color(scale)
        inf = False
        if scale >= len(self.scale_sizes):
            inf = True
        if inf:
            x0_ = 1.
            dist_label = ''
        else:
            x0_ = size_km / self.width_km
            dist_label = '%s km' % size_km
        y0_ = 1.01 - (scale + 1) * 0.02
        x1_ = 0.
        xn_ = natural_scale_km / self.width_km
        y0 = self.cc[0] + (self.height_c * y0_)
        x1 = self.cc[3] - self.width_c * x1_
        x0 = x1 - x0_ * self.width_c
        xn = x1 - xn_ * self.width_c

        # draw text
        if not inf:
            text_point = self.m(x0 - self.width_c * 0.01, y0)
            text = plt.text(text_point[0], text_point[1], dist_label,
                            color=color, ha='right', va='center', size=self.font_size * 1.5)
            text.set_zorder(300)

        # draw line
        thick = self.thick * 2
        if inf:
            xm = x0 + self.width_c * .1
            x, y = self.m((xm, x1), (y0, y0))
            l = self.m.plot(x, y, color, linewidth=thick)
            l[0].set_zorder(200)
            x, y = self.m((x0, xm), (y0, y0))
            l = self.m.plot(x, y, color, linewidth=thick, linestyle='--', dashes=(thick, thick))
            l[0].set_zorder(200)
        else:
            x, y = self.m((x0, x1), (y0, y0))
            l = self.m.plot(x, y, color, linewidth=thick)
            l[0].set_zorder(200)

        # draw natural scale
        x, y = self.m(xn, y0)
        draw_natural_scale(x, y, self.thick * 7, color)

    # override
    def draw_borders(self):
        for i in range(self.cols):
            x, y = self.m((self.co[i][1], self.co[i][3]), (self.co[i][0], self.co[i][2]))
            x = (x[0] - self.xorig, x[1] - self.xorig)
            y = (y[0] - self.yorig, y[1] - self.yorig)
            borders = self.co[i][4]
            for j in range(self.intervals):
                self.draw_border(x, y, borders, j)

        # draw scale sizes legend
        for i in range(len(self.scale_sizes)):
            self.draw_scale_label(i, self.natural_scales[i], self.scale_sizes[i])
        j = len(self.scale_sizes)
        self.draw_scale_label(j, self.natural_scales[j])
        ymin = self.base_height / self.height
        r = self.ax.axvspan(-sys.maxsize, sys.maxsize, ymin=ymin, ymax=1, color='white')
        r.set_zorder(100)
