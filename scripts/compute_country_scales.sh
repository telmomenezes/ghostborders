#!/bin/bash

ghostb --db $1 --infile $1/full-graph.csv --outfile $1/filtered-graph.csv --min_degree 10 replace_low_degree
ghostb --db $1 --infile $1/filtered-graph.csv --outfile $1/dists.csv dists
cp $1/filtered-graph.csv $1/graph-d100.csv
ghostb --db $1 --infile $1/dists.csv --outdir $1 scales_graphs
ghostb --outdir $1 --best scales_communities
ghostb --db $1 --outdir $1 --outfile $1/borders.csv --best --scales 25,50,75,100 --smooth scales_multi_borders