#!/bin/bash

source python/env/bin/activate

while read repo; do
    npm --prefix js start "$repo"
    python python/app.py "$repo"
done < repos.txt
