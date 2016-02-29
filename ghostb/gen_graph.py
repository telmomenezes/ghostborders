import sys
import itertools
from ghostb.locmap import LocMap
import ghostb.geo as geo


def time_delta(link, loc_ts):
    min_delta = -1
    for ts1 in loc_ts[link[0]]:
        for ts2 in loc_ts[link[1]]:
            if ts1 != ts2:
                delta = abs(ts1 - ts2)
                if (min_delta < 0) or (delta < min_delta):
                    min_delta = delta
    return min_delta


class GenGraph:
    def __init__(self, db, graph_file, dist_file, max_time=-1):
        self.db = db
        self.max_time = max_time
        self.write_graph = False
        self.write_dist = False
        if graph_file != '':
            self.graph_file = graph_file
            self.write_graph = True
            self.ll = {}
        if dist_file != '':
            self.f_dist = open(dist_file, 'w')
            self.f_dist.write('distance,time\n')
            self.write_dist = True
            self.locmap = LocMap(db)
        

    def write_ll(self):
        f = open(self.graph_file, 'w')
        f.write('orig,targ,weight\n')
        for k in self.ll:
            f.write('%s,%s,%s\n' % (k[0], k[1], self.ll[k]))
        f.close()

    def process_link(self, link, time):
        v1 = link[0]
        v2 = link[1]
        if v1 > v2:
            v1 = link[1]
            v2 = link[0]
        l = (v1, v2)

        if self.write_graph:
            if (self.max_time < 0) or (time <= self.max_time):
                if l in self.ll:
                    self.ll[l] += 1
                else:
                    self.ll[l] = 1

        if self.write_dist:
            loc1 = self.locmap.coords[l[0]]
            loc2 = self.locmap.coords[l[1]]
            dist = geo.distance(loc1, loc2)
            if (time > 0) and (dist > 0):
                self.f_dist.write('%s,%s\n' % (dist, time))
            else:
                print('%s,%s\n' % (dist, time))
        
    def process_user(self, user_id):
        self.db.cur.execute("SELECT location, ts FROM media WHERE user=%s" % user_id)
        data = self.db.cur.fetchall()
        locations = [x[0] for x in data]

        loc_ts = {}
        for x in data:
            loc = x[0]
            ts = x[1]
            if loc in loc_ts:
                loc_ts[loc].append(ts)
            else:
                loc_ts[loc] = [ts,]
        
        #freqs = {}
        #for l in locations:
        #    if l in freqs:
        #        freqs[l] += 1
        #    else:
        #        freqs[l] = 1

        # make locations unique
        locations = set(locations)

        links = itertools.combinations(locations, 2)

        for link in links:
            time = time_delta(link, loc_ts)
            self.process_link(link, time)

        # create self-loops for locations where a single user has more than one event
        #for l in freqs:
        #    if freqs[l] > 1:
        #        self.process_link([l , l], loc_ts)

    def generate(self):
        if self.write_graph:
            print('generating graph.')
        if self.write_dist:
            print('generating distance/time link distribution.')

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
                for user in users:
                    self.process_user(user[0])

                print("%s/%s (%s%%) processed" % (n, nusers, percent))
                n += len(users)

        if self.write_graph:
            self.write_ll()
        if self.write_dist:
            self.f_dist.close()
    
        print("done.")