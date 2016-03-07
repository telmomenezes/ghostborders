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


class MultiBorders:
    def __init__(self, db, files, scales, smooth):
        print(files)
        print(scales)
        self.files = files
        self.scales = scales
        self.nscales = len(files)
        self.locmap = LocMap(db)
        self.do_smooth = smooth
        segments = voronoi.point_map2segments(self.locmap.coords)
        self.vor = [normalize_segment(x) for x in segments]
        self.comm_map = {}
        for loc_id in self.locmap.coords:
            coord = self.locmap.coords[loc_id]
            self.comm_map[loc_id] = {'community': [-1 for i in range(self.nscales)],
                                     'lat': coord['lat'],
                                     'lng': coord['lng']}
        self.neighbors = voronoi2neighbors(self.vor)

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
        ids = [loc]
        if loc in self.neighbors:
            ids += self.neighbors[loc]
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
            print('smoothing pass %s, %s updates.' % (i, updates))
            if updates == 0:
                return
    
    def borders(self):
        if self.do_smooth:
            self.smooth_until_stable()
        return [segment for segment in self.vor if self.check_border(segment)]

    def read_communities(self, path, pos):
        print("reading file %s ..." % path)
        lines = [line.rstrip('\n') for line in open(path)]
        del lines[0]

        # read communities from csv
        for line in lines:
            row = line2row(line)
            self.comm_map[row[0]]['community'][pos] = row[1]
    
    def process_file(self, f_in):
        print("processing file %s ..." % f_in)
        self.read_communities(f_in)
        return self.borders()

    def files2borders(self):
        for i in range(len(self.files)):
            self.read_communities(self.files[i], i)

        # converting community lists to tuples so that they can be used as keys
        for loc_id in self.locmap.coords:
            self.comm_map[loc_id]['community'] = tuple(self.comm_map[loc_id]['community'])
            
        return self.borders()

    def metrics(self, seg):
        id1 = seg['id1']
        id2 = seg['id2']
        comm1 = self.comm_map[id1]['community']
        comm2 = self.comm_map[id2]['community']
            
        summ = 0.
        h = 0.
        for i in range(self.nscales):
            if comm1[i] != comm2[i]:
                scale = self.scales[i]
                summ += scale
                h += 1.

        mean_dist = summ / h

        #h /= pow(total, 2)
        #h = 1. / h
    
        return mean_dist, h

    def borders2file(self, vor, path):
        f = open(path, 'w')
        f.write('x1,y1,x2,y2,weight,mean_dist,std_dist,max_weight,h\n')

        for seg in vor:
            mean_dist, h = self.metrics(seg)
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' %
                    (seg['x1'], seg['y1'], seg['x2'], seg['y2'], 1., mean_dist, 0., 1., h))
        f.close()
    
    def process(self, f_out):
        bs = self.files2borders()
        self.borders2file(bs, f_out)
