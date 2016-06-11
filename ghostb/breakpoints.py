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


def mean_dist(data, a, b):
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


def mean_mean_dist(data, breaks, intervals):
    total = 0.0
    start = 0
    for b in breaks:
        total += mean_dist(data, start, b) * (b - start)
        start = b
    total += mean_dist(data, start, intervals) * (intervals - start)
    return total / intervals


def valid_break(breaks, brk, window):
    for i in breaks:
        if abs(i - brk) < window:
            return False
    return True


def find_breakpoints(infile, intervals, window):
    data = np.genfromtxt(infile, skip_header=0, delimiter=',')

    breaks = []
    best_breaks = []
    best_best_score = float('inf')

    while True:
        best = []
        best_score = float('inf')
        for i in range(intervals):
            if valid_break(breaks, i, window):
                new_breaks = breaks[:]
                new_breaks.append(i)
                score = mean_mean_dist(data, new_breaks, intervals)
                if score < best_score:
                    best_score = score
                    best = new_breaks
        breaks = best
        if best_score < best_best_score:
            # print(best_score)
            # print(best)
            best_breaks = breaks
            best_best_score = best_score
        else:
            break

    print(best_breaks)
