FROM tiangolo/meinheld-gunicorn:python3.7
# use delphi's timezome
RUN ln -s -f /usr/share/zoneinfo/America/New_York /etc/localtime

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/server/**/*.py ./src/server/**/*.html /app/app/
RUN chmod -R o+r /app/app