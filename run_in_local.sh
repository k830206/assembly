#!/bin/bash

python -m virtualenv weather --python=$(which python3)
source weather/bin/activate

./run_server.sh