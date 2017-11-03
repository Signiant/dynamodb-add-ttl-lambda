#!/bin/bash

echo "Creating dist folder"
mkdir -p dist
echo "Copying lambda code into dist folder"
cp -f lambda/dynamodb-add-ttl.py ./dist/dynamodb-add-ttl.py
cd dist
echo "Creating lambda zip"
zip -r dynamodb-add-ttl .
cd ..
echo "DONE"
