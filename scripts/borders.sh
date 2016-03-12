#!/bin/bash

for i in $1/* 
do
  if test -f "$i" 
  then
    filename=$(basename "$i")
    filename="${filename%.*}"
    echo "Generating bord-$filename.pdf"
    ghostb --db berlin --infile $i --outfile "%1/bord-$filename.pdf" --smooth borders
  fi
done
