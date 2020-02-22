#!/bin/bash

python -m virtualenv weather_env --python=$(which python3)
source weather_env/bin/activate

./run_server.sh