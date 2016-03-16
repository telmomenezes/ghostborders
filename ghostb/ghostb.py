import click
import ghostb.cropdata
from ghostb.db import DB
from ghostb.locations import Locations
from ghostb.config import Config
from ghostb.retriever import Retriever
from ghostb.fixlocations import FixLocations
from ghostb.cropborders import CropBorders
from ghostb.useractivity import UserActivity
from ghostb.userlocation import UserLocation
from ghostb.userhome import UserHome
from ghostb.photodensity import PhotoDensity
from ghostb.comment_locations import CommentLocations
from ghostb.gen_graph import GenGraph
from ghostb.filter_dists import FilterDists
from ghostb.confmodel import normalize_with_confmodel
from ghostb.communities import Communities
from ghostb.distances import Distances
from ghostb.borders import Borders
from ghostb.draw_map import draw_map
from ghostb.draw_map2 import draw_map2
from ghostb.locphotos import LocPhotos
from ghostb.graphinfo import graphinfo
from ghostb.scales import Scales
from ghostb.locs_metrics import LocsMetrics


@click.group()
@click.option('--db', help='Database name.')
@click.option('--locs_file', help='Path to locations file.')
@click.option('--region', help='Region name.')
@click.option('--country_code', help='Country code.')
@click.option('--min_lat', help='Minimum latitude.')
@click.option('--max_lat', help='Maximum latitude.')
@click.option('--min_lng', help='Minimum longitude.')
@click.option('--max_lng', help='Maximum longitude.')
@click.option('--rows', help='Number of rows.')
@click.option('--cols', help='Number of columns.')
@click.option('--infile', help='Input file.')
@click.option('--outfile', help='Output file.', default=None)
@click.option('--indir', help='Input directory.')
@click.option('--outdir', help='Output directory.', default=None)
@click.option('--smooth/--nosmooth', help='Smooth communities.', default=False)
@click.option('--shapefile', help='Shape file.', multiple=True)
@click.option('--runs', help='Number of runs.', default=100)
@click.option('--two/--many', default=False)
@click.option('--photo_dens_file', help='Photo densities file.', default=None)
@click.option('--pop_dens_file', help='Population densities file.', default=None)
@click.option('--osm/--noosm', default=False)
@click.option('--resolution', help='Map resolution.', default='i')
@click.option('--width', help='Map width.', default=50.)
@click.option('--best/--all', default=False)
@click.option('--max_dist', help='Maximum distance.')
@click.option('--graph_file', help='Output graph file.', default='')
@click.option('--dist_file', help='Output distribution file.', default='')
@click.option('--max_time', help='Maximum time.', default=-1)
@click.option('--intervals', help='Number of intervals.', default=4)
@click.option('--thick', help='Line thickness factor.', default=1.)
@click.option('--scale', help='Scale type.', default='percentiles')
@click.option('--metric', help='Metric type.')
@click.option('--table', help='Table name.', default='media')
@click.pass_context
def cli(ctx, db, locs_file, region, country_code, min_lat, max_lat, min_lng,
        max_lng,rows, cols, infile, outfile, smooth, indir, outdir, shapefile,
        runs, two, photo_dens_file, pop_dens_file, osm, resolution, width, best,
        max_dist, graph_file, dist_file, max_time, intervals, thick, scale, metric,
        table):
    ctx.obj = {
        'config': Config('ghostb.conf'),
        'dbname': db,
        'locs_file': locs_file,
        'region': region,
        'country_code': country_code,
        'min_lat': min_lat,
        'max_lat': max_lat,
        'min_lng': min_lng,
        'max_lng': max_lng,
        'rows': rows,
        'cols': cols,
        'infile': infile,
        'outfile': outfile,
        'indir': indir,
        'outdir': outdir,
        'smooth': smooth,
        'shapefile': shapefile,
        'runs': runs,
        'two': two,
        'photo_dens_file': photo_dens_file,
        'pop_dens_file': pop_dens_file,
        'osm': osm,
        'resolution': resolution,
        'width': width,
        'best': best,
        'max_dist': max_dist,
        'graph_file': graph_file,
        'dist_file': dist_file,
        'max_time': max_time,
        'intervals': intervals,
        'thick': thick,
        'scale': scale,
        'metric': metric,
        'table': table
    }


@cli.command()
@click.pass_context
def create_db(ctx):
    click.echo('Creating database')
    db = DB(ctx.obj['dbname'], ctx.obj['config'])
    db.create_db()
    db.close()


@cli.command()
@click.pass_context
def add_locations(ctx):
    country_code = ctx.obj['country_code']
    click.echo('Adding locations for %s' % country_code)
    db = DB(ctx.obj['dbname'], ctx.obj['config'])
    db.open()
    locs = Locations(db)
    (points, inserted) = locs.add_locations(ctx.obj['locs_file'], country_code)
    db.close()
    click.echo('%d points found, %d points added.' % (points, inserted))


@cli.command()
@click.pass_context
def add_area(ctx):
    min_lat = float(ctx.obj['min_lat'])
    min_lng = float(ctx.obj['min_lng'])
    max_lat = float(ctx.obj['max_lat'])
    max_lng = float(ctx.obj['max_lng'])
    click.echo('Adding locations in area: [%s, %s, %s, %s]' % (min_lat, min_lng, max_lat, max_lng))
    db = DB(ctx.obj['dbname'], ctx.obj['config'])
    db.open()
    locs = Locations(db)
    (points, inserted) = locs.add_area(ctx.obj['locs_file'],
                                       min_lat, min_lng, max_lat, max_lng)
    db.close()
    click.echo('%d points found, %d points added.' % (points, inserted))


@cli.command()
@click.pass_context
def add_grid(ctx):
    min_lat = float(ctx.obj['min_lat'])
    min_lng = float(ctx.obj['min_lng'])
    max_lat = float(ctx.obj['max_lat'])
    max_lng = float(ctx.obj['max_lng'])
    rows = int(ctx.obj['rows'])
    cols = int(ctx.obj['cols'])
    click.echo('Adding grid of locations for area: [%s, %s, %s, %s]' % (min_lat, min_lng, max_lat, max_lng))
    db = DB(ctx.obj['dbname'], ctx.obj['config'])
    db.open()
    locs = Locations(db)
    locs.add_grid(min_lat, min_lng, max_lat, max_lng, rows, cols)
    db.close()

@cli.command()
@click.pass_context
def add_region_grid(ctx):
    region = ctx.obj['region']
    rows = int(ctx.obj['rows'])
    cols = int(ctx.obj['cols'])
    click.echo('Adding grid of locations for region: %s' % region)
    db = DB(ctx.obj['dbname'], ctx.obj['config'])
    db.open()
    locs = Locations(db)
    locs.add_region_grid(region, rows, cols)
    db.close()

@cli.command()
@click.pass_context
def clean_locations(ctx):
    click.echo('Cleaning location data')
    db = DB(ctx.obj['dbname'], ctx.obj['config'])
    db.open()
    locs = Locations(db)
    locs.clean()
    db.close()
    click.echo('done.')


@cli.command()
@click.pass_context
def retrieve(ctx):
    click.echo('Retrieving Instagram data')
    config = ctx.obj['config']
    db = DB(ctx.obj['dbname'], config)
    db.open()
    retriever = Retriever(config, db)
    retriever.run()
    db.close()


@cli.command()
@click.pass_context
def fix_locations(ctx):
    click.echo('Fixing locations')
    config = ctx.obj['config']
    db = DB(ctx.obj['dbname'], config)
    db.open()
    fixer = FixLocations(db)
    fixer.run()
    db.close()


@cli.command()
@click.pass_context
def crop_borders(ctx):
    infile = ctx.obj['infile']
    shapefile = ctx.obj['shapefile']
    cropper = CropBorders(infile, shapefile)
    cropper.crop()
    cropper.write()


@cli.command()
@click.pass_context
def user_activity(ctx):
    click.echo('Computing user activity')
    config = ctx.obj['config']
    db = DB(ctx.obj['dbname'], config)
    db.open()
    activity = UserActivity(db)
    activity.update()
    db.close()


@cli.command()
@click.pass_context
def user_locations(ctx):
    click.echo('Computing userlocations')
    config = ctx.obj['config']
    db = DB(ctx.obj['dbname'], config)
    db.open()
    ul = UserLocation(db)
    ul.generate()
    db.close()


@cli.command()
@click.pass_context
def userhome(ctx):
    click.echo('Computing user homes')
    config = ctx.obj['config']
    db = DB(ctx.obj['dbname'], config)
    db.open()
    uhome = UserHome(db)
    uhome.generate()
    db.close()


@cli.command()
@click.pass_context
def photodensity(ctx):
    config = ctx.obj['config']
    db = DB(ctx.obj['dbname'], config)
    db.open()
    pd = PhotoDensity(db)
    pd.generate()
    db.close()


@cli.command()
@click.pass_context
def comment_locations(ctx):
    config = ctx.obj['config']
    db = DB(ctx.obj['dbname'], config)
    db.open()
    cl = CommentLocations(db)
    cl.fix()
    db.close()


@cli.command()
@click.pass_context
def crop_rectangle(ctx):
    min_lat = float(ctx.obj['min_lat'])
    min_lng = float(ctx.obj['min_lng'])
    max_lat = float(ctx.obj['max_lat'])
    max_lng = float(ctx.obj['max_lng'])
    db = DB(ctx.obj['dbname'], ctx.obj['config'])
    db.open()
    ghostb.cropdata.crop_rectangle(db, min_lat, min_lng, max_lat, max_lng)
    db.close()


@cli.command()
@click.pass_context
def crop_region(ctx):
    region = ctx.obj['region']
    db = DB(ctx.obj['dbname'], ctx.obj['config'])
    db.open()
    ghostb.cropdata.crop_region(db, region)
    db.close()


@cli.command()
@click.pass_context
def gen_graph(ctx):
    dbname = ctx.obj['dbname']
    graph_file = ctx.obj['graph_file']
    dist_file = ctx.obj['dist_file']
    table = ctx.obj['table']
    max_time = ctx.obj['max_time']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    gg = GenGraph(db, graph_file, dist_file, table, max_time)
    gg.generate()
    db.close()

    
@cli.command()
@click.pass_context
def filter_dists(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    max_dist = float(ctx.obj['max_dist'])
    fd = FilterDists(db)
    fd.filter(infile, outfile, max_dist)
    db.close()


@cli.command()
@click.pass_context
def confmodel(ctx):
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    normalize_with_confmodel(infile, outfile)


@cli.command()
@click.pass_context
def communities(ctx):
    infile = ctx.obj['infile']
    outdir = ctx.obj['outdir']
    outfile = ctx.obj['outfile']
    two = ctx.obj['two']
    runs = int(ctx.obj['runs'])
    best = ctx.obj['best']
    comms = Communities(infile)
    comms.compute_n_times(outdir, outfile, two, runs, best)


@cli.command()
@click.pass_context
def distances(ctx):
    dbname = ctx.obj['dbname']
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    dist = Distances(db)
    dist.compute(infile, outfile)
    db.close()


@cli.command()
@click.pass_context
def borders(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    indir = ctx.obj['indir']
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    smooth = ctx.obj['smooth']
    bs = Borders(db, smooth)
    bs.process(indir, infile, outfile)


@cli.command()
@click.pass_context
def draw(ctx):
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    region = ctx.obj['region']
    photo_dens_file = ctx.obj['photo_dens_file']
    pop_dens_file = ctx.obj['pop_dens_file']
    osm = ctx.obj['osm']
    resolution = ctx.obj['resolution']
    width = ctx.obj['width']
    draw_map(borders_file=infile,
             output_file=outfile,
             region=region,
             photo_dens_file=photo_dens_file,
             pop_dens_file=pop_dens_file,
             osm=osm,
             resolution=resolution,
             width=width)


@cli.command()
@click.pass_context
def draw2(ctx):
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    region = ctx.obj['region']
    photo_dens_file = ctx.obj['photo_dens_file']
    pop_dens_file = ctx.obj['pop_dens_file']
    osm = ctx.obj['osm']
    resolution = ctx.obj['resolution']
    width = ctx.obj['width']
    thick = float(ctx.obj['thick'])
    draw_map2(borders_file=infile,
              output_file=outfile,
              region=region,
              photo_dens_file=photo_dens_file,
              pop_dens_file=pop_dens_file,
              osm=osm,
              resolution=resolution,
              width=width,
              thickness=thick)

    
@cli.command()
@click.pass_context
def locphotos(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    lp = LocPhotos(db)
    lp.update()


@cli.command()
@click.pass_context
def graph_info(ctx):
    infile = ctx.obj['infile']
    graphinfo(infile)


@cli.command()
@click.pass_context
def scales_graphs(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    infile = ctx.obj['infile']
    outdir = ctx.obj['outdir']
    intervals = int(ctx.obj['intervals'])
    scale = ctx.obj['scale']
    table = ctx.obj['table']
    
    scales = Scales(outdir, intervals)
    scales.generate_graphs(db, infile, scale, table)


@cli.command()
@click.pass_context
def scales_normalize(ctx):
    outdir = ctx.obj['outdir']
    intervals = int(ctx.obj['intervals'])
    
    scales = Scales(outdir, intervals)
    scales.normalize()


@cli.command()
@click.pass_context
def scales_communities(ctx):
    outdir = ctx.obj['outdir']
    two = ctx.obj['two']
    runs = int(ctx.obj['runs'])
    best = ctx.obj['best']
    intervals = int(ctx.obj['intervals'])

    scales = Scales(outdir, intervals)
    scales.generate_communities(two, runs, best)

    
@cli.command()
@click.pass_context
def scales_rand(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    outdir = ctx.obj['outdir']
    intervals = int(ctx.obj['intervals'])

    scales = Scales(outdir, intervals)
    scales.rand_index_seq(db)


@cli.command()
@click.pass_context
def scales_metric(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    outdir = ctx.obj['outdir']
    intervals = int(ctx.obj['intervals'])
    smooth = ctx.obj['smooth']
    scale = ctx.obj['scale']
    infile = ctx.obj['infile']
    metric = ctx.obj['metric']

    scales = Scales(outdir, intervals)
    scales.metric(metric, db, smooth, scale, infile)


@cli.command()
@click.pass_context
def scales_borders(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    outdir = ctx.obj['outdir']
    best = ctx.obj['best']
    smooth = ctx.obj['smooth']
    intervals = int(ctx.obj['intervals'])
    
    scales = Scales(outdir, intervals)
    scales.generate_borders(db, best, smooth)


@cli.command()
@click.pass_context
def scales_multi_borders(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    outdir = ctx.obj['outdir']
    outfile = ctx.obj['outfile']
    smooth = ctx.obj['smooth']
    intervals = int(ctx.obj['intervals'])
    
    scales = Scales(outdir, intervals)
    scales.generate_multi_borders(db, outfile, smooth)


@cli.command()
@click.pass_context
def scales_crop_borders(ctx):
    outdir = ctx.obj['outdir']
    shapefile = ctx.obj['shapefile']
    intervals = int(ctx.obj['intervals'])

    scales = Scales(outdir, intervals)
    scales.crop_borders(shapefile)


@cli.command()
@click.pass_context
def scales_combine_borders(ctx):
    outdir = ctx.obj['outdir']
    outfile = ctx.obj['outfile']
    intervals = int(ctx.obj['intervals'])
    
    scales = Scales(outdir, intervals)
    scales.combine_borders(outfile)


@cli.command()
@click.pass_context
def scales_maps(ctx):
    outdir = ctx.obj['outdir']
    region = ctx.obj['region']
    intervals = int(ctx.obj['intervals'])
    
    scales = Scales(outdir, intervals)
    scales.generate_maps(region)


@cli.command()
@click.pass_context
def locs_metrics(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    outfile = ctx.obj['outfile']
    lm = LocsMetrics(db)
    lm.generate(outfile)


if __name__ == '__main__':
    cli()
