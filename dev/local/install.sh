#!/bin/bash
# Bootstrap delphi-epidata
#
# Downloads the repos needed for local delphi-epidata development into current dir 
# and provides a Makefile with Docker control commands.

mkdir -p repos/delphi
cd repos/delphi
git clone https://github.com/cmu-delphi/operations
git clone https://github.com/cmu-delphi/delphi-epidata
git clone https://github.com/cmu-delphi/utils
git clone https://github.com/cmu-delphi/flu-contest
git clone https://github.com/cmu-delphi/nowcast
git clone https://github.com/cmu-delphi/github-deploy-repo
cd ../../

mkdir -p repos/undefx
cd repos/undefx
git clone https://github.com/undefx/py3tester
git clone https://github.com/undefx/undef-analysis
cd ../../

mkdir -p docker-logs

ln -s repos/delphi/delphi-epidata/dev/local/Makefile
ln -s repos/delphi/delphi-epidata/dev/local/.dockerignore
