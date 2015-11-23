from ghostb.locmap import LocMap
import ghostb.geo as geo


def comp_mean_dist(center, locs):
    total_distance = 0.0
    for loc in locs:
        total_distance += geo.distance(center, loc)
    return total_distance / float(len(locs))


class Distances:
    def __init__(self, db):
        self.db = db
        self.locmap = LocMap(self.db)

    def user_mean_dist(self, user_id, home, table):
        self.db.cur.execute("SELECT location FROM %s WHERE user=%s" % (table, user_id))
        locs = self.db.cur.fetchall()
        if len(locs) > 0:
            locs = [self.locmap.coords[x[0]] for x in locs]
            return comp_mean_dist(home, locs)
        else:
            return 0.0

    def compute(self, table):
        self.db.cur.execute("SELECT count(id) FROM user")
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)
    
        done = False
        n = 0
        active_users = 0
        total_mean_dist = 0.0
        while not done:
            self.db.cur.execute("SELECT id, home FROM user LIMIT %s,1000" % n)
            users = self.db.cur.fetchall()
            if len(users) == 0:
                done = True
            else:
                percent = (float(n) / float(nusers)) * 100.0
                for user in users:
                    if user[1] is not None:
                        home = self.locmap.coords[user[1]]
                        user_id = user[0]
                        mean_dist = self.user_mean_dist(user_id, home, table)
                        if mean_dist > 0.0:
                            active_users += 1
                            total_mean_dist += mean_dist
                            print("user %s mean distance: %s" % (user_id, mean_dist))

                print("%s/%s (%s%%) processed" % (n, nusers, percent))
                n += len(users)

        total_mean_dist /= float(active_users)
        print("Total mean distance: %s" % total_mean_dist)

        print("done.")
