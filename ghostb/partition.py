#   Copyright (c) 2016 Centre Marc Bloch Berlin
#   (An-Institut der Humboldt Universität, UMIFRE CNRS-MAE).
#   All rights reserved.
#
#   Written by Telmo Menezes <telmo@telmomenezes.com>
#
#   This file is part of GhostBorders.
#
#   GhostBorders is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   GhostBorders is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with GhostBorders.  If not, see <http://www.gnu.org/licenses/>.


import math
import sys
import numpy as np


def modes(comms):
    distrib = {}
    for comm in comms:
        if comm in distrib:
            distrib[comm] += 1
        else:
            distrib[comm] = 1
    maxfq = max(distrib.values())
    return [comm for comm in distrib if distrib[comm] == maxfq]


def read(path, comms={}):
    # read communities from csv
    lines = [line.rstrip('\n') for line in open(path)]
    del lines[0]
    for line in lines:
        cols = line.split(',')
        comms[int(cols[0])] = int(cols[1])
    return comms


def community(partitions, partition_index, loc_id):
    comms = partitions[partition_index].comms
    if loc_id in comms:
        return comms[loc_id]
    else:
        return -1


class Partition:
    def __init__(self, vor, singletons=True):
        self.vor = vor

        # init comms
        self.comms = {}
        singleton_id = -1
        for loc in self.vor.locmap.coords:
            self.comms[loc] = singleton_id
            if singletons:
                singleton_id -= 1

        # init comm x comm
        self.commxcomm = None

    def read(self, path):
        self.comms = read(path, self.comms)

    def combine(self, pars):
        npars = len(pars)
        for loc_id in self.vor.locmap.coords:
            self.comms[loc_id] = tuple([community(pars, i, loc_id) for i in range(npars)])
            
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
        
    def init_commxcomm(self):
        if self.commxcomm is None:
            commxcomm = []
            locs = self.comms
            for loc1 in locs:
                for loc2 in locs:
                    if loc2 > loc1:
                        commxcomm.append(int(self.comms[loc1] == self.comms[loc2]))
            self.commxcomm = np.array(commxcomm)

    def load_commxcomm(self, path):
        self.commxcomm = np.load('%s.npy' % path)

    def save_commxcomm(self, path):
        np.save(path, self.commxcomm)
        self.commxcomm = None

    def clean_commxcomm(self):
        self.commxcomm = None

    # compute Rand index
    # https://en.wikipedia.org/wiki/Rand_index
    def distance(self, part):
        self.init_commxcomm()
        part.init_commxcomm()
        count = len(self.commxcomm)
        d = self.commxcomm - part.commxcomm
        dist = np.count_nonzero(d)
        return float(dist) / float(count)

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
