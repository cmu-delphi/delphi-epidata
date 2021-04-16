FROM node:lts-buster AS builder
WORKDIR /src
COPY . /src
RUN npm ci && npm run build

FROM tiangolo/meinheld-gunicorn:python3.7
LABEL org.opencontainers.image.source=https://github.com/cmu-delphi/delphi-epidata
# use delphi's timezome
RUN ln -s -f /usr/share/zoneinfo/America/New_York /etc/localtime

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# disable python stdout buffering
ENV PYTHONUNBUFFERED 1

COPY ./devops/gunicorn_conf.py /app
COPY ./devops/start_wrapper.sh /
COPY ./src/server/ /app/app/
COPY --from=builder ./src/build/lib/ /app/app/lib/
RUN rm -rf /app/app/__pycache__ /app/app/*.php \
      && chmod -R o+r /app/app \
      && chmod 755 /start_wrapper.sh

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "/start_wrapper.sh" ]
