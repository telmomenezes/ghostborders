#!/bin/bash
 
for i in `seq 0 99`;
do
    ghostb --infile berlin-borders2/$i.csv --outfile berlin-borders2/$i.pdf --country berlin draw
done    
