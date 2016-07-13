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
import ghostb.geo as geo


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


def segments_by_id(segments):
    segmap = {}
    for segment in segments:
        id1 = segment['id1']
        id2 = segment['id2']
        if id1 in segmap:
            segmap[id1].append(segment)
        else:
            segmap[id1] = [segment]
        if id2 in segmap:
            segmap[id2].append(segment)
        else:
            segmap[id2] = [segment]
    return segmap


def next_polygon_segment(segments, segs):
    seg = segs[-1]
    for s in segments:
        if (s['x1'] == seg['x2']) and (s['y1'] == seg['y2']):
            return s
        elif (s['x2'] == seg['x2']) and (s['y2'] == seg['y2']) and (s['x1'] != seg['x1']):
            return {'x1': s['x2'],
                    'y1': s['y2'],
                    'x2': s['x1'],
                    'y2': s['y1']}

    # print('OPEN LOOP')
    seg0 = segs[0]
    return {'x1': seg['x2'],
            'y1': seg['y2'],
            'x2': seg0['x1'],
            'y2': seg0['y2']}


def polygon_ordering(segments):
    segs = [segments[0]]
    while len(segs) < len(segments):
        segs.append(next_polygon_segment(segments, segs))
    return segs


def area(segments):
    a = 0.
    for seg in segments:
        a += seg['x1'] * seg['y2'] + seg['x2'] * seg['y1']
    return abs(a / 2.)


def tokms(segments):
    min_x = float('inf')
    min_y = float('inf')
    for seg in segments:
        if seg['x1'] < min_x:
            min_x = seg['x1']
        if seg['x2'] < min_x:
            min_x = seg['x2']
        if seg['y1'] < min_y:
            min_y = seg['y1']
        if seg['x2'] < min_x:
            min_y = seg['y2']

    normsegs = []
    for seg in segments:
        nseg = {'x1': geo.distance({'lat': min_x, 'lng': min_y}, {'lat': seg['x1'], 'lng': min_y}),
                'y1': geo.distance({'lat': min_x, 'lng': min_y}, {'lat': min_x, 'lng': seg['y1']}),
                'x2': geo.distance({'lat': min_x, 'lng': min_y}, {'lat': seg['x2'], 'lng': min_y}),
                'y2': geo.distance({'lat': min_x, 'lng': min_y}, {'lat': min_x, 'lng': seg['y2']}),
                'id1': seg['id1'],
                'id2': seg['id2']}
        normsegs.append(nseg)
    return normsegs


class Voronoi:
    def __init__(self, db, vertices):
        self.locmap = LocMap(db)
        segments = point_map2segments(self.locmap.coords, vertices)
        self.segments = [normalize_segment(x) for x in segments]
        self.neighbors = segments2neighbors(self.segments)

    def areas(self):
        normsegs = tokms(self.segments)
        segmap = segments_by_id(normsegs)
        areamap = {}
        for loc_id in segmap:
            areamap[loc_id] = area(polygon_ordering(segmap[loc_id]))
            print(areamap[loc_id])
        return areamap
