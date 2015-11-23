from phantomb.locmap import LocMap
import phantomb.geo as geo
import random


def comp_mean_dist(center, locs):
        total_distance = 0.0
        total_weight = 0.0
        for loc in locs:
            total_distance += geo.distance(center['pos'], loc['pos']) * loc['weight']
            total_weight += loc['weight']
        mean_dist = total_distance / total_weight
        center['mean_dist'] = mean_dist
        return mean_dist


class UserHome:
    def __init__(self, db):
        self.db = db
        self.locmap = LocMap(self.db)

    def update_users(self, updates):
        updates_params = [(update['pos']['lat'], update['pos']['lng'], update['location'], update['user'])
                          for update in updates]
        self.db.cur.executemany("UPDATE user SET homelat=%s, homelng=%s, home=%s WHERE id=%s", updates_params)
        self.db.conn.commit()

    def user_locations(self, user_id):
        self.db.cur.execute("SELECT location, weight, user FROM userlocation WHERE user=%s" % user_id)
        return self.db.cur.fetchall()

    def user_home(self, user_id):
        ulocs = self.user_locations(user_id)
        if len(ulocs) == 0:
            return None
        else:
            locs = [{'location': uloc[0],
                     'weight': uloc[1],
                     'user': uloc[2],
                     'pos': self.locmap.coords[uloc[0]]} for uloc in ulocs]
            best_mean_dist = float("inf")
            for loc in locs:
                md = comp_mean_dist(loc, locs)
                if md < best_mean_dist:
                    best_mean_dist = md
            best_locs = [loc for loc in locs if loc['mean_dist'] == best_mean_dist]
            return random.choice(best_locs)

    def generate(self):
        self.db.cur.execute("SELECT count(id) FROM user")
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)

        done = False
        n = 0

        while not done:
            self.db.cur.execute("SELECT id FROM user LIMIT %s,1000" % n)
            users = self.db.cur.fetchall()
            if len(users) == 0:
                done = True
            else:
                percent = (float(n) / float(nusers)) * 100.0
                updates = [self.user_home(user[0]) for user in users]
                updates = [update for update in updates if update]

                print("%s updates" % len(updates))
                self.update_users(updates)
                print("%s/%s (%s%%) processed" % (n, nusers, percent))
                n += len(users)

        print("done.")
