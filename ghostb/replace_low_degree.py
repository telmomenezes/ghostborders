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


import ghostb.graph
import ghostb.geo
from ghostb.locmap import LocMap


class ReplaceLowDegree:
    def __init__(self, db, infile, min_degree):
        self.db = db
        locmap = LocMap(db)
        self.locs = locmap.coords

        self.g = ghostb.graph.read_graph(infile)
        self.degs = ghostb.graph.degrees(self.g)

        self.min_degree = min_degree

        self.active = []
        self.inactive = []
        self.inactive_active = {}

    def nearest(self, inactive_loc):
        new_loc = -1
        min_dist = 9999999
        for loc in self.locs:
            if loc in self.active:
                dist = ghostb.geo.distance(self.locs[inactive_loc], self.locs[loc])
                if dist < min_dist:
                    new_loc = loc
                    min_dist = dist

        if new_loc < 0:
            print('nearest -1: %s' % inactive_loc)
        return new_loc

    def mean_degree(self):
        total = 0.0
        count = 0.0
        for loc in self.degs:
            total += float(self.degs[loc])
            count += 1.0
        mean_degree = total / count
        print('mean degreee: %s' % mean_degree)

    def active_inactive(self):
        # determin active and inactive locations
        for loc in self.degs:
            if self.degs[loc] >= self.min_degree:
                self.active.append(loc)
            else:
                self.inactive.append(loc)

        # determine closest locations
        for loc in self.inactive:
            self.inactive_active[loc] = self.nearest(loc)

    def fix_vert(self, vert):
        if vert in self.active:
            return vert
        else:
            return self.inactive_active[vert]

    def fix_edge(self, edge):
        return [self.fix_vert(edge[0]), self.fix_vert(edge[1])]

    def run(self, outfile):
        self.mean_degree()
        self.active_inactive()        

        # compute filtered graph
        new_g = {}
        for edge in self.g:
            new_edge = self.fix_edge(edge)
            # do not add self-loops (can be created by fix_edge)
            if new_edge[0] != new_edge[1]:
                ghostb.graph.add_edge(new_g, new_edge, self.g[edge])
        
        # write new graph
        ghostb.graph.write_graph(new_g, outfile)