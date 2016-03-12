#!/bin/bash
 
for i in `seq 0 99`;
do
    ghostb --db berlin --infile berlin-media/$i.csv --outfile berlin-borders/$i.csv borders
done    
