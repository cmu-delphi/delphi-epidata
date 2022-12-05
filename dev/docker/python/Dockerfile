FROM python:3.8-buster

# use delphi's timezome
RUN ln -s -f /usr/share/zoneinfo/America/New_York /etc/localtime

# specify a working directory inside the container
WORKDIR /usr/src/app

# copy over all source files
COPY repos repos
RUN chmod -R o+r repos/

# configure the image to match the delphi server
COPY repos/delphi/delphi-epidata/dev/docker/python/setup.sh .
RUN bash setup.sh

# install python packages
RUN pip install --no-cache-dir -r repos/delphi/delphi-epidata/requirements.api.txt -r repos/delphi/delphi-epidata/requirements.dev.txt
