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
from ghostb.draw_map import phantom_border_width_factor


def draw_multi_borders(cols, co, m, xorig, yorig, extra):
    thickness = extra['thickness']
    intervals = extra['intervals']

    for i in range(cols):
        weight = co[i][4]
        max_weight = co[i][7]
        if (weight > 0.) and (max_weight > 0.):
            x, y = m((co[i][1], co[i][3]), (co[i][0], co[i][2]))
            x = (x[0] - xorig, x[1] - xorig)
            y = (y[0] - yorig, y[1] - yorig)
            mean_dst = co[i][5]
            h = co[i][8]
            color = 'black'
            if h <= intervals / 2.:
                if mean_dst > 50.0:
                    color = 'red'
                else:
                    color = 'blue'
            lw = h * phantom_border_width_factor * thickness
            m.plot(x, y, color, linewidth=lw, alpha=max_weight)


def draw_multi_map(borders_file, output_file, region, photo_dens_file=None, pop_dens_file=None,
                   osm=False, resolution='i', width=50., thickness=1.0, intervals=100):
    extra = {'thickness': thickness,
             'intervals': intervals}
    draw(borders_file, output_file, region, photo_dens_file=photo_dens_file, pop_dens_file=pop_dens_file, osm=osm,
         resolution=resolution, width=width, draw_borders=draw_multi_borders, extra=extra)
