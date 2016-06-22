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


from ghostb.locmap import LocMap
import ghostb.geo as geo
import ghostb.graph as graph


class Distances:
    def __init__(self, db):
        self.locmap = LocMap(db)

    def compute(self, infile, outfile):
        g = graph.read_graph(infile)

        f = open(outfile, 'w')
        
        total_distance = 0.
        count = 0.
        for edge in g:
            loc1 = self.locmap.coords[edge[0]]
            loc2 = self.locmap.coords[edge[1]]
            dist = geo.distance(loc1, loc2)
            f.write('%s\n' % dist)
            total_distance += dist
            count += 1.

        f.close()
        
        mean_distance = total_distance / count
        print('mean distance: %s' % mean_distance)
