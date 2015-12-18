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


def map2voronoi(m):
    segments = voronoi.point_map2segments(m)
    return [normalize_segment(x) for x in segments]


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


def mode_community(loc, m, neighbors, comm_sizes):
    ids = neighbors[loc] + [loc]
    comms = [m[x]['community'] for x in ids]
    cmodes = modes(comms)
    best_mode = None
    best_size = 0
    for mode in cmodes:
        size = comm_sizes[mode]
        if size > best_size:
            best_size = size
            best_mode = mode
    return best_mode


def map2community_sizes(m):
    comm_sizes = {}
    for key in m:
        comm = m[key]['community']
        if comm in comm_sizes:
            comm_sizes[comm] += 1
        else:
            comm_sizes[comm] = 1
    return comm_sizes


def smooth(m, neighbors):
    comm_sizes = map2community_sizes(m)
    for loc in m:
        comm = mode_community(loc, m, neighbors, comm_sizes)
        m[loc]['community'] = comm


def smooth_n(m, neighbors, n):
    for i in range(n):
        smooth(m, neighbors)


def check_border(m, segment):
    id1 = segment['id1']
    id2 = segment['id2']

    # no borders with regions with unknown communities
    if m[id1]['community'] < 0:
        return False
    if m[id2]['community'] < 0:
        return False

    # border if community
    return m[id1]['community'] != m[id2]['community']


def borders(vor, m):
    neighbors = voronoi2neighbors(vor)
    smooth_n(m, neighbors, 10)
    return [segment for segment in vor if check_border(m, segment)]


def equal_segments(seg1, seg2):
    return (seg1['x1'] == seg2['x1'])\
            and (seg1['y1'] == seg2['y1'])\
            and (seg1['x2'] == seg2['x2'])\
            and (seg1['y2'] == seg2['y2'])


def weight(segment, bs):
    total = float(len(bs))
    count = 0.0
    for b in bs:
        for seg in b:
            if equal_segments(segment, seg):
                count += 1.0
    return count / total


def voronoi2file(vor, path):
    f = open(path, 'w')
    f.write('x1,y1,x2,y2,weight\n')

    for seg in vor:
        f.write('%s,%s,%s,%s,%s\n' % (seg['x1'], seg['y1'], seg['x2'], seg['y2'], seg['weight']))

    f.close()


def dir_list(dir_path):
    return next(walk(dir_path))[1]


def border_weight(bs, border):
    if border in bs:
        return bs[border]
    else:
        return 0.


def weights(border, mborders):
    return [border_weight(bs, border) for bs in mborders]


def wtable2file(wtable, path):
    wc = len(wtable[list(wtable.keys())[0]])

    f = open(path, 'w')

    f.write('x1,y1,x2,y2,')
    wcolnames = list(range(wc))
    wcolnames = ['w%s' % x for x in wcolnames]
    f.write(','.join(wcolnames))
    f.write('\n')

    for key in wtable:
        f.write('%s,%s\n' % (','.join(key), ','.join(wtable[key])))

    f.close()


def borders2map(bs):
    m = {}
    for border in bs:
        key = (border['x1'], border['y1'], border['x2'], border['y2'])
        m[key] = border['weight']


class Borders:
    def __init__(self, db):
        self.locmap = LocMap(db)

    def csv2map(self, path):
        lines = [line.rstrip('\n') for line in open(path)]
        del lines[0]

        # initialize with no communities
        m = {}
        for loc in self.locmap.coords:
            coord = self.locmap.coords[loc]
            m[loc] = {'community': -1,
                      'lat': coord['lat'],
                      'lng': coord['lng']}

        # read communities from csv
        for line in lines:
            row = line2row(line)
            coord = self.locmap.coords[row[0]]
            m[row[0]] = {'community': row[1],
                         'lat': coord['lat'],
                         'lng': coord['lng']}
        return m

    def process_file(self, f_in):
        print("processing file %s ..." % f_in)
        m = self.csv2map(f_in)
        vor = map2voronoi(m)
        return borders(vor, m)

    def file_list2borders(self, f_ins, dir_in=''):
        if len(dir_in) > 0:
            path = '%s/' % dir_in
        else:
            path = ''
        bs = [self.process_file('%s%s' % (path, f)) for f in f_ins]
        all_borders = [item for sublist in bs for item in sublist]
        for segment in all_borders:
            segment['weight'] = weight(segment, bs)
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

    def process_multiple(self, dir_in, f_out):
        d_ins = dir_list(dir_in)[-12:]  # take last 12 directories
        mborders = [borders2map(self.dir2borders(d)) for d in d_ins]
        all_borders = [list(bs.keys) for bs in mborders]
        all_borders = [item for sublist in all_borders for item in sublist]
        all_borders = set(all_borders)
        wtable = {}
        for border in all_borders:
            wtable[border] = weights(border, mborders)
        wtable2file(wtable, f_out)
