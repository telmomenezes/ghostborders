from ghostb.scales import Scales
from ghostb.cropborders import CropBorders
from ghostb.draw_map import draw_map


class ScalesVis(Scales):
    def __init__(self, outdir, intervals):
        self.outdir = outdir
        self.intervals = intervals
        self.per_table = None
                
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
            draw_map(bord_file, map_file, region, osm=True)
