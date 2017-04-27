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


import ghostb.graph as graph
from ghostb.locmap import LocMap
import ghostb.geo as geo


class CropGraph:
    def __init__(self, db):
        self.locmap = LocMap(db)

    def crop(self, csv_in, csv_out, min_lat, min_lng, max_lat, max_lng):
        print('cropping graph for rectangle: %s %s %s %s' % (min_lat, min_lng, max_lat, max_lng))
        g = graph.read_graph(csv_in)

        new_g = {}
        for edge in g:
            loc1 = self.locmap.coords[edge[0]]
            loc2 = self.locmap.coords[edge[1]]
            if geo.in_area(loc1, min_lat, min_lng, max_lat, max_lng)\
                    and geo.in_area(loc2, min_lat, min_lng, max_lat, max_lng):
                new_g[edge] = g[edge]

        graph.write_graph(new_g, csv_out)
