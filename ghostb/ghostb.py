import click
from ghostb.db import DB
from ghostb.locations import Locations
from ghostb.config import Config
from ghostb.retriever import Retriever
from ghostb.fixlocations import FixLocations
from ghostb.cropborders import CropBorders
from ghostb.useractivity import UserActivity
from ghostb.userlocation import UserLocation
from ghostb.monthly import Monthly
from ghostb.userhome import UserHome
from ghostb.photodensity import PhotoDensity
from ghostb.cropdata import CropData
from ghostb.comment_locations import CommentLocations
from ghostb.gen_graph import GenGraph
from ghostb.filter_dists import FilterDists
from ghostb.confmodel import normalize_with_confmodel
from ghostb.communities import Communities
from ghostb.distances import Distances
from ghostb.borders import Borders
from ghostb.draw_map import draw_map
from ghostb.locphotos import LocPhotos
from ghostb.graphinfo import graphinfo
from ghostb.flag import Flag


@click.group()
@click.option('--db', help='Database name.')
@click.option('--locs_file', help='Path to locations file.')
@click.option('--country', help='Country name.')
@click.option('--country_code', help='Country code.')
@click.option('--min_lat', help='Minimum latitude.')
@click.option('--max_lat', help='Maximum latitude.')
@click.option('--min_lng', help='Minimum longitude.')
@click.option('--max_lng', help='Maximum longitude.')
@click.option('--rows', help='Number of rows.')
@click.option('--cols', help='Number of columns.')
@click.option('--infile', help='Input file.')
@click.option('--outfile', help='Output file.')
@click.option('--indir', help='Input directory.')
@click.option('--outdir', help='Output directory.')
@click.option('--shapefile', help='Shape file.', multiple=True)
@click.option('--flagged/--ignoreflags', default=False)
@click.option('--graph_type', help='loc2loc, home2loc or home2home.')
@click.option('--runs', help='Number of runs.')
@click.option('--two/--many', default=False)
@click.option('--photo_dens_file', help='Photo densities file.', default=None)
@click.option('--pop_dens_file', help='Population densities file.', default=None)
@click.option('--osm/--noosm', default=False)
@click.option('--resolution', help='Map resolution.', default='i')
@click.option('--width', help='Map width.', default=50.)
@click.option('--best/--all', default=False)
@click.pass_context
def cli(ctx, db, locs_file, country, country_code, min_lat, max_lat, min_lng,
        max_lng,rows, cols, infile, outfile, indir, outdir, shapefile, flagged,
        graph_type, runs, two, photo_dens_file, pop_dens_file, osm, resolution,
        width, best):
    ctx.obj = {
        'config': Config('ghostb.conf'),
        'dbname': db,
        'locs_file': locs_file,
        'country': country,
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
        'shapefile': shapefile,
        'flagged': flagged,
        'graph_type': graph_type,
        'runs': runs,
        'two': two,
        'photo_dens_file': photo_dens_file,
        'pop_dens_file': pop_dens_file,
        'osm': osm,
        'resolution': resolution,
        'width': width,
        'best': best
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
def monthly(ctx):
    click.echo('Computing months')
    config = ctx.obj['config']
    db = DB(ctx.obj['dbname'], config)
    db.open()
    m = Monthly(db)
    m.generate()
    m.update_photos_month()
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
def crop_data(ctx):
    min_lat = float(ctx.obj['min_lat'])
    min_lng = float(ctx.obj['min_lng'])
    max_lat = float(ctx.obj['max_lat'])
    max_lng = float(ctx.obj['max_lng'])
    db = DB(ctx.obj['dbname'], ctx.obj['config'])
    db.open()
    cd = CropData(db, min_lat, min_lng, max_lat, max_lng)
    cd.crop()
    db.close()


@cli.command()
@click.pass_context
def gen_graph(ctx):
    dbname = ctx.obj['dbname']
    outfile = ctx.obj['outfile']
    graph_type = ctx.obj['graph_type']
    flagged = ctx.obj['flagged']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    gg = GenGraph(db, outfile, graph_type, flagged)
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
    fd = FilterDists(db)
    fd.filter(infile, outfile)
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
    two = ctx.obj['two']
    runs = int(ctx.obj['runs'])
    best = ctx.obj['best']
    comms = Communities(infile)
    comms.compute_n_times(outdir, two, runs, best)


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
    bs = Borders(db)
    bs.process(indir, infile, outfile)


@cli.command()
@click.pass_context
def mborders(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    indir = ctx.obj['indir']
    outfile = ctx.obj['outfile']
    bs = Borders(db)
    bs.process_multiple(indir, outfile)


@cli.command()
@click.pass_context
def draw(ctx):
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    country = ctx.obj['country']
    photo_dens_file = ctx.obj['photo_dens_file']
    pop_dens_file = ctx.obj['pop_dens_file']
    osm = ctx.obj['osm']
    resolution = ctx.obj['resolution']
    width = ctx.obj['width']
    draw_map(borders_file=infile,
             output_file=outfile,
             region=country,
             photo_dens_file=photo_dens_file,
             pop_dens_file=pop_dens_file,
             osm=osm,
             resolution=resolution,
             width=width)

    
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
def flag(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    fl = Flag(db)
    fl.flag()

    
@cli.command()
@click.pass_context
def unflag(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    fl = Flag(db)
    fl.unflag()


if __name__ == '__main__':
    cli()
