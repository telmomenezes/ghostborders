class Flag:
    def __init__(self, db):
        self.db = db

    def update_users(self, updates):
        updates_params = [(update,) for update in updates]
        self.db.cur.executemany("UPDATE user SET flag=1 WHERE id=%s", updates_params)
        self.db.conn.commit()

    def flag_status(self, user_id, first_ts, last_ts, photos):
        MIN_TIME = 30 * 24 * 60 * 60
        MIN_PHOTOS = 2
        if (last_ts - first_ts) < MIN_TIME:
            return None
        elif photos < MIN_PHOTOS:
            return None
        else:
            return user_id

    def flag(self):
        self.db.cur.execute("SELECT count(id) FROM user")
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)

        done = False
        n = 0
        flagged = 0

        while not done:
            self.db.cur.execute("SELECT id, first_ts, last_ts, photos FROM user LIMIT %s,1000" % n)
            users = self.db.cur.fetchall()
            if len(users) == 0:
                done = True
            else:
                percent = (float(n) / float(nusers)) * 100.0
                updates = [self.flag_status(user[0], user[1], user[2], user[3]) for user in users]
                updates = [update for update in updates if update]

                flagged += len(updates)
                print("%s updates" % len(updates))
                self.update_users(updates)
                print("%s/%s (%s%%) processed" % (n, nusers, percent))
                n += len(users)

        flag_perc = (float(flagged) / float(nusers)) * 100.
        print('%s users flagged out of %s [%s%%]' % (flagged, nusers, flag_perc))
        print("done.")

    def unflag(self):
        self.db.cur.execute("UPDATE user SET flag=0")
        self.db.conn.commit()
