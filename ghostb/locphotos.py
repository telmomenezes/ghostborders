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
