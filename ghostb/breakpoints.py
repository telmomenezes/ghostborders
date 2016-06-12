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


import numpy as np


def mean_inner_dist(data, a, b):
    count = 0.0
    dist = 0.0
    for i in range(a, b):
        for j in range(a, i):
            count += 1.0
            dist += data[i][j]
    if count == 0.0:
        return 0.0
    dist /= count
    return dist


def mean_outter_dist(data, a, b, intervals):
    count = 0.0
    dist = 0.0
    for i in range(a, b):
        for j in range(0, intervals):
            if (j < a) or (j >= b):
                count += 1.0
                dist += data[i][j]
    if count == 0.0:
        return 0.0
    dist /= count
    return dist


def intervals_dist(data, a, b, c):
    count = 0.0
    dist = 0.0
    for i in range(a, b):
        for j in range(b, c):
            count += 1.0
            dist += data[i][j]
    if count == 0.0:
        return 0.0
    dist /= count
    return dist


def scores(data, breaks, intervals):
    total_intra = 0.0
    total_inter = float('inf')
    start = 0
    for i in range(len(breaks)):
        b = breaks[i]
        c = intervals
        if i + 1 < len(breaks):
            c = breaks[i + 1]
        total_intra += mean_inner_dist(data, start, b) * (b - start)
        inter = intervals_dist(data, start, b, c)
        if inter < total_inter:
            total_inter = inter
        start = b
    total_intra += mean_inner_dist(data, start, intervals) * (intervals - start)
    total_intra /= intervals
    return total_intra, total_inter


def valid_break(breaks, brk):
    for i in breaks:
        if abs(i - brk) < 1:
            return False
    return True


def find_best_scale(data, a, b):
    best_dist = float('inf')
    best_scale = -1
    for scale in range(a, b):
        dist = 0.0
        for i in range(a, b):
            dist += data[scale][i]
        if dist < best_dist:
            best_dist = dist
            best_scale = scale
    return best_scale


def best_scales(data, breakpoints):
    scales = []
    start = 0
    for b in breakpoints:
        scales.append(find_best_scale(data, start, b))
        start = b
    scales.append(find_best_scale(data, start, 100))
    return scales


def find_breakpoints(infile, intervals):
    data = np.genfromtxt(infile, skip_header=0, delimiter=',')

    breaks = []
    best_breaks = []
    best_best_score = float('inf')

    while True:
        best = []
        best_score = float('inf')
        for i in range(1, intervals):
            if valid_break(breaks, i):
                new_breaks = breaks[:]
                new_breaks.append(i)
                new_breaks.sort()
                intra, inter = scores(data, new_breaks, intervals)
                score = intra / inter
                if score < best_score:
                    best_score = score
                    best = new_breaks
        breaks = best
        if best_score < best_best_score:
            best_best_score = best_score
            best_breaks = breaks
        else:
            break

    scales = best_scales(data, best_breaks)
    print('breakpoints: %s' % best_breaks)
    print('scales: %s' % scales)
