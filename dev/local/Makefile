# Docker control panel for delphi-epidata development.
#
# Usage: make <command> [pdb=1] [test=<test-subdir>]
#
# Assumes you have installed your environment using
# delphi-epidata/dev/local/install.sh.
#
# Checks for the delphi-net bridge and creates if it doesn't exist.
#
# Creates all prereq images (delphi_database, delphi_python) only if they don't
# exist. If you need to rebuild a prereq, you're probably doing something
# complicated, and can figure out the rebuild command on your own.
#
#
# Commands:
#
#   web:     Stops currently-running delphi_web_epidata instances, if any.
#            Rebuilds delphi_web_epidata image.
#            Runs image in the background and pipes stdout to a log file.
#
#   db:      Stops currently-running delphi_database_epidata instances, if any.
#            Rebuilds delphi_database_epidata image.
#            Runs image in the background and pipes stdout to a log file.
#            Blocks until database is ready to receive connections.
#
#   python:  Rebuilds delphi_web_python image. You shouldn't need to do this
#            often; only if you are installing a new environment, or have
#            made changes to delphi-epidata/dev/docker/python/Dockerfile.
#
#   all:     Runs the commands 'web' 'db' and 'python'.
#
#   test:    Runs test and integrations in delphi-epidata. If test 
#            optional arg is provided, then only the tests in that subdir
#            are run.
#
#   clean:   Cleans up dangling Docker images.
#
#
# Optional arguments:
#   pdb=1         Drops you into debug mode upon test failure, if running tests.
#   test=         Only runs tests in the directories provided here, e.g.
#                 repos/delphi/delphi-epidata/tests/acquisition/covidcast


# Set optional argument defaults
ifdef pdb
	override pdb=--pdb
else
	pdb=
endif

ifndef test
	test=repos/delphi/delphi-epidata/tests repos/delphi/delphi-epidata/integrations
endif

SHELL:=/bin/sh

# Get the Makefile's absolute path: https://stackoverflow.com/a/324782/4784655
# (if called from a symlink, the path is the location of the symlink)
CWD:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
NOW:=$(shell date "+%Y-%m-%d")
LOG_WEB:=delphi_web_epidata_$(NOW).log
LOG_DB:=delphi_database_epidata_$(NOW).log
WEB_CONTAINER_ID:=$(shell docker ps -q --filter 'name=delphi_web_epidata')
DATABASE_CONTAINER_ID:=$(shell docker ps -q --filter 'name=delphi_database_epidata')


.PHONY=web
web:
	@# Stop container if running
	@if [ $(WEB_CONTAINER_ID) ]; then\
		docker stop $(WEB_CONTAINER_ID);\
	fi

	@# Setup virtual network if it doesn't exist
	@docker network ls | grep delphi-net || docker network create --driver bridge delphi-net

	@# Build the web_epidata image
	@cd repos/delphi/delphi-epidata;\
		docker build -t delphi_web_epidata -f ./devops/Dockerfile .;\
		cd ../../../

	@# Run the web server
	@docker run --rm -p 127.0.0.1:10080:80 \
		--env "SQLALCHEMY_DATABASE_URI=mysql+mysqldb://user:pass@delphi_database_epidata:3306/epidata" \
		--env "FLASK_SECRET=abc" --env "FLASK_PREFIX=/epidata" \
		--network delphi-net --name delphi_web_epidata \
		delphi_web_epidata >$(LOG_WEB) 2>&1 &

.PHONY=db
db:
	@# Stop container if running
	@if [ $(DATABASE_CONTAINER_ID) ]; then\
		docker stop $(DATABASE_CONTAINER_ID);\
	fi

	@# Only build prereqs if we need them
	@docker images delphi_database | grep delphi || \
		docker build -t delphi_database -f repos/delphi/operations/dev/docker/database/Dockerfile .

	@# Build the database_epidata image
	@docker build -t delphi_database_epidata \
		-f repos/delphi/delphi-epidata/dev/docker/database/epidata/Dockerfile .

	@# Run the database
	@docker run --rm -p 127.0.0.1:13306:3306 \
		--network delphi-net --name delphi_database_epidata \
                --cap-add=sys_nice \
		delphi_database_epidata >$(LOG_DB) 2>&1 &

	@# Block until DB is ready
	@while true; do \
		sed -n '/mysqld: ready for connections/p' $(LOG_DB) | grep "ready for connections" && break; \
		tail -1 $(LOG_DB); \
		sleep 1; \
	done

.PHONY=py
py:
	@# Build the python image
	@docker build -t delphi_python \
		-f repos/delphi/operations/dev/docker/python/Dockerfile .

	@docker build -t delphi_web_python \
		-f repos/delphi/delphi-epidata/dev/docker/python/Dockerfile .

.PHONY=all
all: web db py

.PHONY=test
test:
	@docker run -i --rm --network delphi-net \
		--mount type=bind,source=$(CWD)repos/delphi/delphi-epidata,target=/usr/src/app/repos/delphi/delphi-epidata,readonly \
		--mount type=bind,source=$(CWD)repos/delphi/delphi-epidata/src,target=/usr/src/app/delphi/epidata,readonly \
		--env "SQLALCHEMY_DATABASE_URI=mysql+mysqldb://user:pass@delphi_database_epidata:3306/epidata" \
		--env "FLASK_SECRET=abc" \
		delphi_web_python python -m pytest --import-mode importlib $(pdb) $(test) | tee test_output_$(NOW).log

.PHONY=clean
clean:
	@docker images -f "dangling=true" -q | xargs docker rmi >/dev/null 2>&1
