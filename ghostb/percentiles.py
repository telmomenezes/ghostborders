import os
import numpy as np
from ghostb.gen_graph import GenGraph
from ghostb.filter_dists import FilterDists
from ghostb.communities import Communities
from ghostb.borders import Borders
from ghostb.draw_map import draw_map
from ghostb.confmodel import normalize_with_confmodel


def percent_range():
    return range(10, 101, 10)

    
class Percentiles:
    def __init__(self, outdir):
        self.outdir = outdir

    def make_path(self, name, per_dist, per_time, directory=False):
        path = '%s/%s-d%s-t%s' % (self.outdir, name, per_dist, per_time)
        if directory:
            if not os.path.exists(path):
                os.makedirs(path)
            return path
        else:
            return '%s.csv' % (path,)

    def graph_path(self, per_dist, per_time):
        return self.make_path('graph', per_dist, per_time)

    def comm_path(self, per_dist, per_time, directory):
        return self.make_path('comm', per_dist, per_time, directory)

    def bord_path(self, per_dist, per_time):
        return self.make_path('bord', per_dist, per_time)

    def map_path(self, per_dist, per_time):
        return '%s/map-d%s-t%s.pdf' % (self.outdir, per_dist, per_time)
    
    def write_percentiles(self, per_table):
        per_file = '%s/percentiles.csv' % self.outdir
        f = open(per_file, 'w')
        f.write('percentile,distance,time\n')
        for per in per_table:
            f.write('%s,%s,%s\n' % (per, per_table[per][0], per_table[per][1]))
        f.close()
    
    def compute_percentiles(self, infile):
        per_table = {}
        
        print('loading file: %s' % infile)
        data = np.genfromtxt(infile, names=['dist', 'time'], skip_header=1, delimiter=',')
        print('computing percentiles...')
        for per in percent_range():
            dist_per = np.percentile(data['dist'], per)
            time_per = np.percentile(data['time'], per)
            per_table[per] = (dist_per, time_per)
            print('[percentile %s] dist: %s; time: %s' % (per, dist_per, time_per))

        print('writing percentiles...')
        self.write_percentiles(per_table)
        return per_table

    def generate_graphs(self, db, infile):
        per_table = self.compute_percentiles(infile)
        
        fd = FilterDists(db)

        for per_time in percent_range():
            graph_file = self.graph_path(100, per_time)
            print('generating: %s' % graph_file)
            max_time = per_table[per_time][1]
            gg = GenGraph(db, graph_file, '', max_time)
            gg.generate()
            for per_dist in percent_range():
                if per_dist < 100:
                    filtered_file = self.graph_path(per_dist, per_time)
                    print('filtering: %s' % filtered_file)
                    max_dist = per_table[per_dist][0]
                    fd.filter(graph_file, filtered_file, max_dist)

        print('done.')

    def normalize(self):
        for per_dist in percent_range():
            for per_time in percent_range():
                graph_file = self.graph_path(per_dist, per_time)
                normalize_with_confmodel(graph_file, graph_file)
        
    def generate_communities(self, two, runs, best):
        fname = '%s/metrics.csv' % self.outdir
        f = open(fname, 'w')
        f.write('per_distance,per_time,modularity,ncomms\n')
        for per_dist in percent_range():
            for per_time in percent_range():
                graph_file = self.graph_path(per_dist, per_time)
                comm = Communities(graph_file)
                comm_file = self.comm_path(per_dist, per_time, False)
                comm_dir = self.comm_path(per_dist, per_time, True)
                modul, ncomms = comm.compute_n_times(
                    comm_dir, comm_file, two, runs, best)
                f.write('%s,%s,%s,%s\n' % (per_dist, per_time, modul, ncomms))
        f.close()

    def generate_borders(self, db):
        for per_dist in percent_range():
            for per_time in percent_range():
                comm_file = self.comm_path(per_dist, per_time)
                bord_file = self.bord_path(per_dist, per_time)
                bord = Borders(db)
                bord.process(None, comm_file, bord_file)

    def generate_maps(self, region):
        for per_dist in percent_range():
            for per_time in percent_range():
                bord_file = self.bord_path(per_dist, per_time)
                map_file = self.map_path(per_dist, per_time)
                print('drawing map: %s' % map_file)
                draw_map(bord_file, map_file, region, osm=True)
