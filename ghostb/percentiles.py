import numpy as np
from ghostb.gen_graph import GenGraph
from ghostb.filter_dists import FilterDists


class Percentiles:
    def __init__(self, db):
        self.db = db
        self.per_table = {}
        
    def compute_percentiles(self, infile):
        print('loading file: %s' % infile)
        data = np.genfromtxt(infile, names=['dist', 'time'], skip_header=1, delimiter=',')
        print('computing percentiles...')
        for i in range(10):
            per = (i + 1) * 10.
            dist_per = np.percentile(data['dist'], per)
            time_per = np.percentile(data['time'], per)
            self.per_table[per] = (dist_per, time_per)
            print('[percentile %s] dist: %s; time: %s' % (per, dist_per, time_per))

    def generate_graphs(self, outdir):
        fd = FilterDists(self.db)
        for per_time in self.per_table:
            pt = int(per_time)
            graph_file = '%s/graph-t%s-d100.csv' % (outdir, pt)
            print('generating: %s' % graph_file)
            max_time = self.per_table[per_time][1]
            gg = GenGraph(self.db, graph_file, '', max_time)
            gg.generate()
            for per_dist in self.per_table:
                if per_dist < 100.:
                    pd = int(per_dist)
                    filtered_file = '%s/graph-t%s-d%s.csv' % (outdir, pt, pd)
                    print('filtering: %s' % filtered_file)
                    max_dist = self.per_table[per_dist][0]
                    fd.filter(graph_file, filtered_file, max_dist)
            
    def generate(self, infile, outdir):
        self.compute_percentiles(infile)
        self.generate_graphs(outdir)
