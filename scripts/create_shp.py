# Joins a shp file from EUROSTAT with the xls with the region names so
# the resulting shp file has the name of every region and the code.
# Roger Veciana, oct 2013
from osgeo import ogr
from os.path import exists
from os.path import basename
from os.path import splitext
from os import remove, sys


def create_shp(in_shp, out_shp, extra_data):
    print("Extracting data")
    
    in_ds = ogr.Open(in_shp)
    if in_ds is None:
        print("Open failed.\n")
        sys.exit(1)
    in_lyr = in_ds.GetLayerByName(splitext(basename(in_shp))[0])
    if in_lyr is None:
        print("Error opening layer")
        sys.exit(1)

    if exists(out_shp):
        remove(out_shp)
    driver_name = "ESRI Shapefile"
    drv = ogr.GetDriverByName(driver_name)
    if drv is None:
        print("%s driver not available.\n" % driver_name)
        sys.exit(1)
    out_ds = drv.CreateDataSource(out_shp)
    if out_ds is None:
        print("Creation of output file failed.\n")
        sys.exit(1)
    proj = in_lyr.GetSpatialRef()
    # Creating the layer with its fields
    out_lyr = out_ds.CreateLayer( 
        splitext(basename(out_shp))[0], proj, ogr.wkbMultiPolygon)
    lyr_def = in_lyr.GetLayerDefn()
    for i in range(lyr_def.GetFieldCount()):
        out_lyr.CreateField(lyr_def.GetFieldDefn(i))

    field_defn = ogr.FieldDefn("NAME", ogr.OFTString)
    out_lyr.CreateField(field_defn)

    field_defn = ogr.FieldDefn("DENSITY", ogr.OFTInteger)
    out_lyr.CreateField(field_defn)

    # Writing all the features
    in_lyr.ResetReading()
    for feat_in in in_lyr:
        value = feat_in.GetFieldAsString(feat_in.GetFieldIndex('NUTS_ID'))
        if value in extra_data:
            feat_out = ogr.Feature(out_lyr.GetLayerDefn())
            feat_out.SetField('NUTS_ID', value)
            feat_out.SetField('DENSITY', extra_data[value]['density'])
            feat_out.SetField('STAT_LEVL_', int(extra_data[value]['level']))
            feat_out.SetField('SHAPE_Area', feat_in.GetFieldAsString(feat_in.GetFieldIndex('SHAPE_Area')))
            feat_out.SetField('SHAPE_Leng', feat_in.GetFieldAsString(feat_in.GetFieldIndex('SHAPE_Leng')))

            feat_out.SetGeometry(feat_in.GetGeometryRef())
            out_lyr.CreateFeature(feat_out)


def read_density(csv_file):
    # Reads the NUTS csv population file and returns the data in a dict
    dens_table = {}
    f = open(csv_file, "r")
    f.readline()  # Skip header
    for line in f:
        line_data = line.split('\t')
        try:
            dens_table[line_data[0]] = int(float(line_data[4]) * 1000)
        except ValueError:
            dens_table[line_data[0]] = -9999
    f.close()

    return dens_table


def read_names(csv_file, dens_data):
    # Reads a NUTS csv file and returns the data in a dict
    names_table = {}
    f = open(csv_file, "r")
    f.readline()  # Skip header
    for line in f:
        line_data = line.split(',')
        nuts_id = line_data[2][1:-1]
        names_table[nuts_id] = {
            'level': line_data[0][1:-1],
            'code': line_data[1][1:-1],
            'label': line_data[3][1:-1],
            'population': 0
        }
        if nuts_id in dens_data:
            names_table[nuts_id]['density'] = dens_data[nuts_id]

    f.close()

    return names_table


if __name__ == '__main__':
    density_data = read_density('data/NUTS/demo_r_d3dens.tsv')
    csv_data = read_names('data/NUTS/NUTS_33_20151103_191005.csv', density_data)
    create_shp('data/NUTS/NUTS_2010_10M_SH/Data/NUTS_RG_10M_2010.shp', 'dens/dens.shp', csv_data)
