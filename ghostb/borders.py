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

    
def isempty(comm):
    if isinstance(comm, int):
        return comm < 0

    for i in comm:
        if i >= 0:
            return False

    return True


class Borders:
    def __init__(self, db, smooth):
        self.smooth = smooth
        self.vor = Voronoi(db)
        
    def check_border(self, comms, segment):
        id1 = segment['id1']
        id2 = segment['id2']
        comm1 = comms[id1]
        comm2 = comms[id2]

        # no border between empty regions
        if isempty(comm1) and isempty(comm2):
            return False
        
        return comm1 != comm2

    def borders(self, comms):
        return [segment for segment in self.vor.segments
                if self.check_border(comms, segment)]
    
    def process_file(self, f_in):
        print("processing file %s ..." % f_in)
        par = Partition(self.vor, False)
        par.read(f_in)
        if self.smooth:
            par.smooth_until_stable()
        return self.borders(par.comms)

    def files2comms(self, files):
        pars = []
        nfiles = len(files)
        for i in range(nfiles):
            par = Partition(self.vor, False)
            par.read(files[i])
            pars.append(par)

        multi_par = Partition(self.vor, False)
        multi_par.combine(pars)
        if self.smooth:
            multi_par.smooth_until_stable()
        return multi_par.comms
    
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

    def metrics(self, seg, comms, scales):
        id1 = seg['id1']
        id2 = seg['id2']
        comm1 = comms[id1]
        comm2 = comms[id2]
            
        summ = 0.
        h = 0.
        for i in range(len(scales)):
            if comm1[i] != comm2[i]:
                scale = scales[i]
                summ += scale
                h += 1.

        mean_dist = summ / h

        return mean_dist, h

    def multi_borders2file(self, bs, comms, scales, path):
        f = open(path, 'w')
        f.write('x1,y1,x2,y2,weight,mean_dist,std_dist,max_weight,h\n')

        for seg in bs:
            mean_dist, h = self.metrics(seg, comms, scales)
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' %
                    (seg['x1'], seg['y1'], seg['x2'], seg['y2'], 1., mean_dist, 0., 1., h))
        f.close()
        
    def process_multi(self, files, scales, f_out):
        comms = self.files2comms(files)
        bs = self.borders(comms)
        self.multi_borders2file(bs, comms, scales, f_out)
