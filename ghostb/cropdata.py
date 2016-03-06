import ghostb.region_defs


def crop_rectangle(db, min_lat, min_lng, max_lat, max_lng):
    print("removing photos ouside of crop region...")
    db.cur.execute("DELETE FROM media WHERE lat<%s OR lat>%s OR lng<%s OR lng>%s",
        (min_lat, max_lat, min_lng, max_lng))
    self.db.conn.commit()

    print("removing locations ouside of crop region...")
    db.cur.execute("DELETE FROM location WHERE lat<%s OR lat>%s OR lng<%s OR lng>%s",
        (min_lat, max_lat, min_lng, max_lng))
    self.db.conn.commit()

    print("done.")


def crop_region(db, region):
    coords = ghostb.region_defs.region_coords[region]
    crop_rectangle(db, coords[0], coords[1], coords[2], coords[3])
