# Docker control panel for delphi-epidata development.
#
# Usage: make <command> [pdb=1] [test=<test-subdir>]
#
# Assumes you have installed your environment using
# delphi-epidata/dev/local/install.sh.
#
# Checks for the delphi-net bridge and creates if it doesn't exist.
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
#   sql=          Overrides the default SQL connection string.


# Set optional argument defaults
ifdef pdb
	override pdb=--pdb
else
	pdb=
endif

ifndef test
	test=repos/delphi/delphi-epidata/tests repos/delphi/delphi-epidata/integrations
endif

ifdef sql
	sqlalchemy_uri:=$(sql)
else
	sqlalchemy_uri:=mysql+mysqldb://user:pass@delphi_database_epidata:3306/epidata
endif

SHELL:=/bin/sh

# Get the Makefile's absolute path: https://stackoverflow.com/a/324782/4784655
# (if called from a symlink, the path is the location of the symlink)
CWD:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
NOW:=$(shell date "+%Y-%m-%d")
LOG_WEB:=delphi_web_epidata_$(NOW).log
LOG_DB:=delphi_database_epidata_$(NOW).log
LOG_REDIS:=delphi_redis_instance_$(NOW).log

M1=
ifeq ($(shell uname -smp), Darwin arm64 arm)
$(info M1 system detected, changing docker platform to linux/amd64.)
	override M1 =--platform linux/amd64
endif

.PHONY=db
db:
	@docker compose up delphi_database_epidata $(M1) --detach
	@docker logs -f delphi_database_epidata >$(LOG_DB) 2>&1 &

.PHONY=web
web:
	@SQLALCHEMY_DATABASE_URI=$(sqlalchemy_uri) docker compose up delphi_web_epidata $(M1) --detach
	@docker logs -f delphi_web_epidata >$(LOG_WEB) 2>&1 &

.PHONY=redis
redis:
	@docker compose up delphi_redis $(M1) --detach
	@docker logs -f delphi_redis >$(LOG_REDIS) 2>&1 &

.PHONY=test
test:
	@SQLALCHEMY_DATABASE_URI=$(sqlalchemy_uri) docker compose run delphi_web_python $(M1) \
		python -m pytest --import-mode importlib $(pdb) $(test) | tee test_output_$(NOW).log

.PHONY=r-test
r-test:
	@SQLALCHEMY_DATABASE_URI=$(sqlalchemy_uri) docker compose run delphi_web_python $(M1) \
		Rscript repos/delphi/delphi-epidata/integrations/client/test_delphi_epidata.R | tee r-test_output_$(NOW).log

.PHONY=bash
bash:
	@SQLALCHEMY_DATABASE_URI=$(sqlalchemy_uri) docker compose run delphi_web_python $(M1) bash

.PHONY=sql
sql:
	@docker run --rm -it --network delphi-net --cap-add=sys_nice \
		percona mysql --user=user --password=pass --port 3306 --host delphi_database_epidata epidata

.PHONY=down
down:
	@docker compose down

.PHONY=down-force-rebuild
down-force-rebuild:
	@docker compose down --rmi all --volumes
	@docker compose up --build --force-recreate --detach

.PHONY=clean
clean:
	@docker images -f "dangling=true" -q | xargs docker rmi >/dev/null 2>&1
