# start with the `delphi_python` image
FROM delphi_python

RUN --mount=type=cache,target=/root/.cache/pip pip install -r repos/delphi/delphi-epidata/requirements.txt -r repos/delphi/delphi-epidata/requirements.dev.txt
