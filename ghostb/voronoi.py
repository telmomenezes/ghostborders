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


from shapely.geometry import box
import scipy.spatial
import numpy as np
from ghostb.locmap import LocMap


def comp_points(p1, p2):
    return (p2[0] > p1[0]) or ((p2[0] == p1[0]) and (p2[1] >= p1[1]))


def point2id(point, m):
    for key in m:
        lat = m[key]['lat']
        lng = m[key]['lng']
        if (lat == point[0]) and (lng == point[1]):
            return key

    return None


def point_map2segments(m, vertices):
    ids = []
    lats = []
    lngs = []
    point_list = []
    for key in vertices:
        ids.append(key)
        lat = m[key]['lat']
        lng = m[key]['lng']
        lats.append(lat)
        lngs.append(lng)
        point_list.append([lat, lng])
    max_lat = max(lats)
    min_lat = min(lats)
    max_lng = max(lngs)
    min_lng = min(lngs)

    min_distance = max(max_lat - min_lat, max_lng - min_lng)
    safety_margin = min_distance * 2
    # Get points at corners of buffered bbox
    fake_points = box(min_lat - safety_margin,
                      min_lng - safety_margin,
                      max_lat + safety_margin,
                      max_lng + safety_margin).exterior.coords[:-1]

    for fp in fake_points:
        point_list.append([fp[0], fp[1]])

    points = np.array(point_list)

    # Make voronoi
    # print('POINTS %s' % points)
    vor = scipy.spatial.Voronoi(points)

    # TODO: remove fake points?

    # Build segments
    verts = vor.vertices
    segments = []
    for i in range(len(vor.ridge_vertices)):
        rverts = vor.ridge_vertices[i]
        rpoints = vor.ridge_points[i]
        p1 = verts[rverts[0]]
        p2 = verts[rverts[1]]
        seg = {'x1': p1[0],
               'y1': p1[1],
               'x2': p2[0],
               'y2': p2[1],
               'id1': point2id(points[rpoints[0]], m),
               'id2': point2id(points[rpoints[1]], m)}
        if (seg['id1'] is not None) and (seg['id2'] is not None):
            segments.append(seg)

    return segments


def normalize_segment(segment):
    if segment['id2'] > segment['id1']:
        id1 = segment['id1']
        id2 = segment['id2']
    else:
        id1 = segment['id2']
        id2 = segment['id1']
    p1 = (segment['x1'], segment['y1'])
    p2 = (segment['x2'], segment['y2'])
    if not comp_points(p1, p2):
        ptemp = p1
        p1 = p2
        p2 = ptemp
    return {'x1': p1[0],
            'y1': p1[1],
            'x2': p2[0],
            'y2': p2[1],
            'id1': id1,
            'id2': id2}


def segments2neighbors(vor):
    neighbors = {}
    for segment in vor:
        id1 = segment['id1']
        id2 = segment['id2']
        if id1 in neighbors:
            neighbors[id1].append(id2)
        else:
            neighbors[id1] = [id2]
            if id2 in neighbors:
                neighbors[id2].append(id1)
            else:
                neighbors[id2] = [id1]
    return neighbors


class Voronoi:
    def __init__(self, db, vertices):
        self.locmap = LocMap(db)
        segments = point_map2segments(self.locmap.coords, vertices)
        self.segments = [normalize_segment(x) for x in segments]
        self.neighbors = segments2neighbors(self.segments)
