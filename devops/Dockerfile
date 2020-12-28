FROM tiangolo/meinheld-gunicorn:python3.7

COPY requirements.txt
RUN pip install --no-cache -r requirements.txt

COPY ./src/server/**/*.py ./src/server/**/*.html /app/app/