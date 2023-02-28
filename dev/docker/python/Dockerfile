FROM python:3.8-buster

WORKDIR /usr/src/app

COPY repos repos
COPY repos/delphi/delphi-epidata/dev/docker/python/setup.sh .


RUN ln -s -f /usr/share/zoneinfo/America/New_York /etc/localtime && \
    chmod -R o+r repos/ && \
    bash setup.sh && \
    pip install --no-cache-dir -r repos/delphi/delphi-epidata/requirements.api.txt -r repos/delphi/delphi-epidata/requirements.dev.txt
