# generate home->home graph

import itertools


class LocsGraph2:
    def __init__(self, db, dbname):
        self.db = db
        self.dbname = dbname
        self.ll = {}

    def write_ll(self, csvpath):
        f = open(csvpath, 'w')
        f.write('orig,targ,weight\n')
        for k in self.ll:
            f.write('%s,%s,%s\n' % (k[0], k[1], self.ll[k]))        
        f.close()

    def process_link(self, link):
        v1 = link[0]
        v2 = link[1]
        if v1 > v2:
            v1 = link[1]
            v2 = link[0]
        l = (v1, v2)

        if l in self.ll:
            self.ll[l] += 1
        else:
            self.ll[l] = 1

    def target_home(self, media_id):
        self.db.cur.execute("SELECT user FROM media WHERE id=%s" % (media_id,))
        user_id = self.db.cur.fetchone()[0]
        self.db.cur.execute("SELECT home FROM user WHERE id=%s" % (user_id,))
        return self.db.cur.fetchone()[0]
            
    def process_user(self, user_id, home, table):
        self.db.cur.execute("SELECT media FROM %s WHERE user=%s" % (table, user_id))
        medias = self.db.cur.fetchall()
        medias = set([x[0] for x in medias])
        homes = [self.target_home(x) for x in medias]
        homes = [x for x in homes if x is not None]

        links = itertools.product([home], homes)

        for link in links:
            self.process_link(link)

    def generate(self, table):
        self.db.cur.execute("SELECT count(id) FROM user WHERE home IS NOT NULL")
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)
    
        done = False
        n = 0
        while not done:
            self.db.cur.execute(
                "SELECT id, home FROM user WHERE home IS NOT NULL LIMIT %s,1000" % n)
            users = self.db.cur.fetchall()
            if len(users) == 0:
                done = True
            else:
                percent = (float(n) / float(nusers)) * 100.0
                for user in users:
                    self.process_user(user[0], user[1], table)

                print("%s/%s (%s%%) processed" % (n, nusers, percent))
                n += len(users)

        suffix = 'home-home'
        self.write_ll("%s-%s.csv" % (self.dbname, suffix))
    
        print("done (%s)." % suffix)


