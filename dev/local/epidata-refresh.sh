#!/bin/bash

if [ -z "$1" ]; then
    echo "USAGE:"
    echo "$0 [database] [web] [python] [testdir|test.py ...]"
    echo "Docker control panel for delphi-epidata development"
    echo
    echo "  Assumes you have installed your environment using"
    echo "  delphi-epidata/dev/local/install.sh."
    echo
    echo "  Cleans up dangling Docker images before starting."
    echo
    echo "  Checks for the delphi-net bridge, and creates it if it doesn't exist."
    echo
    echo "  Creates all prereq images (delphi_database, delphi_python) only if they don't"
    echo "  exist. If you need to rebuild a prereq, you're probably doing something"
    echo "  complicated, and can figure out the rebuild command on your own."
    echo
    echo "  database: Stops currently-running delphi_database_epidata instances, if any."
    echo "            Rebuilds delphi_database_epidata image."
    echo "            Runs image in the background and pipes stdout to a log file."
    echo "            Blocks until database is ready to receive connections."
    echo
    echo "  web:      Stops currently-running delphi_web_epidata instances, if any."
    echo "            Rebuilds delphi_web_epidata image."
    echo "            Runs image in the background and pipes stdout to a log file."
    echo
    echo "  python:   Rebuilds delphi_web_python image. You shouldn't need to do this"
    echo "            often; only if you are installing a new environment, or have"
    echo "            made changes to delphi-epidata/dev/docker/python/Dockerfile."
    echo
    echo "  Loops through the remaining arguments and runs them as pytest within the"
    echo "  delphi_web_python image. This uses bindmounts into the local filesystem,"
    echo "  so any changes you have made to src/acquisition/, tests/, or integrations/"
    echo "  will automatically take effect without having to rebuild delphi_web_python."
    echo "  Saves all test output to output.txt for review, in case it excees your"
    echo "  terminal buffer. Halts on first failure and lists failed tests."
    echo
    echo "  Always run this from the `driver` directory. Never put anything other than"
    echo "  code in the `driver` directory, since everything under the `driver` directory"
    echo "  will get folded into the Docker images created. If it takes more than 1m to"
    echo "  build Docker images, you have probably accidentally stored other data in the"
    echo "  `driver` directory tree."
    echo
    echo "  Depending on your operating system, you may need to be root or use sudo."
    exit 0
fi

docker images -f "dangling=true" -q | xargs docker rmi >/dev/null 2>&1
docker network ls | grep delphi-net || docker network create --driver bridge delphi-net

LOGS=../driver-logs
NOW=`date "+%Y-%m-%d`

if [ "$1" == "database" ]; then
    shift
    LOGFILE=${LOGS}/delphi_database_epidata/${NOW}.log
    docker ps | grep delphi_database_epidata && docker stop delphi_database_epidata
    # only build prereqs if we need them
    docker images delphi_database | grep delphi || \
        docker build -t delphi_database -f repos/delphi/operations/dev/docker/database/Dockerfile . || exit 1
    docker build -t delphi_database_epidata -f repos/delphi/delphi-epidata/dev/docker/database/epidata/Dockerfile . || exit 1
    docker run --rm -p 127.0.0.1:13306:3306 --network delphi-net --name delphi_database_epidata delphi_database_epidata \
           >${LOGFILE} 2>&1 &
    while true; do
        sed -n '/Temporary server stopped/,/mysqld: ready for connections/p' ${LOGFILE} | grep "ready for connections" && break
        tail -1 ${LOGFILE}
        sleep 1
    done
    grep ERROR ${LOGFILE} && exit 1
fi

if [ "$1" == "web" ]; then
    shift
    docker ps | grep delphi_web_epidata && docker stop delphi_web_epidata
    cd repos/delphi/delphi-epidata && docker build -t delphi_web_epidata   -f ./devops/Dockerfile . && cd - || exit 1
    docker run --rm -p 127.0.0.1:10080:80 \
           --env "SQLALCHEMY_DATABASE_URI=mysql+mysqldb://user:pass@delphi_database_epidata:3306/epidata" \
           --env "FLASK_SECRET=abc" --env "FLASK_PREFIX=/epidata" \
           --network delphi-net --name delphi_web_epidata delphi_web_epidata >>${LOGS}/delphi_web_epidata/${NOW}.log 2>&1 &
fi
if [ "$1" == "python" ]; then
    shift
    # only build prereqs if we need them
    docker images delphi_python | grep delphi || \
        docker build -t delphi_python -f repos/delphi/operations/dev/docker/python/Dockerfile . || exit 1
    docker build -t delphi_web_python \
           -f repos/delphi/delphi-epidata/dev/docker/python/Dockerfile . || exit 1
fi
rm -f output.txt
for t in $@; do
    set -x
    docker run --rm --network delphi-net \
           --mount type=bind,source="$(pwd)"/repos/delphi/delphi-epidata,target=/usr/src/app/repos/delphi/delphi-epidata,readonly \
           --mount type=bind,source="$(pwd)"/repos/delphi/delphi-epidata/src,target=/usr/src/app/delphi/epidata,readonly \
           --env "SQLALCHEMY_DATABASE_URI=mysql+mysqldb://user:pass@delphi_database_epidata:3306/epidata" --env "FLASK_SECRET=abc" \
           delphi_web_python \
           python -m pytest --import-mode importlib $t | tee -a output.txt
    set +x
    [[ $? = "0" ]] || exit 1
    grep -e "FAIL" -e "tests did not pass" output.txt && exit 1
done
