import math


def distance(p1, p2):
    # Haversine formula
    lat1 = math.radians(p1['lat'])
    lat2 = math.radians(p2['lat'])
    lng1 = math.radians(p1['lng'])
    lng2 = math.radians(p2['lng'])
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = math.pow(math.sin(dlat / 2.0), 2.0) + (math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(dlng / 2.0), 2.0))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    d = c * 6373.0
    return d


def centroid(locs):
    k = 0.0
    lat = 0.0
    lng = 0.0
    for loc in locs:
        w = float(loc['weight'])
        k += w
        lat += w * loc['lat']
        lng += w * loc['lng']
    lat /= k
    lng /= k
    return {
        'lat': lat,
        'lng': lng
    }
