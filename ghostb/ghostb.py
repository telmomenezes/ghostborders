import click
from ghostb.db import DB
from ghostb.locations import Locations
from ghostb.config import Config
from ghostb.retriever import Retriever
from ghostb.fixlocations import FixLocations
from ghostb.cropborders import CropBorders
from ghostb.useractivity import UserActivity
from ghostb.monthly import Monthly
from ghostb.userhome import UserHome
from ghostb.photodensity import PhotoDensity
from ghostb.cropdata import CropData
from ghostb.comment_locations import CommentLocations
from ghostb.locsgraph import LocsGraph
from ghostb.confmodel import normalize_with_confmodel
from ghostb.communities import Communities
from ghostb.distances import Distances
from ghostb.borders import Borders
# from ghostb.map import draw


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
@click.option('--directed/--undirected', default=False)
@click.option('--bymonth/--full', default=False)
@click.option('--table', help='media, comment or links.')
@click.option('--runs', help='Number of runs.')
@click.option('--two/--many', default=False)
@click.pass_context
def cli(ctx, db, locs_file, country, country_code, min_lat, max_lat, min_lng, max_lng, rows, cols, infile, outfile,
        indir, outdir, shapefile, directed, bymonth, table, runs, two):
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
        'directed': directed,
        'bymonth': bymonth,
        'table': table,
        'runs': runs,
        'two': two
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
def locsgraph(ctx):
    dbname = ctx.obj['dbname']
    directed = ctx.obj['directed']
    bymonth = ctx.obj['bymonth']
    table = ctx.obj['table']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    lg = LocsGraph(db, dbname, directed)
    lg.generate(table, bymonth)
    db.close()


@cli.command()
@click.pass_context
def confmodel(ctx):
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    runs = int(ctx.obj['runs'])
    normalize_with_confmodel(infile, outfile, runs)


@cli.command()
@click.pass_context
def communities(ctx):
    infile = ctx.obj['infile']
    outdir = ctx.obj['outdir']
    two = ctx.obj['two']
    runs = int(ctx.obj['runs'])
    comms = Communities(infile)
    comms.compute_n_times(outdir, two, runs)


@cli.command()
@click.pass_context
def distances(ctx):
    dbname = ctx.obj['dbname']
    table = ctx.obj['table']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    dist = Distances(db)
    dist.compute(table)
    db.close()


@cli.command()
@click.pass_context
def borders(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    indir = ctx.obj['indir']
    outfile = ctx.obj['outfile']
    bs = Borders(db)
    bs.process(indir, outfile)


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


# @cli.command()
# @click.pass_context
# def draw_map(ctx):
#     infile = ctx.obj['infile']
#     outfile = ctx.obj['outfile']
#     country = ctx.obj['country']
#     draw(infile, outfile, country)


if __name__ == '__main__':
    cli()
