from ghostb.locmap import LocMap
from ghostb import voronoi
from os import walk


def comp_points(p1, p2):
    return (p2[0] > p1[0]) or ((p2[0] == p1[0]) and (p2[1] >= p1[1]))


def line2row(line):
    cols = line.split(',')
    return int(cols[0]), int(cols[1])


def normalize_segment(segment):
    if segment['id2'] > segment['id1']:
        id1 = segment['id1']
        id2 = segment['id2']
    else:
        id1 = segment['id2']
        id2 = segment['id1']
    p1 = (segment['x1'], segment['y1'])
    p2 = (segment['x2'], segment['y2'])
    if not comp_points(p1, p2):
        ptemp = p1
        p1 = p2
        p2 = ptemp
    return {'x1': p1[0],
            'y1': p1[1],
            'x2': p2[0],
            'y2': p2[1],
            'id1': id1,
            'id2': id2}


def seg2list(segment):
    return (segment['x1'], segment['y1'], segment['x2'], segment['y2'])


def voronoi2file(vor, path):
    f = open(path, 'w')
    f.write('x1,y1,x2,y2,weight\n')

    for seg in vor:
        f.write('%s,%s,%s,%s,%s\n' % seg)

    f.close()

    
def voronoi2neighbors(vor):
    neighbors = {}
    for segment in vor:
        id1 = segment['id1']
        id2 = segment['id2']
        if id1 in neighbors:
            neighbors[id1].append(id2)
        else:
            neighbors[id1] = [id2]
            if id2 in neighbors:
                neighbors[id2].append(id1)
            else:
                neighbors[id2] = [id1]
    return neighbors

    
def modes(comms):
    distrib = {}
    for comm in comms:
        if comm in distrib:
            distrib[comm] += 1
        else:
            distrib[comm] = 1
    maxfq = max(distrib.values())
    return [comm for comm in distrib if distrib[comm] == maxfq]


class Borders:
    def __init__(self, db):
        self.locmap = LocMap(db)
        segments = voronoi.point_map2segments(self.locmap.coords)
        self.vor = [normalize_segment(x) for x in segments]
        self.comm_map = {}
        for loc_id in self.locmap.coords:
            coord = self.locmap.coords[loc_id]
            self.comm_map[loc_id] = {'community': -1,
                                     'lat': coord['lat'],
                                     'lng': coord['lng']}
        self.neighbors = voronoi2neighbors(self.vor)
        
    def read_communities(self, path):
        lines = [line.rstrip('\n') for line in open(path)]
        del lines[0]

        # initialize with no communities
        for loc_id in self.locmap.coords:
            self.comm_map[loc_id]['community'] = -1

        # read communities from csv
        for line in lines:
            row = line2row(line)
            coord = self.locmap.coords[row[0]]
            self.comm_map[row[0]]['community'] = row[1]

    def check_border(self, segment):
        id1 = segment['id1']
        id2 = segment['id2']
        comm1 = self.comm_map[id1]['community']
        comm2 = self.comm_map[id2]['community']

        # no borders with empty regions
        #if (comm1 < 0) or (comm2 < 0):
        #    return False
        
        return comm1 != comm2

    # find the mode community for a given location and its neighbors
    # in case of a tie, uses the largest community
    def mode_community(self, loc, comm_sizes):
        ids = self.neighbors[loc] + [loc]
        comms = [self.comm_map[x]['community'] for x in ids]
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
        for key in self.comm_map:
            comm = self.comm_map[key]['community']
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
        for loc in self.comm_map:
            comm = self.mode_community(loc, comm_sizes)
            if self.comm_map[loc]['community'] != comm:
                self.comm_map[loc]['community'] = comm
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

    
    def borders(self):
        self.smooth_until_stable()
        return [segment for segment in self.vor if self.check_border(segment)]
    
    def process_file(self, f_in):
        print("processing file %s ..." % f_in)
        self.read_communities(f_in)
        return self.borders()

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
