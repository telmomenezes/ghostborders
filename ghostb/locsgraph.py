import itertools
import ghostb.monthly as monthly


class LocsGraph:
    def __init__(self, db, dbname, directed):
        self.db = db
        self.dbname = dbname
        self.directed = directed
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
        if (not self.directed) and (v1 > v2):
            v1 = link[1]
            v2 = link[0]
        l = (v1, v2)

        if l in self.ll:
            self.ll[l] += 1
        else:
            self.ll[l] = 1

    def process_user(self, user_id, home, month, table):
        if month:
            ts0 = monthly.month_start(month)
            ts1 = monthly.month_end(month)
            self.db.cur.execute("SELECT location FROM %s WHERE user=%s AND ts>=%s AND ts<%s"
                                % (table, user_id, ts0, ts1))
        else:
            self.db.cur.execute("SELECT location FROM %s WHERE user=%s" % (table, user_id))
    
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

        if self.directed:
            links = itertools.product([home], locations)
        else:
            links = itertools.combinations(locations, 2)

        for link in links:
            self.process_link(link)

        # create self-loops for locations where a single user has more than one event
        for l in freqs:
            if freqs[l] > 1:
                self.process_link([l , l])

    def generate_graph(self, table, month=None):
        self.db.cur.execute("SELECT count(id) FROM user")
        nusers = self.db.cur.fetchone()[0]
        print("%s users to process" % nusers)
    
        done = False
        n = 0
        while not done:
            self.db.cur.execute("SELECT id, home FROM user LIMIT %s,1000" % n)
            users = self.db.cur.fetchall()
            if len(users) == 0:
                done = True
            else:
                percent = (float(n) / float(nusers)) * 100.0
                for user in users:
                    self.process_user(user[0], user[1], month, table)

                print("%s/%s (%s%%) processed" % (n, nusers, percent))
                n += len(users)

        suffix = 'full'
        if month:
            suffix = month
        if self.directed:
            suffix += '-home'
        self.write_ll("%s-%s.csv" % (self.dbname, suffix))
    
        print("done (%s)." % suffix)

    def generate_full(self, table):
        self.generate_graph(table)

    def generate_months(self, table):
        self.db.cur.execute("SELECT id FROM month")
        months = self.db.cur.fetchall()
        months = [x[0] for x in months]

        for month in months:
            print('generating graph for month: %s' % month)
            self.generate_graph(table, month)

    def generate(self, table, bymonth=False):
        if bymonth:
            self.generate_months(table)
        else:
            self.generate_full(table)
