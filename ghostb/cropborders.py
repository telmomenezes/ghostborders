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


from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString
import csv


def shape2poly(shape):
    points = [(point[1], point[0]) for point in shape]
    return Polygon(points)


def line_string2segment(line_string, segment):
    coords = list(line_string.coords)
    return Point(coords[0]), Point(coords[1]), segment[2]


def seg2str(seg):
    head = '%s,%s,%s,%s' % (seg[0].x, seg[0].y, seg[1].x, seg[1].y)
    tail = ','.join(['%s' % x for x in seg[2][4:]])
    return ','.join((head, tail))


class CropBorders:
    def __init__(self, in_file, shapefile_paths):
        self.in_file = in_file
        self.shapefile_paths = shapefile_paths
        self.polys = []
        self.segments = []
        self.header = ''

    def within(self, point):
        for poly in self.polys:
            if point.within(poly):
                return True

        return False

    def fix(self, segment):
        p1within = self.within(segment[0])
        p2within = self.within(segment[1])

        if p1within and p2within:
            return [segment]

        segments = []

        line = LineString((segment[0], segment[1]))
        for poly in self.polys:
            inter = line.intersection(poly)
            if inter.geom_type == 'LineString':
                segments.append(line_string2segment(inter, segment))
            elif inter.geom_type == 'MultiLineString':
                for line in list(inter.geoms):
                    segments.append(line_string2segment(line, segment))
        
        return segments

    def crop(self):
        cc = [49.4, 2.420480, 51.726419, 6.589545]  # belgium
        x0 = cc[1]
        y0 = cc[0]
        x1 = cc[3]
        y1 = cc[2]

        bmap = Basemap(resolution='i', llcrnrlat=y0, llcrnrlon=x0, urcrnrlat=y1, urcrnrlon=x1)

        for path in self.shapefile_paths:
            bmap.readshapefile(path, 'land')
            self.polys += [shape2poly(shape) for shape in bmap.land]

        with open(self.in_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            header = True
            for row in csvreader:
                if header:
                    self.header = ','.join(row)
                    header = False
                else:
                    p1 = Point(float(row[0]), float(row[1]))
                    p2 = Point(float(row[2]), float(row[3]))
                    self.segments.append((p1, p2, row))

        self.segments = [self.fix(segment) for segment in self.segments]
        # flatten
        self.segments = [item for sublist in self.segments for item in sublist]    
        
    def write(self, path=None):
        if path is None:
            print(self.header)
            for segment in self.segments:
                print(seg2str(segment))
        else:
            f = open(path, 'w')
            f.write('%s\n' % self.header)
            for segment in self.segments:
                f.write('%s\n' % seg2str(segment))
            f.close()
