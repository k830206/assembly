#!/usr/bin/env bash
docker build -t assembly -f Dockerfile .

docker run -p 8080:8080 -it --rm --name wserver assembly:latest