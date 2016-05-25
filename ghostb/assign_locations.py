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


class AssignLocations:
    def __init__(self, db, table):
        self.db = db
        self.table = table

    def update_locations(self, updates):
        args = [(self.table, x['location'], x['ts'], x['id']) for x in updates]
        self.db.cur.executemany("UPDATE %s SET location=%s, ts=%s WHERE id=%s", args)
        self.db.conn.commit()

    def extra_data(self, comment_id, media_id):
        self.db.cur.execute("SELECT location, ts FROM media WHERE id=%s", (media_id,))
        media = self.db.cur.fetchone()
        return {'id': comment_id, 'location': media[0], 'ts': media[1]}

    def fix(self):
        print("assigning locations for: %s" % self.table)
        self.db.cur.execute("SELECT count(id) as c FROM %s", (self.table,))
        nitems = self.db.cur.fetchone()[0]
        print("%s items to process" % ncomms)
  
        n = 0
        while True:
            self.db.cur.execute("SELECT id, media FROM %s ORDER BY id LIMIT %s, 1000",
                                (self.table, n))
            items = self.db.cur.fetchall()
            if len(items) == 0:
                break
            ups = [self.extra_data(x[0], x[1]) for x in items]
            self.update_locations(ups)

            print("%s/%s (%s%%) processed" %
                  (n, nitems, (100.0 * float(n) / float(nitems))))
            n += len(items)

        print("done.")
