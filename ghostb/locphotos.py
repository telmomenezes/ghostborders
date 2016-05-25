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


class LocPhotos:
    def __init__(self, db):
        self.db = db
        self.densities = {}
        self.locmap = LocMap(self.db)

    def update_densities(self, loc):
        if loc in self.densities:
            self.densities[loc] += 1
        else:
            self.densities[loc] = 1

    def update(self):
        print('generating densities table')
        n = 0
        while True:
            photos = self.db.query("SELECT location FROM media LIMIT %s, 10000" % (n,))
            if len(photos) == 0:
                break
            n += len(photos)
            photo_locs = [x[0] for x in photos]
            for loc in photo_locs:
                self.update_densities(loc)

        self.db.open()
        print('resetting #photos per location')
        self.db.cur.execute('UPDATE location SET photos=0')
        print('updating #photos per location')
        updates_params = [(self.densities[key], key) for key in self.densities]
        self.db.cur.executemany("UPDATE location SET photos=%s WHERE id=%s",
                                updates_params)
        self.db.conn.commit()
        print('done.')
