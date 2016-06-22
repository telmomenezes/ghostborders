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


import ghostb.region_defs


def crop_rectangle(db, min_lat, min_lng, max_lat, max_lng):
    print("removing photos ouside of crop region...")
    db.cur.execute("DELETE FROM media WHERE lat<%s OR lat>%s OR lng<%s OR lng>%s",
                   (min_lat, max_lat, min_lng, max_lng))
    db.conn.commit()

    print("removing locations ouside of crop region...")
    db.cur.execute("DELETE FROM location WHERE lat<%s OR lat>%s OR lng<%s OR lng>%s",
                   (min_lat, max_lat, min_lng, max_lng))
    db.conn.commit()

    print("done.")


def crop_region(db, region):
    coords = ghostb.region_defs.region_coords[region]
    crop_rectangle(db, coords[0], coords[1], coords[2], coords[3])
