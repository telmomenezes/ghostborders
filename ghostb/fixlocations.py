import ghostb.geo


def nearest(photo, locs):
    new_loc = {
        'location': -1,
        'dist': 9999999
    }

    for loc in locs:
        dist = ghostb.geo.distance(photo, loc)
        if dist < new_loc['dist']:
            new_loc['id'] = loc['id']
            new_loc['dist'] = dist

    return new_loc


def fixed_location(photo, locs):
    new_loc = nearest(photo, locs)
    if photo['location'] != new_loc['id']:
        return {
            'location': new_loc['id'],
            'id': photo['id']
        }
    else:
        return None


class FixLocations:
    def __init__(self, db):
        self.db = db

    def update_locations(self, updates):
        args = [(x['location'], x['id']) for x in updates]
        self.db.cur.executemany("UPDATE media SET location=%s WHERE id=%s", args)
        self.db.conn.commit()

    def run(self):
        self.db.cur.execute("SELECT id, lat, lng FROM location")
        locs = self.db.cur.fetchall()
        locs = [{'id': x[0], 'lat': x[1], 'lng': x[2]} for x in locs]

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

            ups = [fixed_location(x, locs) for x in photos]
            ups = [x for x in ups if x is not None]
            self.update_locations(ups)
            print("number of updates: %s" % len(ups))
            print("%s/%s (%s%%) processed" % (n, nphotos, (100.0 * float(n) / float(nphotos))))
            n += len(photos)

        print("done.")
