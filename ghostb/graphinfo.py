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
import math


def graphinfo(csv_in):
    g = graph.read_graph(csv_in)
    print('edges: %s' % (len(g),))
    degs = graph.degrees(g)
    print('nodes: %s' % (len(degs),))
    total = 0.
    max_deg = -1.
    min_deg = float("inf")
    for node in degs:
        deg = degs[node]
        total += deg
        if deg > max_deg:
            max_deg = deg
        if deg < min_deg:
            min_deg = deg
    print('degress: min: %s; max: %s, mean: %s' % (min_deg, max_deg, total / len(degs)))
