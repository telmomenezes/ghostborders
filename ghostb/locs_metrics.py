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


class LocsMetrics:
    def __init__(self, db):
        self.db = db
        self.locmap = LocMap(db).coords
        self.ll = {}
        for loc in self.locmap:
            self.locmap[loc]['photos'] = 0
            self.locmap[loc]['users'] = set()
            self.locmap[loc]['dist'] = 0.
            self.locmap[loc]['time'] = 0.
            self.locmap[loc]['degree'] = 0
            self.locmap[loc]['neighbors'] = 0
            self.locmap[loc]['self'] = 0
        

    def post_process(self):
        for loc in self.locmap:
            degree = self.locmap[loc]['degree']
            if degree > 0:
                self.locmap[loc]['dist'] /= degree
                self.locmap[loc]['time'] /= degree
            self.locmap[loc]['users'] = len(self.locmap[loc]['users'])
            
    def write_data(self, outfile):
        f = open(outfile, 'w')
        f.write('loc,lat,lng,photos,users,dist,time,degree,neighbors,self\n')
        for loc in self.locmap:
            lm = self.locmap[loc]
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' %
                    (loc, lm['lat'], lm['lng'], lm['photos'], lm['users'], lm['dist'],
                     lm['time'], lm['degree'], lm['neighbors'], lm['self']))
        f.close()

    def process_link(self, link, time):
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
            self.locmap[v1]['neighbors'] += 1
            self.locmap[v2]['neighbors'] += 1

        self.locmap[v1]['degree'] += 1
        self.locmap[v2]['degree'] += 1

        loc1 = self.locmap[v1]
        loc2 = self.locmap[v2]
        dist = geo.distance(loc1, loc2)
        self.locmap[v1]['dist'] += dist
        self.locmap[v2]['dist'] += dist

        t = float(time) / 60.
        t /= 60.
        t /= 24.
        self.locmap[v1]['time'] += t
        self.locmap[v2]['time'] += t
        
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
        
        freqs = {}
        for l in locations:
            if l in freqs:
                freqs[l] += 1
            else:
                freqs[l] = 1

        # make locations unique
        locations = set(locations)

        # add user to location's user list
        for loc in locations:
            self.locmap[loc]['users'].add(user_id)

        links = itertools.combinations(locations, 2)

        for link in links:
            time = time_delta(link, loc_ts)
            self.process_link(link, time)

        # create self-loops for locations where a single user has more than one event
        for l in freqs:
            self.locmap[l]['photos'] += freqs[l]
            if freqs[l] > 1:
                self.locmap[l]['self'] += 1

    def generate(self, outfile):
        print('generating location metrics.')

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

        self.post_process()
        self.write_data(outfile)
    
        print("done.")
