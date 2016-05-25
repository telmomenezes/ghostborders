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


class FilterDists:
    def __init__(self, db):
        self.locmap = LocMap(db)

    def filter(self, csv_in, csv_out, max_dist):
        print('filtering graph for maximum distance: %s' % max_dist)
        g = graph.read_graph(csv_in)

        for edge in g:
            loc1 = self.locmap.coords[edge[0]]
            loc2 = self.locmap.coords[edge[1]]
            dist = geo.distance(loc1, loc2)
            if dist > max_dist:
                g[edge] = 0.

        graph.write_graph(g, csv_out)
