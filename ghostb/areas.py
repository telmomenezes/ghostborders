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


from ghostb.voronoi import Voronoi
import ghostb.partition as part


class Areas:
    def __init__(self, db, in_file, smooth):
        self.smooth = smooth
        self.db = db
        self.in_file = in_file
        self.vor = self.init_voronoi()

    def init_voronoi(self):
        vertices = set(part.read(self.in_file).keys())
        return Voronoi(self.db, vertices)
    
    def compute(self):
        print("processing file %s ..." % self.in_file)
        par = part.Partition(self.vor, False)
        par.read(self.in_file)
        if self.smooth:
            par.smooth_until_stable()

        vareas = self.vor.areas()
        careas = {}
        for loc_id in par.comms:
            comm = par.comms[loc_id]
            if comm >= 0:
                a = vareas[loc_id]
                if comm in careas:
                    careas[comm] += a
                else:
                    careas[comm] = a

        total = 0.
        for comm in careas:
            total += careas[comm]
        mean_area = total / len(careas)
        print('mean_area: %s' % mean_area)
