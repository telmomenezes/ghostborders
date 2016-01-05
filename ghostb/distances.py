from ghostb.locmap import LocMap
import ghostb.geo as geo
import ghostb.graph as graph


class Distances:
    def __init__(self, db):
        self.locmap = LocMap(db)

    def compute(self, infile, outfile):
        g = graph.read_graph(infile)

        f = open(outfile, 'w')
        
        total_distance = 0.
        count = 0.
        for edge in g:
            loc1 = self.locmap.coords[edge[0]]
            loc2 = self.locmap.coords[edge[1]]
            dist = geo.distance(loc1, loc2)
            f.write('%s\n' % dist)
            total_distance += dist
            count += 1.

        f.close()
        
        mean_distance = total_distance / count
        print('mean distance: %s' % mean_distance)

