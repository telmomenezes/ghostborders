class CommentLocations:
    def __init__(self, db):
        self.db = db

    def update_locations(self, updates):
        args = [(x['location'], x['ts'], x['id']) for x in updates]
        self.db.cur.executemany("UPDATE comment SET location=%s, ts=%s WHERE id=%s", args)
        self.db.conn.commit()

    def extra_data(self, comment_id, media_id):
        self.db.cur.execute("SELECT location, ts FROM media WHERE id=%s", (media_id,))
        media = self.db.cur.fetchone()
        return {'id': comment_id, 'location': media[0], 'ts': media[0]}

    def fix(self):
        print("fixing comments")
        self.db.cur.execute("SELECT count(id) as c FROM comment")
        ncomms = self.db.cur.fetchone()[0]
        print("%s comments to process" % ncomms)
  
        n = 0
        while True:
            self.db.cur.execute("SELECT id, media FROM comment ORDER BY id LIMIT %s, 1000", (n,))
            comments = self.db.cur.fetchall()
            if len(comments) == 0:
                break
            ups = [self.extra_data(x[0], x[1]) for x in comments]
            self.update_locations(ups)

            print("%s/%s (%s%%) processed" % (n, ncomms, (100.0 * float(n) / float(ncomms))))
            n += len(comments)

        print("done.")
