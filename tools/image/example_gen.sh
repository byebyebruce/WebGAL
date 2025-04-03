#!/bin/bash

set -ex

#input=$1

curl -X POST \
-H "Content-Type: application/json" \
-d '{"prompt":"A little beautiful asian girl, wear a blue t shirt","rmbg":true}' http://localhost:5100/gen_image -o out.png
