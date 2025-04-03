#!/bin/bash

set -ex

input=$1


curl -X POST -F "file=@$input" http://localhost:5100/remove_bg -o output.png
