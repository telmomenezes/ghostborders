class CropData:
    def __init__(self, db, min_lat, min_lng, max_lat, max_lng):
        self.db = db
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lng = min_lng
        self.max_lng = max_lng

    def crop(self):
        print("removing photos ouside of crop region...")
        self.db.cur.execute("DELETE FROM media WHERE lat<%s OR lat>%s OR lng<%s OR lng>%s",
                            (self.min_lat, self.max_lat, self.min_lng, self.max_lng))
        self.db.conn.commit()

        print("removing locations ouside of crop region...")
        self.db.cur.execute("DELETE FROM location WHERE lat<%s OR lat>%s OR lng<%s OR lng>%s",
                            (self.min_lat, self.max_lat, self.min_lng, self.max_lng))
        self.db.conn.commit()

        print("removing orphan comments...")
        self.db.cur.execute("DELETE FROM comment WHERE NOT EXISTS(SELECT NULL FROM media WHERE media.id=media)")
        self.db.conn.commit()

        print("removing orphan likes...")
        self.db.cur.execute("DELETE FROM likes WHERE NOT EXISTS(SELECT NULL FROM media WHERE media.id=media)")
        self.db.conn.commit()

        print("removing orphan userlocations...")
        self.db.cur.execute(
            "DELETE FROM userlocation WHERE NOT EXISTS(SELECT NULL FROM location WHERE location.id=location)")
        self.db.conn.commit()

        print("removing orphan locationlocations (pass #1) ...")
        self.db.cur.execute(
            "DELETE FROM locationlocation WHERE NOT EXISTS(SELECT NULL FROM location WHERE location.id=loc1)")
        self.db.conn.commit()

        print("removing orphan locationlocations (pass #2) ...")
        self.db.cur.execute(
            "DELETE FROM locationlocation WHERE NOT EXISTS(SELECT NULL FROM location WHERE location.id=loc2)")
        self.db.conn.commit()

        print("done.")
