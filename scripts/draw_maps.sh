#!/bin/bash

for i in $1/bord-* 
do
  if test -f "$i" 
  then
    filename=$(basename "$i")
    filename="${filename%.*}"
    echo "Generating $filename.pdf"
    ghostb --infile $i --outfile "$filename.pdf" --region berlin --osm draw
  fi
done
