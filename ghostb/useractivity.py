class UserActivity:
    def __init__(self, db):
        self.db = db

    def update_user_activity(self, updates):
        args = [(x['first_ts'], x['last_ts'], x['photos'], x['id']) for x in updates]
        self.db.cur.executemany("UPDATE user SET first_ts=%s, last_ts=%s, photos=%s WHERE id=%s", args)
        self.db.conn.commit()

    def user_activity(self, user_id):
        self.db.cur.execute("SELECT ts FROM media WHERE user=%s" % user_id)
        medias = self.db.cur.fetchall()

        nphotos = len(medias)
        if len(medias) > 0:
            ts_seq = [media[0] for media in medias]
            min_ts = min(ts_seq)
            max_ts = max(ts_seq)
            return {'user': user_id,
                    'first_ts': min_ts,
                    'last_ts': max_ts,
                    'photos': nphotos}
        return None

    def update(self):
        self.db.cur.execute("SELECT count(id) as c FROM user")
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)

        n = 0
        while True:
            self.db.cur.execute("SELECT id FROM user LIMIT %s, 10000" % n)
            users = self.db.cur.fetchall()
            if len(users) == 0:
                break
        
            n += len(users)
            percent = 100.0 * float(n) / float(nusers)
            ups = [self.user_activity(x[0]) for x in users]
            ups = [x for x in ups if x is not None]
            self.update_user_activity(ups)
            print("%s / %s ( %s %%) processed" % (n, nusers, percent))

        print("done.")
