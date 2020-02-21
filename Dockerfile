FROM python:3.7.2-stretch

WORKDIR assembly
EXPOSE 8080

COPY *.sh ./
COPY requirements.txt requirements.txt
COPY resources resources
COPY weather weather
COPY tests tests

RUN ["chmod", "+x", "run_server.sh"]

ENTRYPOINT "./run_server.sh"