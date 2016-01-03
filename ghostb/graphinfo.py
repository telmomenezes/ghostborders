import ghostb.graph as graph
import math


def graphinfo(csv_in):
    g = graph.read_graph(csv_in)
    print('edges: %s' % (len(g),))
    degs = graph.degrees(g)
    print('nodes: %s' % (len(degs),))
    total = 0.
    max_deg = -1.
    min_deg = float("inf")
    for node in degs:
        deg = degs[node]
        total += deg
        if deg > max_deg:
            max_deg = deg
        if deg < min_deg:
            min_deg = deg
    print('degress: min: %s; max: %s, mean: %s' % (min_deg, max_deg, total / len(degs)))
