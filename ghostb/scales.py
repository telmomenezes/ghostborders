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


import os
import os.path
import sys
import math
import numpy as np
import ghostb.graph
from ghostb.gen_graph import GenGraph
from ghostb.filter_dists import FilterDists
from ghostb.communities import Communities
from ghostb.borders import Borders
from ghostb.voronoi import Voronoi
import ghostb.partition as part


def abs_log_scale(per):
    max_dist = 100.
    return math.pow(float(per) / 100., 2) * max_dist


class Scales:
    def __init__(self, outdir, intervals):
        self.outdir = outdir
        self.intervals = intervals
        self.per_table = None

    def percent_range(self):
        step = 100.0 / self.intervals
        return [int(i * step) for i in range(1, self.intervals + 1)]
        
    def make_path(self, name, per_dist, directory=False):
        path = '%s/%s-d%s' % (self.outdir, name, per_dist)
        if directory:
            if not os.path.exists(path):
                os.makedirs(path)
            return path
        else:
            return '%s.csv' % (path,)

    def graph_path(self, per_dist):
        return self.make_path('graph', per_dist)

    def comm_path(self, per_dist, directory):
        return self.make_path('comm', per_dist, directory)

    def bord_path(self, per_dist):
        return self.make_path('bord', per_dist)

    def map_path(self, per_dist):
        return '%s/map-d%s.pdf' % (self.outdir, per_dist)

    def dists_path(self):
        return '%s/dists.csv' % self.outdir
    
    def percentiles_path(self):
        return '%s/percentiles.csv' % self.outdir

    def write_percentiles(self, per_table):
        f = open(self.percentiles_path(), 'w')
        f.write('percentile,distance\n')
        for per in per_table:
            f.write('%s,%s\n' % (per, per_table[per]))
        f.close()
    
    def percentiles_table(self):
        per_table = {}

        # check if percentiles file already exists
        percentiles_file = self.percentiles_path()
        if os.path.isfile(percentiles_file):
            data = np.genfromtxt(percentiles_file, names=['percentile', 'dist'], skip_header=1, delimiter=',')
            for row in data:
                per_table[int(row['percentile'])] = float(row['dist'])
        # if not, compute percentiles and create file
        else:
            data = np.genfromtxt(self.dists_path(), names=['dist'], skip_header=1, delimiter=',')
            for per in self.percent_range():
                dist_per = np.percentile(data['dist'], per)
                per_table[per] = dist_per

            self.write_percentiles(per_table)

        return per_table

    def percentile2dist(self, per):
        if self.per_table is None:
            self.per_table = self.percentiles_table()
        return self.per_table[per]

    def dist2percentile(self, dist):
        if self.per_table is None:
            self.per_table = self.percentiles_table()
        for per in self.per_table:
            if dist < self.per_table[per]:
                return per
        return max(self.per_table.keys())
    
    def dist(self, per, scale):
        if scale == 'percentiles':
            return self.percentile2dist(per)
        elif scale == 'log':
            return abs_log_scale(per)
        else:
            print('Unknown scale type: %s' % scale)
            sys.exit()
    
    def generate_graphs(self, db, scale, table):
        fd = FilterDists(db)
        
        graph_file = self.graph_path(100)

        if os.path.isfile(graph_file):
            print('full graph file found: %s' % graph_file)
        else:
            print('generating: %s' % graph_file)
            gg = GenGraph(db, outfile=graph_file, table=table)
            gg.generate()

        for per in self.percent_range():
            if per < 100:
                filtered_file = self.graph_path(per)
                print('generating: %s' % filtered_file)
                max_dist = self.dist(per, scale)
                fd.filter(graph_file, filtered_file, max_dist)

        print('done.')

    def normalize(self):
        for per_dist in self.percent_range():
            graph_file = self.graph_path(per_dist)
            ghostb.graph.normalize_with_confmodel(graph_file, graph_file)

    def generate_communities(self, two, runs, best):
        fname = '%s/metrics.csv' % self.outdir
        f = open(fname, 'w')
        f.write('per_distance,modularity,ncomms\n')
        for per_dist in self.percent_range():
            graph_file = self.graph_path(per_dist)
            comm = Communities(graph_file)
            comm_file = self.comm_path(per_dist, False)
            comm_dir = self.comm_path(per_dist, True)
            modul, ncomms = comm.compute_n_times(
                comm_dir, comm_file, two, runs, best)
            f.write('%s,%s,%s\n' % (per_dist, modul, ncomms))
        f.close()

    def generate_borders(self, db, best, smooth):
        bord = Borders(db, smooth)
        for per_dist in self.percent_range():
            bord_file = self.bord_path(per_dist)
            if best:
                comm_file = self.comm_path(per_dist, False)
                bord.process(None, comm_file, bord_file)
            else:
                comm_dir = self.comm_path(per_dist, True)
                bord.process(comm_dir, None, bord_file)

    def metric(self, metric, db, best, smooth, scale):
        # create Voronoi
        f_ins = []
        for per in self.percent_range():
            if best:
                f_ins.append(self.comm_path(per, False))
            else:
                dir_in = self.comm_path(per, True)
                for (dirpath, dirnames, filenames) in os.walk(dir_in):
                    f_ins.extend(filenames)
                f_ins = ["%s/%s" % (dir_in, f) for f in f_ins]

        vertices = set()
        for f in f_ins:
            fverts = set(part.read(f).keys())
            vertices = vertices.union(fverts)
        vor = Voronoi(db, vertices)

        # compute metrics
        print("percentile,distance,metric")
        for per in self.percent_range():
            f_ins = []
            if best:
                f_ins = [self.comm_path(per, False)]
            else:
                dir_in = self.comm_path(per, True)
                for (dirpath, dirnames, filenames) in os.walk(dir_in):
                    f_ins.extend(filenames)
                f_ins = ["%s/%s" % (dir_in, f) for f in f_ins]

            m = 0.
            for f in f_ins:
                par = part.Partition(vor)
                par.read(f)
                if smooth:
                    par.smooth_until_stable()
                m += par.metric(metric)
            m /= float(len(f_ins))
            print("%s,%s,%s" % (per, self.dist(per, scale), m))

    def similarity_matrix(self, db, smooth, optimize):
        # create precentile range
        pr = self.percent_range()
        npers = len(pr)

        # save memory
        use_disk = optimize == 'memory'

        # create Voronoi
        f_ins = []
        for per in pr:
            f_ins.append(self.comm_path(per, False))
            
        vertices = set()
        for f in f_ins:
            fverts = set(part.read(f).keys())
            vertices = vertices.union(fverts)
        vor = Voronoi(db, vertices)

        # create paritions
        parts = {}
        for per in pr:
            f_in = self.comm_path(per, False)
            par = part.Partition(vor)
            par.read(f_in)
            if smooth:
                par.smooth_until_stable()
            parts[per] = par

        # create distances cache
        dists = np.zeros((npers, npers))

        # compute distances
        for i in range(npers):
            per1 = pr[i]
            if use_disk and (i > 0):
                parts[per1].load_commxcomm('tmp/%s' % per1)
            for j in range(npers):
                per2 = pr[j]
                if per1 < per2:
                    if use_disk and (i > 0):
                        parts[per2].load_commxcomm('tmp/%s' % per2)
                    dist = parts[per1].distance(parts[per2])
                    if use_disk:
                        if i > 0:
                            parts[per2].clean_commxcomm()
                        else:
                            parts[per2].save_commxcomm('tmp/%s' % per2)
                            if j == 1:
                                parts[per1].save_commxcomm('tmp/%s' % per1)
                    dists[i][j] = dist
                else:
                    dist = dists[j][i]
                if j > 0:
                    print(',', end="")
                print('%s' % dist, end="", flush=True)
            print('', flush=True)
            if use_disk:
                parts[per1].clean_commxcomm()

    def dist_sequence(self, db, smooth):
        # create Voronoi
        f_ins = []
        for per in self.percent_range():
            f_ins.append(self.comm_path(per, False))
            
        vertices = set()
        for f in f_ins:
            fverts = set(part.read(f).keys())
            vertices = vertices.union(fverts)
        vor = Voronoi(db, vertices)

        # create paritions
        parts = {}
        for per in self.percent_range():
            f_in = self.comm_path(per, False)
            par = part.Partition(vor)
            par.read(f_in)
            if smooth:
                par.smooth_until_stable()
            parts[per] = par

        prev = False
        for per in self.percent_range():
            if prev:
                dist = parts[per].distance(parts[prev])
                print('%s' % dist)
            prev = per

    def generate_multi_borders(self, db, out_file, smooth, scales):
        if len(scales) == 0:
            scales = self.percent_range()
        print('Using scales: %s' % scales)
        files = [self.comm_path(i, False) for i in scales]
        b = Borders(db, smooth)
        b.process_multi(files, scales, out_file)

    def user_scales(self, dists_str):
        dists = dists_str.split(' ')
        dists = [float(s) for s in dists]
        scales = [self.dist2percentile(d) for d in dists]
        return set(scales)

    def usermetrics(self, db):
        users = {}
        db.cur.execute("SELECT id,dists_str,photos,first_ts,last_ts,mean_time_interval,locations,herfindahl,mean_dist,mean_weighted_dist,comments_given,comments_received,likes_given,likes_received FROM user WHERE active=1")
        for row in db.cur.fetchall():
            user_id = row[0]
            users[user_id] = {}
            users[user_id]['scales'] = self.user_scales(row[1])
            users[user_id]['min_scale'] = min(users[user_id]['scales'])
            users[user_id]['photos'] = row[2]
            users[user_id]['first_ts'] = row[3]
            users[user_id]['last_ts'] = row[4]
            users[user_id]['mean_time_interval'] = row[5]
            users[user_id]['locations'] = row[6]
            users[user_id]['herfindahl'] = row[7]
            users[user_id]['mean_dist'] = row[8]
            users[user_id]['mean_weighted_dist'] = row[9]
            users[user_id]['comments_given'] = row[10]
            users[user_id]['comments_received'] = row[11]
            users[user_id]['likes_given'] = row[12]
            users[user_id]['likes_received'] = row[13]

        print('percentile,count,photos,first_ts,last_ts,mean_time_interval,locations,herfindahl,mean_dist,mean_weighted_dist,comments_given,comments_received,likes_given,likes_received')

        for per in self.percent_range():
            count = 0.
            photos = 0.
            first_ts = 0.
            last_ts = 0.
            mean_time_interval = 0.
            locations = 0.
            herfindahl = 0.
            mean_dist = 0.
            mean_weighted_dist = 0.
            comments_given = 0.
            comments_received = 0.
            likes_given = 0.
            likes_received = 0.
            for user_id in users:
                # if users[user_id]['min_scale'] <= per:
                if per in users[user_id]['scales']:
                    count += 1.
                    photos += users[user_id]['photos']
                    first_ts += users[user_id]['first_ts']
                    last_ts += users[user_id]['last_ts']
                    mean_time_interval += users[user_id]['mean_time_interval']
                    locations += users[user_id]['locations']
                    herfindahl += users[user_id]['herfindahl']
                    mean_dist += users[user_id]['mean_dist']
                    mean_weighted_dist += users[user_id]['mean_weighted_dist']
                    comments_given += users[user_id]['comments_given']
                    comments_received += users[user_id]['comments_received']
                    likes_given += users[user_id]['likes_given']
                    likes_received += users[user_id]['likes_received']

            photos /= count
            first_ts /= count
            last_ts /= count
            mean_time_interval /= count
            locations /= count
            herfindahl /= count
            mean_dist /= count
            mean_weighted_dist /= count
            comments_given /= count
            comments_received /= count
            likes_given /= count
            likes_received /= count

            print('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' %
                  (per, count, photos, first_ts, last_ts, mean_time_interval, locations, herfindahl, mean_dist, mean_weighted_dist, comments_given, comments_received, likes_given, likes_received))
