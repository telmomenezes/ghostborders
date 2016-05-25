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


import csv
import ghostb.region_defs


def safe_unicode(obj, *args):
    # return the unicode representation of obj
    try:
        return str(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return str(ascii_text)


class Locations:
    def __init__(self, db):
        self.db = db

    def insert_location(self, country, name, lat, lng):
        print(">>> %s %s %f %f" % (country, name, lat, lng))
        self.db.cur.execute("SELECT id FROM location WHERE country=%s AND name=%s", (country, name))
        row = self.db.cur.fetchone()
        if row is None:
            self.db.cur.execute("INSERT INTO location (country, name, lat, lng, done) VALUES (%s, %s, %s, %s, 0)",
                                (country, name, lat, lng))
            print("inserted.")
            return True
        return False

    def add_locations(self, locs_file, country_code):
        points = set()

        with open(locs_file) as infile:
            reader = csv.reader(infile, delimiter='\t', quoting=csv.QUOTE_NONE)
            for row in reader:
                if row[8] == country_code:
                    p = (float(row[4]), float(row[5]), row[2])
                    points.add(p)

        inserted = 0
        for p in points:
            if self.insert_location(country_code, safe_unicode(p[2]), p[0], p[1]):
                inserted += 1

        self.db.conn.commit()

        return len(points), inserted

    def add_area(self, locs_file, min_lat, min_lng, max_lat, max_lng):
        points = set()

        with open(locs_file) as infile:
            reader = csv.reader(infile, delimiter='\t', quoting=csv.QUOTE_NONE)
            for row in reader:
                p = (float(row[4]), float(row[5]), row[2], row[8])
                if (p[0] >= min_lat) and (p[0] <= max_lat) and (p[1] >= min_lng) and (p[1] <= max_lng):
                    points.add(p)

        inserted = 0
        for p in points:
            if self.insert_location(p[3], safe_unicode(p[2]), p[0], p[1]):
                inserted += 1

        self.db.conn.commit()

        return len(points), inserted

    def add_grid(self, min_lat, min_lng, max_lat, max_lng, rows, cols):
        delta_lat = (max_lat - min_lat) / rows
        delta_lng = (max_lng - min_lng) / cols

        for i in range(1, rows):
            lat = i * delta_lat + min_lat
            for j in range(1, cols):
                lng = j * delta_lng + min_lng
                name = 'node_%s_%s' % (i, j)
                self.insert_location('grid', name, lat, lng)

        self.db.conn.commit()

    def add_region_grid(self, region, rows, cols):
        coords = ghostb.region_defs.region_coords[region]
        self.add_grid(coords[0], coords[1], coords[2], coords[3], rows, cols)
        
    def clean(self):
        self.db.cur.execute("DELETE FROM location")
        self.db.conn.commit()
