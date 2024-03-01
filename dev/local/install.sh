#!/bin/bash
# Bootstrap delphi-epidata development
#
# Downloads the repos needed for local delphi-epidata development into current dir 
# and provides a Makefile with Docker control commands
# as well as pyproject/setup.cfg files for IDE mappings.
#
# Creates the directory structure:
#
#   driver/
#     .dockerignore
#     Makefile
#     repos/
#       pyproject.toml
#       setup.cfg
#       delphi/
#         operations/
#         delphi-epidata/
#         utils/
#
# Leaves you in driver, the main workdir.
#


mkdir -p driver/repos/delphi
cd driver/repos/delphi
git clone https://github.com/cmu-delphi/operations
git clone https://github.com/cmu-delphi/delphi-epidata
git clone https://github.com/cmu-delphi/utils
cd ../../

ln -s repos/delphi/delphi-epidata/dev/local/Makefile
ln -s repos/delphi/delphi-epidata/dev/local/.dockerignore
cd repos
ln -s delphi/delphi-epidata/dev/local/pyproject.toml
ln -s delphi/delphi-epidata/dev/local/setup.cfg
cd -
