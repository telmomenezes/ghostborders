# What is GhostBorders? #

GhostBorders is a set of tools to study socio-geographical borders using social media data.

It's capabilities include:

* Retrieving metadata from photos and other media shared in social media platforms. [Instagram](http://instagram.com) is currently supported;
* Generating location graphs from above data;
* Performing community detection on location graphs;
* Deriving borders from communities;
* Drawing maps with socio-geographical borders;
* Working with multiple scales.

# Installation #

Installation is performed by first cloning the source code to your computer. Then a number of prerequisites have to be installed, depending on the operating system. `pip` is used to complete the installation.

Everything is done on the terminal.

Two commands become available: `ghostb` and `ghostb_vis`. The first is multipurpose, while the second performs tasks related to map drawing. They are separated so that you can install only the prerequisites for `ghostb`. This can be useful because the prerequisites for `ghostb_vis` are tricky to install on some operating systems. This way you can still easily use such systems for data retrieval and graph computations.

## Clone Repository ##

Start by cloning the source code to your current local directory.

    $ git clone https://github.com/telmomenezes/ghostborders.git

## MariaDB / MySQL ##

GhostBorders uses either [MariaDB](http://mariadb.org) or [MySQL](http://mysql.com) as its main database. To install one of them in your server, refer to the instructions on their website.

## Create Config File ##

Copy the file `ghostb.conf.template` to `ghostb.conf` and open the latter in a text editor. Provide the correct information for the things below.

### Database ###

Provide the `host`, `user` name and `password` to access the database. If the database server is running on the local machine, `host` can be `localhost`. 

### Instagram API ###

To be able to make requests to the Instagram API, for retrieval tasks, you must provide a `CLIENT_ID` and `CLIENT_SECRET`. You can obtain these by registering on the [Instagram developers area](https://www.instagram.com/developer/).

### Time range ###

These are the UNIX timestamps to define a time range for retrieval tasks. Only photos created between the two timestamps will be retrieved.

## Prerequisites ##

### OS X ###

* XCode
* The `igraph` library. To install with [homebrew](http://brew.sh/):

    $ brew install homebrew/science/igraph

#### ValueError: unknown locale: UTF-8 ####

Solution if you have this problem:
http://stackoverflow.com/questions/19961239/pelican-3-3-pelican-quickstart-error-valueerror-unknown-locale-utf-8

### Linux (Debian / Ubuntu) ###

    $ sudo apt-get install gfortran libopenblas-dev liblapack-dev
    $ sudo apt-get install -y libigraph0-dev
    $ sudo apt-get build-dep python-imaging
    $ sudo apt-get install libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev

## Create Virtual Environment and Install Python Packages ##

It is advisable to work with virtual environments. To create one in the current directory you can do this:

    $ virtualenv -p /usr/local/bin/python3 venv

The, anytime you want to activate it:

    $ source venv/bin/activate

Finally, after activating the virtual environment above, you can install GhostBorders and its Python dependencies:

    $ pip install --editable .

The above is enough to run `ghostb` commands. If you also want to be able to run `ghostb_vis`, you must install the bascamp matplotlib module:

    $ pip install https://github.com/matplotlib/basemap/archive/v1.0.7rel.tar.gz

# How to use #

## Retrieve Data ##

### Create database ###

Creates the database to be used by further operations.

    $ ghostb --db <db_name> create_db

### Create locations ###

It is necessary to add a set of geographical locations to the database, for which the retrieval process can then request data. It is possible to add locations from a file, from a grid of points inside a given rectangle, or from a grid of points inside a predefined region.

For a country, using the provided file `cities1000.txt` to add locations is a good option:

    $ ghostb --db <db_name> --locs_file <locations_file> --country_code <country_code> add_locations

For any *ad hoc* region you can add a grid of points like so:

    $ ghostb --db <db_name> --min_lat <min_lat> --min_lng <min_lng> --max_lat <max_lat> --max_lng <max_lng> --rows <rows> --cols <cols> add_grid

For a predefined region, a grid can be added with this command:

    $ ghostb --db <db_name> --region <region> --rows <rows> --cols <cols> add_region_grid    

### Retrive data from Instagram ###

    $ ghostb --db <db_name> retrieve

### Fix locations (attaches photos to the closest known location) ###

    $ ghostb --db <db_name> fix_locations

### Assign locations to comments / likes (optional) ###

    $ ghostb --db <db_name> --table comment assign_locations
    $ ghostb --db <db_name> --table likes assign_locations

## Generate Simple Maps ##

#### Generate graphs ####

outfile specifies the file path to write the graph to.

    $ ghostb --db <db_name> --outfile <graph_output> gen_graph

#### Generate distances file ####

outfile specifies the file path to write the link distance distribution to.

    $ ghostb --db <db_name> --outfile <distances_output> dists

#### Filter out low weight edges ####

Default min_weight value is 5.

    $ ghostb --db <db_name> --infile <inut_graph> --outfile <output_graph> [--min_weight <min_weight>] --filter_low_weight

#### Filter distances (optional) ####

    $ ghostb --db <db_name> --infile <input_file> --outfile <output_file> --max_dist <max_distance> filter_dists

#### Normalize with configuration model (optional) ####

    $ ghostb --infile <input_file> --outfile <output_file> confmodel

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

    $ ghostb_vis --infile <input file> --shapefile <shapefile> crop_borders > <output file>

The shapefile should be specified without the extension. Shapefiles can be obtained here:
http://www.gadm.org/country

#### Draw map ####

    $ ghostb_vis --infile <borders_file> --outfile <output_file> --region <region> draw

Optional parameters:
* photo_dens_file: photo densities file
* pop_dens_file: population densities file
* osm: draw open street maps background (default: no)
* resolution: map resolution (default: i)
* width: map width

## Create Multi-Scale Maps ##

### Generate Distance Distribution File ###

    $ ghostb --db <db_name> --dist_file <dist_file> gen_graph

### Generate Graph Files ###

    $ ghostb --db <db_name> --infile <dist_file> --outdir <dir> scales_graphs

### Community Detection ###

    $ ghostb --outdir <dir> --best scales_communities

### Compute Borders ###

    $ ghostb --db <db_name> --outdir <dir> [--best] scales_borders

# Contacts #

* telmo@telmomenezes.com