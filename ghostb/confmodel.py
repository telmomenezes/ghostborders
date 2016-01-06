import ghostb.graph as graph
import math

def normalize(g):
    degs = graph.degrees(g)
    m = len(g) * 2.

    for edge in g:
        weight = float(g[edge])
        expected = (float(degs[edge[0]]) * float(degs[edge[1]])) / m
        weight /= expected
        g[edge] = weight


def normalize_with_confmodel(csv_in, csv_out):
    g = graph.read_graph(csv_in)
    normalize(g)
    graph.write_graph(g, csv_out)
