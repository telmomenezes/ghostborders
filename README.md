# What is GhostBorders? #

TODO

# Installation #

## Clone Repository ##

TODO

## Install MySQL ##

TODO

## Create Config File ##

TODO

## Install Prerequisites ##

### OS X ###

* Install XCode


    $ brew install homebrew/science/igraph

#### ValueError: unknown locale: UTF-8 ####

Solution:
http://stackoverflow.com/questions/19961239/pelican-3-3-pelican-quickstart-error-valueerror-unknown-locale-utf-8

### Linux (Debian / Ubuntu) ###

    $ sudo apt-get install gfortran libopenblas-dev liblapack-dev
    $ sudo apt-get install -y libigraph0-dev
    $ sudo apt-get build-dep python-imaging
    $ sudo apt-get install libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev

## Create Virtual Environment and Install Python Packages ##

    $ export LC_ALL=C.UTF-8
    $ export LANG=C.UTF-8
    $ virtualenv -p /usr/local/bin/python3 venv
    $ source venv/bin/activate

    $ pip install --editable .
    $ pip install https://github.com/matplotlib/basemap/archive/v1.0.7rel.tar.gz

# How to use #

## Retrieve Data ##

### Create database ###

Creates the database to be used by further operations.

    $ ghostb --db <db_name> create_db

### Create locations ###

Add locations from file:

    $ ghostb --db <db_name> --locs_file <locations_file> --country_code <country_code> add_locations

Add a grid of points:

    $ ghostb --db <db_name> --min_lat <min_lat> --min_lng <min_lng> --max_lat <max_lat> --max_lng <max_lng> --rows <rows> --cols <cols> add_grid

### Retrive data from Instagram ###

    $ ghostb --db <db_name> retrieve

### Fix locations (attaches photos to the closest known location) ###

    $ ghostb --db <db_name> fix_locations

### Compute user activity ###

    $ ghostb --db <db_name> user_activity

### Compute user homebases ###

    $ ghostb --db <db_name> userhome

### Assign locations to comments ###

    $ ghostb --db <db_name> comment_locations

## Generate Simple Maps ##

#### Generate graphs ####

graph_file specifies the file path to write the graph to. If none is specified, the graph file is not generated.

dist_file specifies the file path to write the distance and time link distribution to. If none is specified, the distribution file is not generated.

max_time specifies a time thershold for links to be included in the graph. It does not affect the distribution.

    $ ghostb --db <db_name> [--graph_file <graph_output>] [--dist_file <dist_output>] [--max_time] <max_time> gen_graph

#### Filter distances ####

    $ ghostb --db <db_name> --infile <input_file> --outfile <output_file> --max_dist <max_distance> filter_dists

#### Normalize with configuration model ####

10 is a good value for the number of runs.

    $ ghostb --infile <input_file> --outfile <output_file> --runs <number_of_runs> confmodel

#### Find communities ####

100 is a good value for the number of runs.

    $ ghostb --infile <input_file> --outdir <output_directory> --runs <number_of_runs> [--best] communities

If the optional --best switch is specified, only the partition with the highest modularity is written. 

#### Compute borders ####

To use a directory as input:
    $ ghostb --db <db_name> --indir <input_directory> --outfile <output_file> borders

To use a file as input:
    $ ghostb --db <db_name> --infile <input_file> --outfile <output_file> borders

#### Crop borders ####

Takes a .csv borders file and a shapefile and outputs a new .csv borders file with the borders cropped as to not extend beyond the country limits defines in the shapefile.

    $ ghostb --infile <input file> --shapefile <shapefile> crop_borders > <output file>

The shapefile should be specified without the extension. Shapefiles can be obtained here:
http://www.gadm.org/country

#### Draw map ####

    $ ghostb --infile <borders_file> --outfile <output_file> --country <region> draw

Optional parameters:
* photo_dens_file: photo densities file
* pop_dens_file: population densities file
* osm: draw open street maps background (default: no)
* resolution: map resolution (default: i)
* width: map width

## Generate Multi-Scale Maps ##

TODO

# Contacts #

* telmo@telmomenezes.com