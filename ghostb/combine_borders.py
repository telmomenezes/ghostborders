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


import math
from numpy import genfromtxt


def metrics(dists_weights, count):
    total = 0.
    summ = 0.
    max_weight = 0.
    h = 0.
    for dw in dists_weights:
        dist = dw[0]
        weight = dw[1]
        if weight > max_weight:
            max_weight = weight
        total += weight
        summ += weight * dist
        h += math.pow(weight, 2)

    mean_weight = total / count
    mean_dist = summ / total

    summ = 0.
    for dw in dists_weights:
        dist = dw[0]
        weight = dw[1]
        summ += weight * math.pow(dist - mean_dist, 2)

    std = math.sqrt(summ / total)

    h /= pow(total, 2)
    h = 1. / h
    
    return mean_weight, mean_dist, std, max_weight, h


class CombineBorders:
    def __init__(self):
        self.segments = {}
        self.count = 0

    def add_file(self, borders_file, distance_threshold):
        self.count += 1
        co = genfromtxt(borders_file, delimiter=',', skip_header=1)
        cols = co.shape[0]

        for i in range(cols):
            segment = (co[i][0], co[i][1], co[i][2], co[i][3])
            weight = co[i][4]

            if segment not in self.segments:
                self.segments[segment] = []
            self.segments[segment].append((distance_threshold, weight))

    def write(self, path):
        f = open(path, 'w')
        f.write('x1,y1,x2,y2,weight,mean_dist,std_dist,max_weight,h\n')
        
        for segment in self.segments:
            dists_weights = self.segments[segment]
            #print(segment + (mean_std_dist(dists_weights)))
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (segment + (metrics(dists_weights, float(self.count)))))

        f.close()
