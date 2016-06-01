#   Copyright (c) 2016 Centre Marc Bloch Berlin
#   (An-Institut der Humboldt Universität, UMIFRE CNRS-MAE).
#   All rights reserved.
#
#   Written by Telmo Menezes <telmo@telmomenezes.com>
#
#   This file is part of GhostBorders.
#
#   GhostBorders is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   GhostBorders is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with GhostBorders.  If not, see <http://www.gnu.org/licenses/>.


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


def degrees(graph):
    degs = {}
    for edge in graph:
        orig = edge[0]
        targ = edge[1]
        weight = graph[edge]
        if orig in degs:
            degs[orig] += weight
        else:
            degs[orig] = weight
        if targ in degs:
            degs[targ] += weight
        else:
            degs[targ] = weight
    return degs


def write_graph(graph, csv_path):
    with open(csv_path, 'w') as f:
        f.write('orig,targ,weight\n')
        for edge in graph:
            if graph[edge] > 0.0:
                f.write('%s,%s,%s\n' % (edge[0], edge[1], graph[edge]))


def normalize(g):
    degs = degrees(g)
    m = len(g) * 2.

    for edge in g:
        weight = float(g[edge])
        expected = (float(degs[edge[0]]) * float(degs[edge[1]])) / m
        if expected > 0.:
            weight /= expected
        g[edge] = weight


def normalize_with_confmodel(csv_in, csv_out):
    g = read_graph(csv_in)
    normalize(g)
    write_graph(g, csv_out)


def write_degrees(g):
    degs = degrees(g)
    for loc in degs:
        print('%s,%s' % (loc, degs[loc]))

def filter_low_degree(g, min_ratio):
    # compute mean degree
    degs = degrees(g)
    total = 0.0
    count = 0.0
    for loc in degs:
        total += float(degs[loc])
        count += 1.0
    mean_degree = total / count 

    # determine active locaions
    active = []
    for loc in degs:
        ratio = float(degs[loc]) / mean_degree
        if ratio >= min_ratio:
            active.append(loc)

    # compute filtered graph
    new_g = {}
    for loc in g:
        if loc in active:
            new_g[loc] = [targ for targ in g[loc] if targ in active]
    return new_g