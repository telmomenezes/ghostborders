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


import click
from ghostb.config import Config
from ghostb.cropborders import CropBorders
from ghostb.draw_map import draw_map
from ghostb.draw_multi_map import draw_multi_map
from ghostb.scales_vis import ScalesVis


@click.group()
@click.option('--locs_file', help='Path to locations file.')
@click.option('--region', help='Region name.')
@click.option('--infile', help='Input file.')
@click.option('--outfile', help='Output file.', default=None)
@click.option('--outdir', help='Output directory.', default=None)
@click.option('--shapefile', help='Shape file.', multiple=True)
@click.option('--photo_dens_file', help='Photo densities file.', default=None)
@click.option('--pop_dens_file', help='Population densities file.', default=None)
@click.option('--osm/--noosm', default=False)
@click.option('--resolution', help='Map resolution.', default='i')
@click.option('--width', help='Map width.', default=50.)
@click.option('--intervals', help='Number of intervals.', default=100)
@click.option('--thick', help='Line thickness factor.', default=10.)
@click.option('--sep', help='Line separation factor.', default=0.0005)
@click.option('--color', help='Line color.', default='darkred')
@click.option('--linestyle', help='Line style.', default='solid')
@click.pass_context
def cli(ctx, locs_file, region, infile, outfile, outdir, shapefile, photo_dens_file, pop_dens_file, osm, resolution,
        width, intervals, thick, sep, color, linestyle):
    ctx.obj = {
        'config': Config('ghostb.conf'),
        'locs_file': locs_file,
        'region': region,
        'infile': infile,
        'outfile': outfile,
        'outdir': outdir,
        'shapefile': shapefile,
        'photo_dens_file': photo_dens_file,
        'pop_dens_file': pop_dens_file,
        'osm': osm,
        'resolution': resolution,
        'width': width,
        'intervals': intervals,
        'thick': thick,
        'sep': sep,
        'color': color,
        'linestyle': linestyle
    }


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
def draw(ctx):
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    region = ctx.obj['region']
    photo_dens_file = ctx.obj['photo_dens_file']
    pop_dens_file = ctx.obj['pop_dens_file']
    osm = ctx.obj['osm']
    resolution = ctx.obj['resolution']
    width = ctx.obj['width']
    thick = float(ctx.obj['thick'])
    color = ctx.obj['color']
    linestyle = ctx.obj['linestyle']
    draw_map(borders_file=infile,
             output_file=outfile,
             region=region,
             photo_dens_file=photo_dens_file,
             pop_dens_file=pop_dens_file,
             osm=osm,
             resolution=resolution,
             width=width,
             thick=thick,
             color=color,
             linestyle=linestyle)


@cli.command()
@click.pass_context
def draw_multi(ctx):
    infile = ctx.obj['infile']
    outfile = ctx.obj['outfile']
    region = ctx.obj['region']
    photo_dens_file = ctx.obj['photo_dens_file']
    pop_dens_file = ctx.obj['pop_dens_file']
    osm = ctx.obj['osm']
    resolution = ctx.obj['resolution']
    width = ctx.obj['width']
    thick = float(ctx.obj['thick'])
    sep = float(ctx.obj['sep'])
    intervals = int(ctx.obj['intervals'])
    draw_multi_map(borders_file=infile,
                   output_file=outfile,
                   region=region,
                   photo_dens_file=photo_dens_file,
                   pop_dens_file=pop_dens_file,
                   osm=osm,
                   resolution=resolution,
                   width=width,
                   thick=thick,
                   sep=sep,
                   intervals=intervals)


@cli.command()
@click.pass_context
def scales_crop_borders(ctx):
    outdir = ctx.obj['outdir']
    shapefile = ctx.obj['shapefile']
    intervals = int(ctx.obj['intervals'])

    scales = ScalesVis(outdir, intervals)
    scales.crop_borders(shapefile)


@cli.command()
@click.pass_context
def scales_maps(ctx):
    outdir = ctx.obj['outdir']
    region = ctx.obj['region']
    intervals = int(ctx.obj['intervals'])
    
    scales = ScalesVis(outdir, intervals)
    scales.generate_maps(region)


if __name__ == '__main__':
    cli()
