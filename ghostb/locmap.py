class LocMap:
    def __init__(self, db):
        db.cur.execute("SELECT id,lat,lng,photos FROM location")
        loctable = db.cur.fetchall()
        self.coords = {}
        for loc in loctable:
            self.coords[loc[0]] = {'lat': loc[1],
                                   'lng': loc[2],
                                   'photos': loc[3]}
