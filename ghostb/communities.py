import igraph
import csv


def bincomm(x, n):
    if (n & (1 << x)) > 0:
        return 1
    else:
        return 0


def twocomms(memb, n):
    return [bincomm(x, n) for x in memb]


class Communities:
    def __init__(self, in_file):
        self.vertmap = {}
        edge_tups = []
        with open(in_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            header = True
            for row in csvreader:
                if header:
                    header = False
                else:
                    orig = self.vert_id(int(row[0]))
                    targ = self.vert_id(int(row[1]))
                    edge_tups.append((orig, targ, float(row[2])))

        # revert vertmap
        self.rev_vertmap = {}
        for k in self.vertmap:
            self.rev_vertmap[self.vertmap[k]] = k

        # create graph
        self.g = igraph.Graph()
        self.g.add_vertices(len(self.vertmap))
        for e in edge_tups:
            self.g.add_edge(e[0], e[1], weight=e[2])

    def vert_id(self, name):
        if name not in self.vertmap:
            self.vertmap[name] = len(self.vertmap)
        return self.vertmap[name]

    def compute(self, out_file, two):
        comms = igraph.Graph.community_multilevel(self.g, weights="weight", return_levels=False)
        memb = comms.membership

        # force dichotomy (horrible exponential time algo)
        if two:
            bestmod = -1
            best = None

            for i in range(2 ** len(comms)):
                memb2 = twocomms(memb, i)
                vc = igraph.VertexClustering(self.g, membership=memb2)
                vc.recalculate_modularity()
                m = vc.modularity
                if m >= bestmod:
                    bestmod = m
                    best = memb2

            memb = best

        f = open(out_file, 'w')
        f.write('id,comm\n')

        for i in range(len(memb)):
            f.write('%s,%s\n' % (self.rev_vertmap[i], memb[i]))
        f.close()

    def compute_n_times(self, out_dir, two, n):
        for i in range(n):
            print('iteration #%s' % i)
            self.compute("%s/%s.csv" % (out_dir, i), two)

        print('done.')
