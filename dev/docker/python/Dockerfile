FROM python:3.8-buster

RUN apt-get update && apt-get install -y r-base && Rscript -e "install.packages(c('httr','xml2'))"

WORKDIR /usr/src/app

RUN ln -s -f /usr/share/zoneinfo/America/New_York /etc/localtime && \
    mkdir delphi && \
    chmod -R o+r delphi/

COPY repos/delphi/operations/src delphi/operations
COPY repos/delphi/utils/src delphi/utils
COPY repos/delphi/delphi-epidata/src delphi/epidata

COPY repos/delphi/delphi-epidata/requirements.*.txt .
RUN install --no-cache-dir -r requirements.api.txt -r requirements.dev.txt
