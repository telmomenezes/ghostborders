from ghostb.locmap import LocMap


class PhotoDensity:
    def __init__(self, db):
        self.db = db
        self.densities = {}
        self.locmap = LocMap(self.db)

    def update_densities(self, loc):
        if loc in self.densities:
            self.densities[loc] += 1
        else:
            self.densities[loc] = 1

    def generate(self):
        # generate densities table
        n = 0
        while True:
            photos = self.db.query("SELECT location FROM media LIMIT %s, 10000" % (n,))
            if len(photos) == 0:
                break
            n += len(photos)
            photo_locs = [x[0] for x in photos]
            for loc in photo_locs:
                self.update_densities(loc)

        # output csv
        print('lat,lng,count')
        for key in self.densities:
            print('%s,%s,%s' % (self.locmap.coords[key]['lat'], self.locmap.coords[key]['lng'], self.densities[key]))
