import os
import numpy as np
from ghostb.gen_graph import GenGraph
from ghostb.filter_dists import FilterDists
from ghostb.communities import Communities
from ghostb.borders import Borders
from ghostb.combine_borders import CombineBorders
from ghostb.draw_map import draw_map
from ghostb.confmodel import normalize_with_confmodel
from ghostb.cropborders import CropBorders


def percent_range():
    return range(10, 101, 10)

    
class Percentiles:
    def __init__(self, outdir):
        self.outdir = outdir

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
    
    def write_percentiles(self, per_table):
        per_file = '%s/percentiles.csv' % self.outdir
        f = open(per_file, 'w')
        f.write('percentile,distance\n')
        for per in per_table:
            f.write('%s,%s\n' % (per, per_table[per]))
        f.close()
    
    def compute_percentiles(self, infile):
        per_table = {}
        
        print('loading file: %s' % infile)
        data = np.genfromtxt(infile, names=['dist', 'time'], skip_header=1, delimiter=',')
        print('computing percentiles...')
        for per in percent_range():
            dist_per = np.percentile(data['dist'], per)
            per_table[per] = dist_per
            print('[percentile %s] dist: %s' % (per, dist_per))

        print('writing percentiles...')
        self.write_percentiles(per_table)
        return per_table

    def generate_graphs(self, db, infile):
        per_table = self.compute_percentiles(infile)
        
        fd = FilterDists(db)
        gg = GenGraph(db, graph_file, '')
        gg.generate()
        for per_dist in percent_range():
            filtered_file = self.graph_path(per_dist)
            print('generating: %s' % filtered_file)
            max_dist = per_table[per_dist]
            fd.filter(graph_file, filtered_file, max_dist)

        print('done.')

    def normalize(self):
        for per_dist in percent_range():
            graph_file = self.graph_path(per_dist)
            normalize_with_confmodel(graph_file, graph_file)
        
    def generate_communities(self, two, runs, best):
        fname = '%s/metrics.csv' % self.outdir
        f = open(fname, 'w')
        f.write('per_distance,modularity,ncomms\n')
        for per_dist in percent_range():
            graph_file = self.graph_path(per_dist)
            comm = Communities(graph_file)
            comm_file = self.comm_path(per_dist, False)
            comm_dir = self.comm_path(per_dist, True)
            modul, ncomms = comm.compute_n_times(
                comm_dir, comm_file, two, runs, best)
            f.write('%s,%s,%s\n' % (per_dist, modul, ncomms))
        f.close()

    def generate_borders(self, db, best):
        bord = Borders(db)
        for per_dist in percent_range():
        #for per_time in percent_range():
            per_time = 100
            bord_file = self.bord_path(per_dist, per_time)
            if best:
                comm_file = self.comm_path(per_dist, per_time, False)
                bord.process(None, comm_file, bord_file)
            else:
                comm_dir = self.comm_path(per_dist, per_time, True)
                bord.process(comm_dir, None, bord_file)

    def crop_borders(self, shapefile):
        for per_dist in percent_range():
            bord_file = self.bord_path(per_dist)
            print('Cropping: %s' % bord_file)
            cropper = CropBorders(bord_file, shapefile)
            cropper.crop()
            cropper.write(bord_file)
                
                    
    def combine_borders(self, out_file):
        cb = CombineBorders()
        for per_dist in percent_range():
            bord_file = self.bord_path(per_dist)
            cb.add_file(bord_file, per_dist)
        cb.write(out_file)
                
                    
    def generate_maps(self, region):
        for per_dist in percent_range():
            bord_file = self.bord_path(per_dist)
            map_file = self.map_path(per_dist)
            print('drawing map: %s' % map_file)
            draw_map(bord_file, map_file, region, osm=True)