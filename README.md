## What is GhostBorders? ##

* TBD

## Installation ##

    $ export LC_ALL=C.UTF-8
    $ export LANG=C.UTF-8
    $ virtualenv -p /usr/local/bin/python3 venv
    $ source venv/bin/activate

### OS X ###

    $ brew install homebrew/science/igraph
    $ pip install --editable .
    $ pip install basemap --allow-external basemap --allow-unverified basemap

#### ValueError: unknown locale: UTF-8 ####

Solution:
http://stackoverflow.com/questions/19961239/pelican-3-3-pelican-quickstart-error-valueerror-unknown-locale-utf-8

### Linux (Debian) ###

    $ sudo apt-get install -y libigraph0-dev
    $ pip install --editable .

## How to use ##

#### Create database ####

Creates the database to be used by further operations.

    $ ghostb --db <db_name> create_db

#### Create locations ####

Add a grid of points:

    $ ghostb --db <db_name> --min_lat <min_lat> --min_lng <min_lng> --max_lat <max_lat> --max_lng <max_lng> --rows <rows> --cols <cols> add_grid

#### Retrive data from Instagram ####

    $ ghostb --db <db_name> retrieve

#### Crop borders ####

Takes a .csv borders file and a shapefile and outputs a new .csv borders file with the borders cropped as to not extend beyond the country limits defines in the shapefile.

    $ ghostb --infile <input file> --shapefile <shapefile> crop_borders > <output file>

The shapefile should be specified without the extension. Shapefiles can be obtained here:
http://www.gadm.org/country

## Contacts ##

* telmo@telmomenezes.com