import math
import sys


def modes(comms):
    distrib = {}
    for comm in comms:
        if comm in distrib:
            distrib[comm] += 1
        else:
            distrib[comm] = 1
    maxfq = max(distrib.values())
    return [comm for comm in distrib if distrib[comm] == maxfq]


class Partition:
    def __init__(self, vor, path):
        self.vor = vor

        # init comms
        self.comms = {}
        for loc in self.vor.locmap.coords:
            self.comms[loc] = -1

        # read communities from csv
        lines = [line.rstrip('\n') for line in open(path)]
        del lines[0]
        for line in lines:
            cols = line.split(',')
            self.comms[int(cols[0])] = int(cols[1])

    def comm(self, loc):
        if loc in self.comms:
            return self.comms[loc]
        else:
            return -1

    # find the mode community for a given location and its neighbors
    # in case of a tie, uses the largest community
    def mode_community(self, loc, comm_sizes):
        ids = [loc]
        if loc in self.vor.neighbors:
            ids += self.vor.neighbors[loc]
        comms = [self.comms[x] for x in ids]
        cmodes = modes(comms)
        best_mode = None
        best_size = 0
        for mode in cmodes:
            size = comm_sizes[mode]
            if size > best_size:
                best_size = size
                best_mode = mode
        return best_mode

    # compute map of size by community
    def map2community_sizes(self):
        comm_sizes = {}
        for key in self.comms:
            comm = self.comms[key]
            if comm in comm_sizes:
                comm_sizes[comm] += 1
            else:
                comm_sizes[comm] = 1
        return comm_sizes

    # set community to the most frequent value in its neighbors (including itself)
    # in case of a tie, choose the largest community
    def smooth(self):
        comm_sizes = self.map2community_sizes()
        updates = 0
        for loc in self.comms:
            comm = self.mode_community(loc, comm_sizes)
            if self.comms[loc] != comm:
                self.comms[loc] = comm
                updates += 1
        return updates

    # run smoothing algortihm until stable
    def smooth_until_stable(self):
        i = 0
        while True:
            i += 1
            updates = self.smooth()
            #print('smoothing pass %s, %s updates.' % (i, updates))
            if updates == 0:
                return
        
    def loc_dist(self, part, loc1, loc2):
        comm1a = self.comm(loc1)
        comm2a = self.comm(loc2)
        comm1b = part.comm(loc1)
        comm2b = part.comm(loc2)
        if (comm1a == comm2a) == (comm1b == comm2b):
            return 0.
        else:
            return 1.

    # compute Rand index
    # https://en.wikipedia.org/wiki/Rand_index
    def distance(self, part):
        locs = set([loc for loc in self.comms] + [loc for loc in part.comms])
        count = 0.
        dist = 0.
        for loc1 in locs:
            for loc2 in locs:
                if loc2 > loc1:
                    count += 1.
                    dist += self.loc_dist(part, loc1, loc2)
        return dist / count

    def freqs(self):
        freqs = {}
        for loc in self.comms:
            comm = self.comms[loc]
            if comm in freqs:
                freqs[comm] += 1.
            else:
                freqs[comm] = 1.

        total = float(len(self.comms))
        for comm in freqs:
            freqs[comm] /= total

        return freqs
    
    # compute information entropy
    def entropy(self):
        freqs = self.freqs()
        h = 0.
        for comm in freqs:
            p = freqs[comm]
            h -= p * math.log(p)
        return h

    # compute Herfindahl index
    # https://en.wikipedia.org/wiki/Herfindahl_index
    def herfindahl(self):
        freqs = self.freqs()
        h = 0.
        for comm in freqs:
            p = freqs[comm]
            h += p * p
        return h

    # number of communities
    def count(self):
        freqs = self.freqs()
        return float(len(freqs))
    
    def metric(self, metric):
        if metric == 'entropy':
            return self.entropy()
        elif metric == 'herfindahl':
            return self.herfindahl()
        elif metric == 'count':
            return self.count()
        else:
            print('unknown metric: %s' % metric)
            sys.exit()
