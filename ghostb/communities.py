import igraph
import csv
import random


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
        self.edge_tups = []
        with open(in_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            header = True
            for row in csvreader:
                if header:
                    header = False
                else:
                    orig = self.vert_id(int(row[0]))
                    targ = self.vert_id(int(row[1]))
                    self.edge_tups.append((orig, targ, float(row[2])))

        # revert vertmap
        self.rev_vertmap = {}
        for k in self.vertmap:
            self.rev_vertmap[self.vertmap[k]] = k

        self.verts = list(range(len(self.vertmap)))
        self.rev_verts = list(range(len(self.vertmap)))

    def build_graph(self):
        # always shuffle the edge tuples list to produce diverse results from the non-deterministic
        # community detection algorithm
        # random.shuffle(self.edge_tups)
        random.shuffle(self.verts)
        self.rev_verts = list(range(len(self.vertmap)))
        for i in range(len(self.vertmap)):
            self.rev_verts[self.verts[i]] = i

        edges = [(self.verts[x[0]], self.verts[x[1]]) for x in self.edge_tups]
        weights = [x[2] for x in self.edge_tups]

        # create graph
        g = igraph.Graph()
        g.add_vertices(len(self.vertmap))
        g.add_edges(edges)
        g.es['weight'] = weights
        return g

    def vert_id(self, name):
        if name not in self.vertmap:
            self.vertmap[name] = len(self.vertmap)
        return self.vertmap[name]

    def compute(self, out_file, two):
        g = self.build_graph()

        comms = igraph.Graph.community_multilevel(g, weights="weight", return_levels=False)
        memb = comms.membership

        # force dichotomy (horrible exponential time algo)
        if two:
            bestmod = -1
            best = None

            for i in range(2 ** len(comms)):
                memb2 = twocomms(memb, i)
                vc = igraph.VertexClustering(g, membership=memb2)
                vc.recalculate_modularity()
                m = vc.modularity
                if m >= bestmod:
                    bestmod = m
                    best = memb2

            memb = best

        f = open(out_file, 'w')
        f.write('id,comm\n')

        for i in range(len(memb)):
            f.write('%s,%s\n' % (self.rev_vertmap[self.rev_verts[i]], memb[i]))
        f.close()

    def compute_n_times(self, out_dir, two, n):
        for i in range(n):
            print('iteration #%s' % i)
            self.compute("%s/%s.csv" % (out_dir, i), two)

        print('done.')
