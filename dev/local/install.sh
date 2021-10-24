#!/bin/bash

mkdir -p driver/repos/delphi driver-logs
cd driver/repos/delphi
git clone https://github.com/cmu-delphi/operations
git clone https://github.com/cmu-delphi/delphi-epidata
git clone https://github.com/cmu-delphi/utils
cd ../../
ln -s repos/delphi/delphi-epidata/dev/local/epidata-refresh.sh
