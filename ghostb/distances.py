from ghostb.locmap import LocMap
import ghostb.geo as geo
import graph


class Distances:
    def __init__(self, db):
        self.locmap = LocMap(db)

    def compute(self, infile):
        g = graph.read_graph(infile)
        total_distance = 0.
        count = 0.
        for edge in g:
            loc1 = self.locmap.coords[edge[0]]
            loc2 = self.locmap.coords[edge[1]]
            total_distance += geo.distance(loc1, loc2)
            count += 1.
        mean_distance = total_distance / count
        print('mean distance: %s' % mean_distance)

