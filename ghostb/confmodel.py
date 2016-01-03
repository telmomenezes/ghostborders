import ghostb.graph as graph
import math


def normalize1(g):
    degs = graph.degrees(g)
    m = len(g) * 2.
    
    for edge in g:
        weight = math.ceil(float(g[edge]))
        expected = (float(degs[edge[0]]) * float(degs[edge[1]])) / m
        ref_weight = math.ceil(expected)
        weight /= ref_weight
        weight = math.ceil(weight)
        g[edge] = weight


def normalize2(g):
    degs = graph.degrees(g)
    m = len(g) * 2.
    
    for edge in g:
        weight = float(g[edge])
        expected = (float(degs[edge[0]]) * float(degs[edge[1]])) / m
        weight /= expected
        g[edge] = weight


def normalize3(g):
    degs = graph.degrees(g)
    m = len(g) * 2.
    
    for edge in g:
        weight = float(g[edge])
        expected = (float(degs[edge[0]]) * float(degs[edge[1]])) / m
        weight -= expected
        g[edge] = weight


def normalize_with_confmodel(csv_in, csv_out, runs):
    g = graph.read_graph(csv_in)
    #ref_graph = graph.conf_model_n_times(g, runs)
    normalize2(g)
    graph.write_graph(g, csv_out)
