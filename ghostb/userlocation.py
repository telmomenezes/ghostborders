class UserLocation:
    def __init__(self, db):
        self.db = db
        
    def generate_user_locations(self, user_id):
        self.db.cur.execute("SELECT location FROM media WHERE user=%s" % user_id)
        medias = self.db.cur.fetchall()
        locations = [x[0] for x in medias]
        freqs = {}
        for l in locations:
            if l in freqs:
                freqs[l] += 1
            else:
                freqs[l] = 1
        total = float(len(locations))
        for l in freqs:
            self.db.cur.execute("INSERT INTO userlocation (location, weight, w) VALUES (%s, %s, %s)" % (l, freqs[l], freqs[l] / total))
        self.db.conn.commit()

    def generate(self):
        self.db.cur.execute("SELECT count(id) FROM user WHERE photos > 4")
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)

        done = False
        n = 0

        while not done:
            self.db.cur.execute("SELECT id FROM user WHERE photos > 4 LIMIT %s,1000" % n)
            users = self.db.cur.fetchall()
            if len(users) == 0:
                done = True
            else:
                percent = (float(n) / float(nusers)) * 100.0
                for user in users:
                    self.generate_user_locations(user[0])
                print("%s/%s (%s%%) processed" % (n, nusers, percent))
                n += len(users)

        print("done.")
