import ghostb.graph as graph
from ghostb.locmap import LocMap
import ghostb.geo as geo


class FilterDists:
    def __init__(self, db):
        self.locmap = LocMap(db)

    def filter(self, csv_in, csv_out, max_dist):
        print('filtering graph for maximum distance: %s' % max_dist)
        g = graph.read_graph(csv_in)

        for edge in g:
            loc1 = self.locmap.coords[edge[0]]
            loc2 = self.locmap.coords[edge[1]]
            dist = geo.distance(loc1, loc2)
            if dist > max_dist:
                g[edge] = 0.

        graph.write_graph(g, csv_out)
