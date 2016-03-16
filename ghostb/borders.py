from ghostb.voronoi import Voronoi
from ghostb.partition import Partition
from os import walk


def line2row(line):
    cols = line.split(',')
    return int(cols[0]), int(cols[1])


def seg2list(segment):
    return (segment['x1'], segment['y1'], segment['x2'], segment['y2'])


def voronoi2file(vor, path):
    f = open(path, 'w')
    f.write('x1,y1,x2,y2,weight\n')

    for seg in vor:
        f.write('%s,%s,%s,%s,%s\n' % seg)

    f.close()

    
class Borders:
    def __init__(self, db, smooth):
        self.smooth = smooth
        self.vor = Voronoi(db)
        
    def check_border(self, par, segment):
        id1 = segment['id1']
        id2 = segment['id2']
        comm1 = par.comms[id1]
        comm2 = par.comms[id2]

        # no border between empty regions
        if (comm1 < 0) and (comm2 < 0):
            return False
        
        return comm1 != comm2

    def borders(self, par):
        return [segment for segment in self.vor.segments if self.check_border(par, segment)]
    
    def process_file(self, f_in):
        print("processing file %s ..." % f_in)
        par = Partition(self.vor, f_in)
        if self.smooth:
            par.smooth_until_stable()
        return self.borders(par)

    def file_list2borders(self, f_ins, dir_in=''):
        if len(dir_in) > 0:
            path = '%s/' % dir_in
        else:
            path = ''
        border_sets = [self.process_file('%s%s' % (path, f)) for f in f_ins]
        total = float(len(border_sets))
        segments = {}
        for border_set in border_sets:
            for segment in border_set:
                segkey = seg2list(segment)
                if segkey in segments:
                    segments[segkey] += 1.0
                else:
                    segments[segkey] = 1.0
        all_borders = [segkey + ((segments[segkey] / total),) for segkey in segments]
        return all_borders
    
    def dir2borders(self, dir_in):
        print("processing %s ..." % dir_in)
        f_ins = []
        for (dirpath, dirnames, filenames) in walk(dir_in):
            f_ins.extend(filenames)
        return self.file_list2borders(f_ins, dir_in)

    def file2borders(self, file_in):
        print("processing %s ..." % file_in)
        f_ins = [file_in]
        return self.file_list2borders(f_ins)

    def process(self, dir_in, file_in, f_out):
        if dir_in is not None:
            bs = self.dir2borders(dir_in)
        else:
            bs = self.file2borders(file_in)
        voronoi2file(bs, f_out)
