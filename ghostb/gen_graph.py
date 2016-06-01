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
import itertools


class GenGraph:
    def __init__(self, db, graph_file, table='media'):
        self.db = db
        self.table = table
        self.graph_file = graph_file
        self.ll = {}

    def write_ll(self):
        f = open(self.graph_file, 'w')
        f.write('orig,targ,weight\n')
        for k in self.ll:
            f.write('%s,%s,%s\n' % (k[0], k[1], self.ll[k]))
        f.close()

    def process_link(self, link):
        v1 = link[0]
        v2 = link[1]
        if v1 > v2:
            v1 = link[1]
            v2 = link[0]
        l = (v1, v2)

        if l in self.ll:
            self.ll[l] += 1
        else:
            self.ll[l] = 1

    def process_user(self, user_id):
        self.db.cur.execute("SELECT location FROM %s WHERE user=%s"
                            % (self.table, user_id))
        data = self.db.cur.fetchall()
        locations = [x[0] for x in data]
        
        # make locations unique
        locations = set(locations)

        links = itertools.combinations(locations, 2)

        for link in links:
            self.process_link(link)

    def generate(self):
        print('generating graph.')
        print('using table: %s' % self.table)
            
        self.db.cur.execute("SELECT count(id) FROM user")
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)
    
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

        self.write_ll()
    
        print("done.")
