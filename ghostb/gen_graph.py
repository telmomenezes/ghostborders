# graph types:
# loc2loc, home2loc, home2home

import sys
import itertools


class GenGraph:
    def __init__(self, db, outfile, graph_type, flagged):
        if graph_type == 'loc2loc':
            self.table = 'media'
        elif graph_type == 'home2loc':
            self.table = 'media'
        elif graph_type == 'home2home':
            self.table = 'comment'
        else:
            print('unknown graph type: %s' % self.graph_type)
            sys.exit(-1)

        self.db = db
        self.outfile = outfile
        self.graph_type = graph_type
        self.flagged = flagged
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

    def process_user_loc2loc(self, user_id, home):
        self.db.cur.execute("SELECT location FROM %s WHERE user=%s" % (self.table, user_id))
    
        locations = self.db.cur.fetchall()
        locations = [x[0] for x in locations]

        freqs = {}
        for l in locations:
            if l in freqs:
                freqs[l] += 1
            else:
                freqs[l] = 1

        # make locations unique
        locations = set(locations)

        links = itertools.combinations(locations, 2)

        for link in links:
            self.process_link(link)

        # create self-loops for locations where a single user has more than one event
        for l in freqs:
            if freqs[l] > 1:
                self.process_link([l , l])

    def process_user_home2loc(self, user_id, home):
        self.db.cur.execute("SELECT location FROM %s WHERE user=%s" % (self.table, user_id))
    
        locations = self.db.cur.fetchall()
        locations = [x[0] for x in locations]

        freqs = {}
        for l in locations:
            if l in freqs:
                freqs[l] += 1
            else:
                freqs[l] = 1

        # make locations unique
        locations = set(locations)

        links = itertools.product([home], locations)

        for link in links:
            self.process_link(link)

        # create self-loops for locations where a single user has more than one event
        for l in freqs:
            if freqs[l] > 1:
                self.process_link([l , l])

    def target_home(self, media_id):
        self.db.cur.execute("SELECT user FROM media WHERE id=%s" % (media_id,))
        user_id = self.db.cur.fetchone()[0]
        self.db.cur.execute("SELECT home FROM user WHERE id=%s" % (user_id,))
        return self.db.cur.fetchone()[0]
            
    def process_user_home2home(self, user_id, home):
        self.db.cur.execute("SELECT media FROM %s WHERE user=%s" % (self.table, user_id))
        medias = self.db.cur.fetchall()
        medias = set([x[0] for x in medias])
        homes = [self.target_home(x) for x in medias]
        homes = [x for x in homes if x is not None]

        links = itertools.product([home], homes)

        for link in links:
            self.process_link(link)

    def process_user(self, user_id, home):
        if self.graph_type == 'loc2loc':
            self.process_user_loc2loc(user_id, home)
        elif self.graph_type == 'home2home':
            self.process_user_home2home(user_id, home)
                
    def generate(self):
        print('generating graph with type: %s' % self.graph_type)

        where_clause = ''
        if self.flagged:
            print('processing only flagged users')
            where_clause = 'WHERE flag > 0'
        else:
            print('processing all users')
        
        self.db.cur.execute("SELECT count(id) FROM user %s" % where_clause)
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)
    
        done = False
        n = 0
        while not done:
            self.db.cur.execute("SELECT id, home FROM user %s LIMIT %s,1000" % (where_clause, n))
            users = self.db.cur.fetchall()
            if len(users) == 0:
                done = True
            else:
                percent = (float(n) / float(nusers)) * 100.0
                for user in users:
                    self.process_user(user[0], user[1])

                print("%s/%s (%s%%) processed" % (n, nusers, percent))
                n += len(users)

        self.write_ll(self.outfile)
    
        print("done.")
