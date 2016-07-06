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


from ghostb.draw_map import draw


def check_scale(borders, i):
    return int(borders) & (2 << i) > 0


def draw_border(m, x, y, scales, borders, scale, thick, sep, dims):
    if check_scale(borders, scale):
        color = 'limegreen'
        if scales == 2:
            if scale > 0:
                color = 'darkred'
        else:
            if scale == 1:
                color = 'dodgerblue'
            elif scale > 1:
                color = 'darkred'

        # horizontal border translation
        delta = sep * dims[0] * scale
        xi = (x[0] + delta, x[1] + delta)
        yi = (y[0], y[1])
        m.plot(xi, yi, color, linewidth=thick)


def draw_multi_borders(cols, co, m, xorig, yorig, dims, extra):
    intervals = extra['intervals']
    thick = extra['thick']
    sep = extra['sep']

    for i in range(cols):
        x, y = m((co[i][1], co[i][3]), (co[i][0], co[i][2]))
        x = (x[0] - xorig, x[1] - xorig)
        y = (y[0] - yorig, y[1] - yorig)
        borders = co[i][4]
        for j in range(intervals):
            draw_border(m, x, y, intervals, borders, j, thick, sep, dims)


def draw_multi_map(borders_file, output_file, region, photo_dens_file=None, pop_dens_file=None, top_cities_file=None,
                   osm=False, resolution='i', width=50., thick=1.0, sep=1.0, intervals=100, font_size=30.0,
                   dot_size=30.0, label_offset=0.00075):
    extra = {'thick': thick,
             'sep': sep,
             'intervals': intervals}
    draw(borders_file, output_file, region, photo_dens_file=photo_dens_file, pop_dens_file=pop_dens_file,
         top_cities_file=top_cities_file, osm=osm, resolution=resolution, width=width, draw_borders=draw_multi_borders,
         font_size=font_size, dot_size=dot_size, label_offset=label_offset, extra=extra)
