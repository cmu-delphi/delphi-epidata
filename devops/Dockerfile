FROM node:lts-buster AS builder
WORKDIR /src
COPY . /src
RUN npm ci && npm run build

FROM tiangolo/meinheld-gunicorn:python3.8
LABEL org.opencontainers.image.source=https://github.com/cmu-delphi/delphi-epidata

COPY ./devops/gunicorn_conf.py /app
COPY ./devops/start_wrapper.sh /
RUN mkdir -p /app/delphi/epidata
COPY ./src/server /app/delphi/epidata/server
COPY ./src/common /app/delphi/epidata/common
COPY --from=builder ./src/build/lib/ /app/delphi/epidata/lib/

COPY requirements.api.txt /app/requirements_also.txt

RUN ln -s -f /usr/share/zoneinfo/America/New_York /etc/localtime \
      && rm -rf /app/delphi/epidata/__pycache__ \
      && chmod -R o+r /app/delphi/epidata \
      && chmod 755 /start_wrapper.sh \
      && pip install --no-cache-dir -r /tmp/requirements.txt -r requirements_also.txt
# the file /tmp/requirements.txt is created in the parent docker definition.  (see:
#   https://github.com/tiangolo/meinheld-gunicorn-docker/blob/master/docker-images/python3.8.dockerfile#L5 )
# this combined requirements installation ensures all version constrants are accounted for.
# disable python stdout buffering
ENV PYTHONUNBUFFERED 1

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "/start_wrapper.sh" ]
