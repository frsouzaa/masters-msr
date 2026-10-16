#!/bin/bash

url=$1

source python/env/bin/activate

if [ -z "$url" ]; then
    while read repo_url; do
        echo "Processing $repo_url"
        npm --prefix js start "$repo_url"
        python python/app.py "$repo_url"
    done < repos.txt
else
    npm --prefix js start "$url"
    python python/app.py "$url"
fi
