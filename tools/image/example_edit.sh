#!/bin/bash

set -ex

#input=$1

curl -X POST \
  http://localhost:5100/edit_image \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$1" \
  -F "prompt=$2" \
  -F "rmbg=true" \
  -o edited_output.png