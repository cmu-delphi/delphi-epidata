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
#   rate_limit=   Overrides the default rate limit for API requests.


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

ifdef rate_limit
# Notation found here: https://flask-limiter.readthedocs.io/en/stable/#rate-limit-string-notation
	rate_limit_settings:=--env "RATE_LIMIT=$(rate_limit)"
else
# Default behavior is to set the rate limit to "5/hour" for API key tests via this environment variable
	rate_limit_settings:=--env "TESTING_MODE=True"
endif

SHELL:=/bin/sh

# Get the Makefile's absolute path: https://stackoverflow.com/a/324782/4784655
# (if called from a symlink, the path is the location of the symlink)
CWD:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
NOW:=$(shell date "+%Y-%m-%d")
LOG_WEB:=delphi_web_epidata_$(NOW).log
LOG_DB:=delphi_database_epidata_$(NOW).log
LOG_REDIS:=delphi_redis_instance_$(NOW).log
WEB_CONTAINER_ID:=$(shell docker ps -q --filter 'name=delphi_web_epidata')
DATABASE_CONTAINER_ID:=$(shell docker ps -q --filter 'name=delphi_database_epidata')
REDIS_CONTAINER_ID:=$(shell docker ps -q --filter 'name=delphi_redis')

M1=
ifeq ($(shell uname -smp), Darwin arm64 arm)
$(info M1 system detected, changing docker platform to linux/amd64.)
	override M1 =--platform linux/amd64
endif

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
		docker build -t delphi_web_epidata\
			$(M1) \
			-f ./devops/Dockerfile .;\
		cd -

	@# Run the web server
	@# MODULE_NAME specifies the location of the `app` variable, the actual WSGI application object to run.
	@# see https://github.com/tiangolo/meinheld-gunicorn-docker#module_name
	@# To receive Slack notification, please add SLACK_WEBHOOK_URL with proper webhook link to the list of env variables.
	@docker run --rm -p 127.0.0.1:10080:80 \
		$(M1) \
		--env "MODULE_NAME=delphi.epidata.server.main" \
		--env "SQLALCHEMY_DATABASE_URI=$(sqlalchemy_uri)" \
		--env "FLASK_SECRET=abc" --env "FLASK_PREFIX=/epidata" --env "LOG_DEBUG" \
		--env "REDIS_HOST=delphi_redis" \
		--env "REDIS_PASSWORD=1234" \
		--env "API_KEY_ADMIN_PASSWORD=test_admin_password" \
		--env "API_KEY_REGISTER_WEBHOOK_TOKEN=abc" \
		--env "RECAPTCHA_SITE_KEY=6Le3wcMnAAAAAL0phFNTaWIHWDDb78I8aSzA34f2" \
		--env "RECAPTCHA_SECRET_KEY=6Le3wcMnAAAAANlmnp_oApGewLwOmiNFjxlTe2Zo" \
		--network delphi-net --name delphi_web_epidata \
		delphi_web_epidata >$(LOG_WEB) 2>&1 &

.PHONY=db
db:
	@# Stop container if running
	@if [ $(DATABASE_CONTAINER_ID) ]; then\
		docker stop $(DATABASE_CONTAINER_ID);\
	fi

	@# Setup virtual network if it doesn't exist
	@docker network ls | grep delphi-net || docker network create --driver bridge delphi-net

	@# Build the database_epidata image
	@docker build -t delphi_database_epidata \
		$(M1) \
		-f repos/delphi/delphi-epidata/dev/docker/database/epidata/Dockerfile .

	@# Run the database
	@docker run --rm -p 127.0.0.1:13306:3306 \
		$(M1) \
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
	@docker build -t delphi_web_python \
		$(M1) \
		-f repos/delphi/delphi-epidata/dev/docker/python/Dockerfile .

.PHONY=redis
redis:
	@# Stop container if running
	@if [ $(REDIS_CONTAINER_ID) ]; then\
		docker stop $(REDIS_CONTAINER_ID);\
	fi

	@docker build -t delphi_redis \
		$(M1) \
		-f repos/delphi/delphi-epidata/dev/docker/redis/Dockerfile .

	@docker run --rm -d -p 127.0.0.1:6379:6379 \
		$(M1) \
		--network delphi-net \
		--env "REDIS_PASSWORD=1234" \
		--name delphi_redis delphi_redis >$(LOG_REDIS) 2>&1 &

.PHONY=all
all: db web py redis

.PHONY=test
test:
	@docker run -i --rm --network delphi-net \
		$(M1) \
		--mount type=bind,source=$(CWD)repos/delphi/delphi-epidata,target=/usr/src/app/repos/delphi/delphi-epidata,readonly \
		--mount type=bind,source=$(CWD)repos/delphi/delphi-epidata/src,target=/usr/src/app/delphi/epidata,readonly \
		--env "SQLALCHEMY_DATABASE_URI=$(sqlalchemy_uri)" \
		--env "FLASK_SECRET=abc" \
		delphi_web_python python -m pytest --import-mode importlib $(pdb) $(test) | tee test_output_$(NOW).log

.PHONY=r-test
r-test:
	@docker run -i --rm --network delphi-net \
		$(M1) \
		--mount type=bind,source=$(CWD)repos/delphi/delphi-epidata,target=/usr/src/app/repos/delphi/delphi-epidata,readonly \
		--mount type=bind,source=$(CWD)repos/delphi/delphi-epidata/src,target=/usr/src/app/delphi/epidata,readonly \
		--env "SQLALCHEMY_DATABASE_URI=$(sqlalchemy_uri)" \
		--env "FLASK_SECRET=abc" \
		delphi_web_python Rscript repos/delphi/delphi-epidata/integrations/client/test_delphi_epidata.R | tee r-test_output_$(NOW).log


.PHONY=bash
bash:
	@docker run -it --rm --network delphi-net \
		$(M1) \
		--mount type=bind,source=$(CWD)repos/delphi/delphi-epidata,target=/usr/src/app/repos/delphi/delphi-epidata,readonly \
		--mount type=bind,source=$(CWD)repos/delphi/delphi-epidata/src,target=/usr/src/app/delphi/epidata,readonly \
		--env "SQLALCHEMY_DATABASE_URI=$(sqlalchemy_uri)" \
		--env "FLASK_SECRET=abc" \
		delphi_web_python bash

.PHONY=sql
sql:
	@docker run --rm -it --network delphi-net --cap-add=sys_nice \
		percona mysql --user=user --password=pass --port 3306 --host delphi_database_epidata epidata

.PHONY=clean
clean:
	@docker images -f "dangling=true" -q | xargs docker rmi >/dev/null 2>&1
