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


from ghostb.scales import Scales
from ghostb.cropborders import CropBorders
from ghostb.draw_map import DrawMap


class ScalesVis(Scales):
    def __init__(self, outdir, intervals):
        super(ScalesVis, self).__init__(outdir, intervals)
                
    def crop_borders(self, shapefile):
        for per_dist in self.percent_range():
            bord_file = self.bord_path(per_dist)
            print('Cropping: %s' % bord_file)
            cropper = CropBorders(bord_file, shapefile)
            cropper.crop()
            cropper.write(bord_file)
                
    def generate_maps(self, region):
        for per_dist in self.percent_range():
            bord_file = self.bord_path(per_dist)
            map_file = self.map_path(per_dist)
            print('drawing map: %s' % map_file)
            DrawMap(bord_file, map_file, region, osm=True).draw()
