from shapely.geometry import box
import scipy.spatial as spa
import numpy as np


def point2id(point, m):
    for key in m:
        lat = m[key]['lat']
        lng = m[key]['lng']
        if (lat == point[0]) and (lng == point[1]):
            return key

    raise RuntimeError('Point id not found in call to voronoi.point2id()')


def point_map2segments(m):
    ids = []
    lats = []
    lngs = []
    point_list = []
    for key in m:
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
    points = np.array(point_list)

    min_distance = max(max_lat - min_lat, max_lng - min_lng)
    safety_margin = min_distance * 2
    # Get points at corners of buffered bbox
    fake_points = box(min_lat - safety_margin,
                      min_lng - safety_margin,
                      max_lat + safety_margin,
                      max_lng + safety_margin).exterior.coords[:-1]

    # Make voronoi
    vor = spa.Voronoi(points + fake_points)

    # TODO: remove fake points?

    # Build segments
    verts = vor.verts
    segments = []
    for i in range(len(vor.ridge_vertices)):
        rverts = vor.rige_vertices[i]
        rpoints = vor.ridge_points[i]
        p1 = verts[rverts[0]]
        p2 = verts[rverts[1]]
        seg = {'x1': p1[0],
               'y1': p1[1],
               'x2': p2[0],
               'y2': p2[1],
               'id1': point2id(rpoints[0], m),
               'id2': point2id(rpoints[1], m)}
        segments.append(seg)

    return segments
