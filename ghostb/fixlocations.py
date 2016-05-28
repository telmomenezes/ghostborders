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


import ghostb.geo
from ghostb.locmap import LocMap


class FixLocations:
    def __init__(self, db):
        self.db = db
        locmap = LocMap(db)
        self.locs = locmap.coords

    def nearest(self, photo):
        new_loc = {
            'location': -1,
            'dist': 9999999
        }

        for loc in self.locs:
            dist = ghostb.geo.distance(photo, self.locs[loc])
            if dist < new_loc['dist']:
                new_loc['id'] = loc
                new_loc['dist'] = dist

        return new_loc


    def fixed_location(self, photo):
        new_loc = self.nearest(photo)
        if photo['location'] != new_loc['id']:
            return {
                'location': new_loc['id'],
                'id': photo['id']
            }
        else:
            return None

    def update_locations(self, updates):
        args = [(x['location'], x['id']) for x in updates]
        self.db.cur.executemany("UPDATE media SET location=%s WHERE id=%s", args)
        self.db.conn.commit()

    def run(self, update):
        self.db.cur.execute("SELECT count(id) as c FROM media")
        nphotos = self.db.cur.fetchone()[0]
        print("%s photos to process" % nphotos)

        n = 0
        while True:
            self.db.cur.execute("SELECT id, location, lat, lng FROM media LIMIT %s, 1000", (n,))
            photos = self.db.cur.fetchall()
            photos = [{'id': x[0], 'location': x[1], 'lat': x[2], 'lng': x[3]} for x in photos]
            if len(photos) == 0:
                break

            # unly reassing for inactive locations
            if update:
                photos = [photo for photo in photos if photo['location'] not in self.locs]

            ups = [self.fixed_location(x) for x in photos]
            ups = [x for x in ups if x is not None]
            self.update_locations(ups)
            n += len(photos)
            print("number of updates: %s" % len(ups))
            print("%s/%s (%s%%) processed" % (n, nphotos, (100.0 * float(n) / float(nphotos))))

        print("done.")
