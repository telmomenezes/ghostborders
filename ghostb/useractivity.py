class UserActivity:
    def __init__(self, db):
        self.db = db

    def __update_user_activity(self, user_id):
        self.db.cur.execute("SELECT ts FROM media WHERE user=%s" % user_id)
        medias = self.db.cur.fetchall()

        nphotos = len(medias)
        if len(medias) > 0:
            ts_seq = [media[0] for media in medias]
            min_ts = min(ts_seq)
            max_ts = max(ts_seq)
            self.db.cur.execute("UPDATE user SET first_ts=%s, last_ts=%s, photos=%s WHERE id=%s"
                                % (min_ts, max_ts, nphotos, user_id))
            self.db.conn.commit()

    def update(self):
        self.db.cur.execute("SELECT count(id) as c FROM user")
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)

        n = 0
        while True:
            self.db.cur.execute("SELECT id FROM user LIMIT %s, 1000" % n)
            users = self.db.cur.fetchall()
            if len(users) == 0:
                break
        
            n += len(users)
            percent = 100.0 * float(n) / float(nusers)
            for user in users:
                self.__update_user_activity(user[0])
            print("%s / %s ( %s %%) processed" % (n, nusers, percent))

        print("done.")
