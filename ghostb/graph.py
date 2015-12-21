import random
import math


def add_edge(graph, edge, weight=1.0):
    e = edge[:]
    e.sort()
    e = tuple(e)
    if e in graph:
        w = graph[e]
    else:
        w = 0.0
    graph[e] = w + weight
    return graph


def random_edge(n):
    while True:
        orig = random.randrange(n)
        targ = random.randrange(n)
        if orig != targ:
            return [orig, targ]


def add_random_edge(graph, n):
    add_edge(graph, random_edge(n))


def random_graph(n, e):
    graph = {}
    for i in range(e):
        add_random_edge(graph, n)
    return graph


def graph2stubs(graph):
    c = 0.
    for k in graph:
        c += graph[k]
    c = int(c) * 2

    stubs = [None] * c

    i = 0
    for key in graph:
        orig = key[0]
        targ = key[1]
        weight = int(graph[key])
        for n in range(weight):
            stubs[n + i] = orig
            stubs[n + i + weight] = targ
        i += 2 * weight

    return stubs


def stubs2graph(ar):
    g = {}
    for i in range(0, len(ar), 2):
        add_edge(g, [ar[i], ar[i + 1]])
    return g


def conf_model(graph):
    stubs = graph2stubs(graph)
    random.shuffle(stubs)
    return stubs2graph(stubs)


def self_loops(graph):
    loops = 0
    for edge in graph:
        if edge[0] == edge[1]:
            loops += graph[edge]
    return loops


def edge_count(graph):
    edges = 0
    for edge in graph:
        edges += graph[edge]
    return edges


def read_graph(csv_path):
    with open(csv_path, 'r') as csvfile:
        lines = csvfile.read().split('\n')

    g = {}
    for line in lines[1:]:
        try:
            tokens = [int(round(float(x))) for x in line.split(',')]
            add_edge(g, [tokens[0], tokens[1]], tokens[2])
        except ValueError:
            # ignore invalid lines (e.g. empty)
            pass

    return g


def add_graph2graph(targ, orig):
    for edge in orig:
        add_edge(targ, [edge[0], edge[1]], orig[edge])


def graph_div(graph, d):
    for edge in graph:
        weight = float(graph[edge])
        graph[edge] = weight / float(d)


def conf_model_n_times(graph, n):
    g = {}
    for i in range(n):
        print('conf model #%s' % i)
        add_graph2graph(g, conf_model(graph))

    graph_div(g, n)
    return g


def normalize(graph, ref_graph):
    zeroes = 0
    below = 0
    THRESHOLD = .000001 #1.
    for edge in graph:
        weight = float(graph[edge])
        if edge in ref_graph:
            ref_weight = math.ceil(float(ref_graph[edge]))
            if ref_weight < THRESHOLD:
                ref_weight = THRESHOLD
                below += 1
        else:
            ref_weight = THRESHOLD
            zeroes += 1
            weight = 0
        weight /= ref_weight
        weight = math.ceil(weight)
        graph[edge] = weight
    print('zeroes: %s; below: %s; total: %s' % (zeroes, below, len(graph)))


def write_graph(graph, csv_path):
    with open(csv_path, 'w') as f:
        f.write('orig,targ,weight\n')
        for edge in graph:
            if graph[edge] > 0.0:
                f.write('%s,%s,%s\n' % (edge[0], edge[1], graph[edge]))
