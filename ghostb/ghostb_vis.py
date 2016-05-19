import click
from ghostb.config import Config
from ghostb.cropborders import CropBorders
from ghostb.draw_map import draw_map
from ghostb.draw_map2 import draw_map2
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
@click.option('--thick', help='Line thickness factor.', default=1.)
@click.pass_context
def cli(ctx, locs_file, region, infile, outfile, outdir, shapefile,
        photo_dens_file, pop_dens_file, osm, resolution, width, intervals, thick):
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
        'thick': thick
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
    intervals = int(ctx.obj['intervals'])
    draw_map2(borders_file=infile,
              output_file=outfile,
              region=region,
              photo_dens_file=photo_dens_file,
              pop_dens_file=pop_dens_file,
              osm=osm,
              resolution=resolution,
              width=width,
              thickness=thick,
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
