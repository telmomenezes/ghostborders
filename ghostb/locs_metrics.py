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
from ghostb.locmap import LocMap
import ghostb.geo as geo
import math


DIRECTIONS = 8


def time_delta(link, loc_ts):
    min_delta = -1
    for ts1 in loc_ts[link[0]]:
        for ts2 in loc_ts[link[1]]:
            if ts1 != ts2:
                delta = abs(ts1 - ts2)
                if (min_delta < 0) or (delta < min_delta):
                    min_delta = delta
    return min_delta


def normalize_angle(ang):
    new_ang = ang
    while new_ang < 0:
        new_ang += math.pi * 2
    while new_ang >= math.pi * 2:
        new_ang -= math.pi * 2
    return new_ang


class LocsMetrics:
    def __init__(self, db):
        self.db = db
        self.locmap = LocMap(db).coords
        self.ll = {}
        for loc in self.locmap:
            self.locmap[loc]['photos'] = 0
            self.locmap[loc]['users'] = set()
            self.locmap[loc]['dist'] = 0.
            self.locmap[loc]['time'] = 0.
            self.locmap[loc]['degree'] = 0
            self.locmap[loc]['neighbors'] = 0
            self.locmap[loc]['self'] = 0
            self.locmap[loc]['entropy'] = 0
            self.locmap[loc]['dist_var'] = 0.
            self.locmap[loc]['angle'] = 0.
            self.locmap[loc]['angle_var'] = 0.
            self.locmap[loc]['angle_entropy'] = [0. for _ in range(DIRECTIONS)]

    def update_entropy(self, loc, weight):
        degree = float(self.locmap[loc]['degree'])
        p = weight / degree
        entr = -p * math.log(p)
        self.locmap[loc]['entropy'] += entr

    def update_angle_entropy(self, orig, targ, weight):
        angle = self.angle(orig, targ)
        angle += math.pi
        if angle >= math.pi * 2:
            angle = 0.
        div = (math.pi * 2) / DIRECTIONS
        i = int(angle / div)
        self.locmap[orig]['angle_entropy'][i] += weight

    def compute_angle_entropy(self, loc):
        degree = float(self.locmap[loc]['degree'])

        entr = 0.
        for i in range(DIRECTIONS):
            weight = self.locmap[loc]['angle_entropy'][i]
            if weight > 0.:
                p = weight / degree
                entr -= p * math.log(p)
            
        self.locmap[loc]['angle_entropy'] = entr

    def update_dist_var(self, v, dist, weight):
        mean = self.locmap[v]['dist']
        x = dist - mean
        x *= x
        self.locmap[v]['dist_var'] += x * weight

    def update_angle_var(self, v1, v2, weight):
        ang = self.angle(v1, v2)
        mean = self.locmap[v1]['angle']
        dang = ang - mean
        if dang > math.pi:
            dang -= math.pi * 2
        if dang < -math.pi:
            dang += math.pi * 2
        x = dang * dang
        self.locmap[v1]['angle_var'] += x * weight
        
    def post_process(self):
        for loc in self.locmap:
            degree = self.locmap[loc]['degree']
            if degree > 0:
                self.locmap[loc]['dist'] /= degree
                self.locmap[loc]['time'] /= degree
                self.locmap[loc]['angle'] /= degree
            self.locmap[loc]['users'] = len(self.locmap[loc]['users'])

        for link in self.ll:
            v1 = link[0]
            v2 = link[1]
            w = float(self.ll[link])
            loc1 = self.locmap[v1]
            loc2 = self.locmap[v2]
            dist = geo.distance(loc1, loc2)
            self.update_entropy(v1, w)
            self.update_entropy(v2, w)
            self.update_dist_var(v1, dist, w)
            self.update_dist_var(v2, dist, w)
            self.update_angle_var(v1, v2, w)
            self.update_angle_var(v2, v1, w)
            self.update_angle_entropy(v1, v2, w)
            self.update_angle_entropy(v2, v1, w)

        for loc in self.locmap:
            degree = self.locmap[loc]['degree']
            if degree > 0:
                self.locmap[loc]['dist_var'] /= degree
                self.locmap[loc]['angle_var'] /= degree
            self.compute_angle_entropy(loc)
            
    def write_data(self, outfile):
        f = open(outfile, 'w')
        f.write('loc,lat,lng,photos,users,dist,time,degree,neighbors,self,entropy,dist_var,angle_var,angle_entropy\n')
        for loc in self.locmap:
            lm = self.locmap[loc]
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' %
                    (loc, lm['lat'], lm['lng'], lm['photos'], lm['users'], lm['dist'],
                     lm['time'], lm['degree'], lm['neighbors'], lm['self'],
                     lm['entropy'], lm['dist_var'], lm['angle_var'],
                     lm['angle_entropy']))
        f.close()

    def angle(self, orig, targ):
        x1 = self.locmap[orig]['lat']
        y1 = self.locmap[orig]['lng']
        x2 = self.locmap[targ]['lat']
        y2 = self.locmap[targ]['lng']
        return math.atan2(y2 - y1, x2 - x1)
        
    def update_angle(self, orig, targ):
        ang = self.angle(orig, targ)
        self.locmap[orig]['angle'] += ang
        
    def process_link(self, link, time):
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
            self.locmap[v1]['neighbors'] += 1
            self.locmap[v2]['neighbors'] += 1

        self.locmap[v1]['degree'] += 1
        self.locmap[v2]['degree'] += 1

        loc1 = self.locmap[v1]
        loc2 = self.locmap[v2]
        dist = geo.distance(loc1, loc2)
        self.locmap[v1]['dist'] += dist
        self.locmap[v2]['dist'] += dist

        t = float(time) / 60.
        t /= 60.
        t /= 24.
        self.locmap[v1]['time'] += t
        self.locmap[v2]['time'] += t

        self.update_angle(v1, v2)
        self.update_angle(v2, v1)
        
    def process_user(self, user_id):
        self.db.cur.execute("SELECT location, ts FROM media WHERE user=%s" % user_id)
        data = self.db.cur.fetchall()
        locations = [x[0] for x in data]

        loc_ts = {}
        for x in data:
            loc = x[0]
            ts = x[1]
            if loc in loc_ts:
                loc_ts[loc].append(ts)
            else:
                loc_ts[loc] = [ts, ]
        
        freqs = {}
        for l in locations:
            if l in freqs:
                freqs[l] += 1
            else:
                freqs[l] = 1

        # make locations unique
        locations = set(locations)

        # add user to location's user list
        for loc in locations:
            self.locmap[loc]['users'].add(user_id)

        links = itertools.combinations(locations, 2)

        for link in links:
            time = time_delta(link, loc_ts)
            self.process_link(link, time)

        # create self-loops for locations where a single user has more than one event
        for l in freqs:
            self.locmap[l]['photos'] += freqs[l]
            if freqs[l] > 1:
                self.locmap[l]['self'] += 1

    def generate(self, outfile):
        print('generating location metrics.')

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

        self.post_process()
        self.write_data(outfile)
    
        print("done.")
