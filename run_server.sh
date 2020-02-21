#!/bin/bash

pip3 install --upgrade pip
pip3 install -r requirements.txt

pylint weather/*.py

coverage run -m pytest tests
coverage report -m

export FLASK_APP=weather
export FLASK_ENV=development

flask run --port 8080