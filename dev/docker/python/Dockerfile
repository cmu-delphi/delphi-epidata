# start with the `delphi_python` image
FROM delphi_python

COPY repos/delphi/delphi-epidata/src/acquisition/covidcast/logger.py /usr/src/app/delphi/epidata/server

RUN pip install --no-cache-dir -r repos/delphi/delphi-epidata/requirements.txt -r repos/delphi/delphi-epidata/requirements.dev.txt
