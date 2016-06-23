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


import itertools
import numpy as np
from ghostb.locmap import LocMap
import ghostb.geo


class UserScales:
    def __init__(self, db, outfile, percentiles_file, scales, table='media'):
        self.db = db
        self.table = table
        self.outfile = open(outfile, 'w')
        self.scales = scales
        locmap = LocMap(db)
        self.locs = locmap.coords
        self.per_table = {}
        data = np.genfromtxt(percentiles_file, names=['percentile', 'dist'], skip_header=1, delimiter=',')
        for row in data:
            self.per_table[int(row['percentile'])] = float(row['dist'])

    def link_scale(self, link):
        dist = ghostb.geo.distance(self.locs[link[0]], self.locs[link[1]])
        for i in range(len(self.scales)):
            if dist < self.per_table[self.scales[i]]:
                return i
        return len(self.scales)

    def write_line(self, user_id, links):
        scales = [0] * (len(self.scales) + 1)
        for link in links:
            scales[self.link_scale(link)] += 1
        self.outfile.write('%s' % user_id)
        for s in scales:
            self.outfile.write(',%s' % s)
        self.outfile.write('\n')

    def process_user(self, user_id):
        self.db.cur.execute("SELECT location FROM %s WHERE user=%s"
                            % (self.table, user_id))
        data = self.db.cur.fetchall()
        locations = [x[0] for x in data]
        
        # make locations unique
        locations = set(locations)

        links = itertools.combinations(locations, 2)
        self.write_line(user_id, links)

    def generate(self):
        print('generating user scales file.')
        print('using table: %s' % self.table)
            
        self.db.cur.execute("SELECT count(id) FROM user")
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)

        # write output file header
        self.outfile.write('user')
        for i in range(len(self.scales) + 1):
            self.outfile.write(',scale_%s' % i)
        self.outfile.write('\n')

        done = False
        n = 0
        while not done:
            self.db.cur.execute("SELECT id FROM user LIMIT %s,1000" % n)
            users = self.db.cur.fetchall()
            if len(users) == 0:
                done = True
            else:
                percent = (float(n) / float(nusers)) * 100.0
                for user in users:
                    self.process_user(user[0])

                print("%s/%s (%s%%) processed" % (n, nusers, percent))
                n += len(users)

        self.outfile.close()
    
        print("done.")
