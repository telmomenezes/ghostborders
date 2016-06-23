#   Copyright (c) 2016 Centre Marc Bloch Berlin
#   (An-Institut der Humboldt Universitat, UMIFRE CNRS-MAE).
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


import click
import ghostb.graph
import ghostb.cropdata
from ghostb.db import DB
from ghostb.locations import Locations
from ghostb.config import Config
from ghostb.retriever import Retriever
from ghostb.fixlocations import FixLocations
from ghostb.photodensity import PhotoDensity
from ghostb.gen_graph import GenGraph
from ghostb.userscales import UserScales
from ghostb.filter_dists import FilterDists
from ghostb.replace_low_degree import ReplaceLowDegree
from ghostb.communities import Communities
from ghostb.distances import Distances
from ghostb.borders import Borders
from ghostb.locphotos import LocPhotos
from ghostb.graphinfo import graphinfo
from ghostb.scales import Scales
from ghostb.locs_metrics import LocsMetrics
from ghostb.breakpoints import find_breakpoints


def parse_scales(scales):
    if len(scales) == 0:
        return []
    else:
        return [int(x) for x in scales.split(',')]


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
@click.option('--runs', help='Number of runs.', default=100)
@click.option('--two/--many', default=False)
@click.option('--best/--all', default=False)
@click.option('--max_dist', help='Maximum distance.')
@click.option('--min_weight', help='Minimum edge weight.', default=5.0)
@click.option('--min_degree', help='Minimum location degree.', default=5.0)
@click.option('--intervals', help='Number of intervals.', default=100)
@click.option('--scale', help='Scale type.', default='percentiles')
@click.option('--metric', help='Metric type.', default='herfindahl')
@click.option('--table', help='Table name.', default='media')
@click.option('--scales', help='List of scales.', default='')
@click.option('--optimize', help='What to optimize for (speed/memory).', default='speed')
@click.pass_context
def cli(ctx, db, locs_file, region, country_code, min_lat, max_lat, min_lng,
        max_lng, rows, cols, infile, outfile, smooth, indir, outdir, runs, two,
        best, max_dist, min_weight, min_degree, intervals, scale, metric, table,
        scales, optimize):
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
        'runs': runs,
        'two': two,
        'best': best,
        'max_dist': max_dist,
        'min_weight': min_weight,
        'min_degree': min_degree,
        'intervals': intervals,
        'scale': scale,
        'metric': metric,
        'table': table,
        'scales': parse_scales(scales),
        'optimize': optimize
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
def photodensity(ctx):
    config = ctx.obj['config']
    db = DB(ctx.obj['dbname'], config)
    db.open()
    pd = PhotoDensity(db)
    pd.generate()
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
    outfile = ctx.obj['outfile']
    table = ctx.obj['table']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    gg = GenGraph(db, outfile, table)
    gg.generate()
    db.close()


@cli.command()
@click.pass_context
def userscales(ctx):
    dbname = ctx.obj['dbname']
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    scales = ctx.obj['scales']
    table = ctx.obj['table']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    us = UserScales(db, outfile, infile, scales, table)
    us.generate()
    db.close()


@cli.command()
@click.pass_context
def dists(ctx):
    dbname = ctx.obj['dbname']
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    g = ghostb.graph.read_graph(infile)
    ghostb.graph.write_dists(g, db, outfile)
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
    ghostb.graph.normalize_with_confmodel(infile, outfile)


@cli.command()
@click.pass_context
def write_degrees(ctx):
    infile = ctx.obj['infile']
    g = ghostb.graph.read_graph(infile)
    ghostb.graph.write_degrees(g)


@cli.command()
@click.pass_context
def filter_low_weight(ctx):
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    min_weight = float(ctx.obj['min_weight'])
    g = ghostb.graph.read_graph(infile)
    g_new = ghostb.graph.filter_low_weight(g, min_weight)
    ghostb.graph.write_graph(g_new, outfile)


@cli.command()
@click.pass_context
def replace_low_degree(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    min_degree = float(ctx.obj['min_degree'])
    rld = ReplaceLowDegree(db, infile, min_degree)
    rld.run(outfile)
    db.close()


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
def locs_metrics(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    outfile = ctx.obj['outfile']
    lm = LocsMetrics(db)
    lm.generate(outfile)


@cli.command()
@click.pass_context
def scales_graphs(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    outdir = ctx.obj['outdir']
    intervals = int(ctx.obj['intervals'])
    scale = ctx.obj['scale']
    table = ctx.obj['table']
    
    scales = Scales(outdir, intervals)
    scales.generate_graphs(db, scale, table)


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
def scales_metric(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    outdir = ctx.obj['outdir']
    best = ctx.obj['best']
    intervals = int(ctx.obj['intervals'])
    smooth = ctx.obj['smooth']
    scale = ctx.obj['scale']
    metric = ctx.obj['metric']

    scales = Scales(outdir, intervals)
    scales.metric(metric, db, best, smooth, scale)


@cli.command()
@click.pass_context
def similarity_matrix(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    outdir = ctx.obj['outdir']
    intervals = int(ctx.obj['intervals'])
    smooth = ctx.obj['smooth']
    optimize = ctx.obj['optimize']

    scales = Scales(outdir, intervals)
    scales.similarity_matrix(db, smooth, optimize)


@cli.command()
@click.pass_context
def dist_sequence(ctx):
    dbname = ctx.obj['dbname']
    db = DB(dbname, ctx.obj['config'])
    db.open()
    outdir = ctx.obj['outdir']
    intervals = int(ctx.obj['intervals'])
    smooth = ctx.obj['smooth']

    scales = Scales(outdir, intervals)
    scales.dist_sequence(db, smooth)


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
    scales = ctx.obj['scales']

    s = Scales(outdir, intervals)
    s.generate_multi_borders(db, outfile, smooth, scales)


@cli.command()
@click.pass_context
def breakpoints(ctx):
    infile = ctx.obj['infile']
    intervals = int(ctx.obj['intervals'])

    find_breakpoints(infile, intervals)


if __name__ == '__main__':
    cli()
