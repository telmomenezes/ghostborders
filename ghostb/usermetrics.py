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


class UserMetrics:
    def __init__(self, db):
        self.db = db
        locmap = LocMap(db)
        self.locs = locmap.coords

    def x_received(self, table, photo_ids):
        total = 0
        for id in photo_ids:
            self.db.cur.execute("SELECT count(id) FROM %s WHERE media=%s" % (table, id))
            data = self.db.cur.fetchall()
            total += data[0][0]
        return total

    def process_user(self, user_id):
        self.db.cur.execute("SELECT location, ts, id FROM media WHERE user=%s ORDER BY ts" % (user_id, ))
        data = self.db.cur.fetchall()
        locations = [x[0] for x in data]
        
        # unique locations
        ulocations = set(locations)

        # only compute metrics for users who have been to at least 2 distinct locations
        if len(ulocations) >= 2:
            # photos
            print('# photos')
            photos = len(data)
            photo_ids = [x[2] for x in data]

            # time stuff
            print('# time stuff')
            times = [x[1] for x in data]
            times.sort()
            first_ts = min(times)
            last_ts = max(times)
            time_deltas = [times[i] - times[i - 1] for i in range(1, len(times))]
            mean_time_interval = sum(t for t in time_deltas) / len(time_deltas)

            # location stuff
            print(' # location stuff')
            loc_count = len(ulocations)
            freqs = {}
            for loc in ulocations:
                freqs[loc] = 0
            for loc in locations:
                freqs[loc] += 1
            links = itertools.combinations(ulocations, 2)

            distances = [geo.distance(self.locs[link[0]], self.locs[link[1]]) for link in links]
            mean_distance = sum(distances) / len(distances)

            total_dist = 0.
            count = 0
            for i in range(1, len(locations)):
                loc0 = locations[i - 1]
                loc1 = locations[i]
                if loc0 != loc1:
                    dist = geo.distance(self.locs[loc0], self.locs[loc1])
                    total_dist += dist
                    count += 1
            mean_weighted_dist = total_dist / count

            # comments
            print('# comments')
            self.db.cur.execute("SELECT count(id) FROM comment WHERE user=%s" % (user_id,))
            data = self.db.cur.fetchall()
            comments_given = data[0][0]
            comments_received = self.x_received('comment', photo_ids)

            # likes
            print('# likes')
            self.db.cur.execute("SELECT count(id) FROM likes WHERE user=%s" % (user_id,))
            data = self.db.cur.fetchall()
            likes_given = data[0][0]
            likes_received = self.x_received('comment', photo_ids)

            print('photos: %s; first_ts: %s; last_ts: %s; mean_time_interval: %s; loc_count: %s; mean_distance: %s; mean_weighted_distance: %s; comments_given: %s; comments_received: %s;  likes_given: %s; likes_received: %s'
                  % (photos, first_ts, last_ts, mean_time_interval, loc_count, mean_distance, mean_weighted_dist, comments_given, comments_received, likes_given, likes_received))


    def generate(self):
        print('computing user metrics.')
            
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

        print("done.")
