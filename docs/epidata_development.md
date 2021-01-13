---
title: Epidata API Development Guide
nav_order: 4
---

# Epidata API Development Guide

**Prerequisite:** this guide assumes that you have read the
[frontend development guide](https://github.com/cmu-delphi/operations/blob/main/docs/frontend_development.md).

This guide describes how to write and test code for the Epidata API. For
preliminary steps,
[install docker and create a virtual network](https://github.com/cmu-delphi/operations/blob/main/docs/frontend_development.md#setup).

After reading this guide, you may want to visit
[the `fluview_meta` tutorial](new_endpoint_tutorial.md) for an example of how
to add a new endpoint to the API.

# setup

For working on the Epidata API, you'll need the following two Delphi
repositories:

- [operations](https://github.com/cmu-delphi/operations)
- [delphi-epidata](https://github.com/cmu-delphi/delphi-epidata)

You likely won't need to modify the `operations` repo, so cloning directly from
`cmu-delphi` is usually sufficient. However, since you _are_ going to be
modifying `delphi-epidata` sources, you'll first need to fork the repository
and then clone your personal fork. For more details, see the Delphi-specific
[discussion on forking and branching](https://github.com/cmu-delphi/operations/blob/main/docs/backend_development.md#everyone).

Here's an example of how to set up your local workspace. Note that you will need
to use your own GitHub username where indicated.

```bash
# collect everything in a directory called "repos"
mkdir repos && cd repos

# delphi python (sub)packages
mkdir delphi && cd delphi
git clone https://github.com/cmu-delphi/operations
git clone https://github.com/Your-GitHub-Username/delphi-epidata
cd ..

# go back up to the workspace root
cd ..
```

Your workspace should now look like this:

```bash
tree -L 3 .
```

```
.
└── repos
    └── delphi
        ├── delphi-epidata
        └── operations
```

# build images

We now need images for the Epidata API web server and the `epidata` database.
These are both based on core Delphi images as defined in the
[`operations` repo](https://github.com/cmu-delphi/operations) which you cloned
above. The base images are built first, followed by the derived
`epidata`-specific images.

- The [`delphi_web_epidata` image](../dev/docker/web/epidata/README.md) adds
  the Epidata API to the `delphi_web` image.
- The
  [`delphi_database_epidata` image](../dev/docker/database/epidata/README.md)
  adds the `epi` user account, `epidata` database, and relevant tables
  (initially empty) to the `delphi_database` image.

From the root of your workspace, all of the images can be built as follows:

```bash
docker build -t delphi_web \
  -f repos/delphi/operations/dev/docker/web/Dockerfile .

docker build -t delphi_web_epidata \
  -f repos/delphi/delphi-epidata/dev/docker/web/epidata/Dockerfile .

docker build -t delphi_database \
  -f repos/delphi/operations/dev/docker/database/Dockerfile .

docker build -t delphi_database_epidata \
  -f repos/delphi/delphi-epidata/dev/docker/database/epidata/Dockerfile .
```

# test

At this point, you're ready to bring the stack online.

First, make sure you have the docker network set up so that the containers can
communicate:

```
docker network create --driver bridge delphi-net
```

Next, start containers for the epidata-specific web and database images. As an aside, the
output from these commands (especially the webserver) can be very helpful for
debugging. For example:

```bash
# launch the database
docker run --rm -p 127.0.0.1:13306:3306 \
  --network delphi-net --name delphi_database_epidata \
  delphi_database_epidata

# launch the web server
docker run --rm -p 127.0.0.1:10080:80 \
  --network delphi-net --name delphi_web_epidata \
  delphi_web_epidata
```

## unit tests

Unit tests are self-contained and do not depend on external services like
databases or web servers. You can run unit tests at any time according to the
instructions in the
[backend development guide](https://github.com/cmu-delphi/operations/blob/main/docs/backend_development.md).

First, [build the `delphi_python` image](https://github.com/cmu-delphi/operations/blob/main/docs/backend_development.md#creating-an-image).
Your test sources will live in, and be executed from within, this image.

Then run the tests in a container based on that image:

```bash
docker run --rm delphi_python \
  python3 -m undefx.py3tester.py3tester --color \
    repos/delphi/delphi-epidata/tests
```

The final line of output should be similar to the following:

```
All 48 tests passed! 68% (490/711) coverage.
```

You can also run tests using pytest like this:
```
docker run --rm delphi_python pytest repos/delphi/delphi-epidata/tests/
```
and with pdb enabled like this:
```
docker run -it --rm delphi_python pytest repos/delphi/delphi-epidata/tests/ --pdb
```

## manual tests

You can test your changes manually by:

1. inserting test data into the relevant table(s)
2. querying the API using your client of choice (`curl` is handy for sanity
  checks)

Here's a full example based on the `fluview` endpoint:

1. Populate the database (particularly the `fluview` table) with some fake
  data. For example:

  ```bash
  echo 'insert into fluview values \
    (0, "2020-04-07", 202021, 202020, "nat", 1, 2, 3, 4, 3.14159, 1.41421, \
    10, 11, 12, 13, 14, 15)' | \
  mysql --user=user --password=pass \
    --port 13306 --host 127.0.0.1 epidata
  ```

  Note that the host and port given above are "external" values, which are
  locally visible. You'll need the `mysql` client installed locally to run the
  above command.

  In case you don't have the `mysql` client installed on your machine and
  don't want to install it, you can simply use the binary that's bundled with
  the `mariadb` docker image, which you should already have from building the
  `delphi_database` image. In that case, use the "internal" values, which are
  visible to containers on the same virtual network. For example:

  ```bash
  echo 'insert into fluview values \
    (0, "2020-04-07", 202021, 202020, "nat", 1, 2, 3, 4, 3.14159, 1.41421, \
    10, 11, 12, 13, 14, 15)' | \
  docker run --rm -i --network delphi-net mariadb \
  mysql --user=user --password=pass \
    --port 3306 --host delphi_database_epidata epidata
  ```

  Note that for these inserts, absence of command-line output is a sign of
  success. On the other hand, output after the insertion likely indicates
  failure (like, for example, attempting to insert a duplicate unique key).

2. Query the API directly:

  ```bash
  curl -s \
    'http://localhost:10080/epidata/api.php?source=fluview&epiweeks=202020&regions=nat' | \
  python3 -m json.tool
  ```

  The pipe to python's built-in JSON formatter is optional, but handy. You
  should expect to see the following response from the server:

  ```json
  {
      "result": 1,
      "epidata": [
          {
              "release_date": "2020-04-07",
              "region": "nat",
              "issue": 202021,
              "epiweek": 202020,
              "lag": 1,
              "num_ili": 2,
              "num_patients": 3,
              "num_providers": 4,
              "num_age_0": 10,
              "num_age_1": 11,
              "num_age_2": 12,
              "num_age_3": 13,
              "num_age_4": 14,
              "num_age_5": 15,
              "wili": 3.14159,
              "ili": 1.41421
          }
      ],
      "message": "success"
  }
  ```

  Alternatively, you could query the API using one of the available client
  libraries. However, this would require you to modify the base URL within the
  client's code, and there is some additional amount of boilerplate involved in
  calling the client and displaying the result. For these reasons, client
  libraries are better candidates for automated integration tests (and unit
  tests, in the case of the python client) than one-off manual tests.

## integration tests

Writing an integration test is outside of the scope of this document. However,
a number of existing integration tests exist and can be used as a good starting
point for additional tests. For example, see the tests for the
[`fluview` API endpoint](../integrations/server/test_fluview.py) and the
[`covidcast` ingestion pipeline](../integrations/acquisition/covidcast).

To run the existing tests and any new tests that you write, you must
follow the
[backend development guide](https://github.com/cmu-delphi/operations/blob/main/docs/backend_development.md)
_within the same workspace_, so that the `delphi_python` image is created with
any changes you have made (e.g., adding new integration tests). That image will
contain the test driver and the source code of your integration tests. Then,
run the tests inside a container based on that image. Note that the container
of tests will need to be attached to the virtual network `delphi-net`
to see and communicate with the web and database servers.

More concretely, you can run Epidata API integration tests like this:

1. Build server images as described in the [building section](#build-images)
  above.

2. Launch the server containers as described in the [test section](#test)
  above.

3. Build the `delphi_python` image per the
  [backend development guide](https://github.com/cmu-delphi/operations/blob/main/docs/backend_development.md#creating-an-image).
  Your test sources will live in, and be executed from within, this image.

4. Run integration tests in a container based on the `delphi_python` image:

  ```bash
  docker run --rm --network delphi-net delphi_python \
  python3 -m undefx.py3tester.py3tester --color \
    repos/delphi/delphi-epidata/integrations
  ```

  You should see output similar to the following (edited for brevity):

  ```
  test_privacy_filtering (repos.delphi.delphi-epidata.integrations.test_covid_survey_hrr_daily.CovidSurveyHrrDailyTests
  Don't return rows with too small of a denominator. ... ok
  test_round_trip (repos.delphi.delphi-epidata.integrations.test_covid_survey_hrr_daily.CovidSurveyHrrDailyTests)
  Make a simple round-trip with some sample data. ... ok

  test_round_trip (repos.delphi.delphi-epidata.integrations.test_fluview.FluviewTests)
  Make a simple round-trip with some sample data. ... ok

  ✔ All 3 tests passed! [coverage unavailable]
  ```

  You can also run tests using pytest like this:
  ```
  docker run --network delphi-net --rm delphi_python pytest repos/delphi/delphi-epidata/integrations/
  ```
  and with pdb enabled like this:
  ```
  docker run --network delphi-net -it --rm delphi_python pytest repos/delphi/delphi-epidata/integrations/ --pdb
  ```

5. Bring down the servers, for example with the `docker stop` command.

# rapid iteration

The workflow described above requires containers to be stopped, rebuilt, and
restarted each time code (including tests) is changed, which can be tedious. To
reduce friction, it's possible to
[bind-mount](https://docs.docker.com/storage/bind-mounts/) your local source
files into a container, which replaces the corresponding files from the image.
This allows your code changes to be reflected immediately, without needing to
rebuild containers.

There are some drawbacks, however, as discussed in the
[Epicast development guide](https://github.com/cmu-delphi/www-epicast/blob/main/docs/epicast_development.md#develop).
For example:

- Code running in the container can read (and possibly also write) your local filesystem.
- The command-line specification of bind-mounts is quite tedious.
- Bind mounts do not interact well with `selinux` on some systems, leading to
various access denials at runtime. As a workaround, you may have to use the
[dangerous "Z" flag](https://docs.docker.com/storage/bind-mounts/#configure-the-selinux-label)
or temporarily disable `selinux` -- neither of which is advised.

## bind-mounting

### non-server code

Python sources (e.g. data acquisition, API clients, and tests), can be
bind-mounted into a `delphi_python` container as follows:

```bash
docker run --rm --network delphi-net \
  --mount type=bind,source="$(pwd)"/repos/delphi/delphi-epidata,target=/usr/src/app/repos/delphi/delphi-epidata,readonly \
  --mount type=bind,source="$(pwd)"/repos/delphi/delphi-epidata/src,target=/usr/src/app/delphi/epidata,readonly \
  delphi_python \
python3 -m undefx.py3tester.py3tester --color \
  repos/delphi/delphi-epidata/integrations
```

The command above maps two local directories into the container:

- `/repos/delphi/delphi-epidata`: The entire repo, notably including unit and
  integration test sources.
- `/repos/delphi/delphi-epidata/src`: Just the source code, which forms the
  container's `delphi.epidata` python package.

### server code

Local web sources (e.g. PHP files) can be bind-mounted into a
`delphi_web_epidata` container as follows:

```bash
docker run --rm -p 127.0.0.1:10080:80 \
  --mount type=bind,source="$(pwd)"/repos/delphi/delphi-epidata/src/server/api.php,target=/var/www/html/epidata/api.php,readonly \
  --mount type=bind,source="$(pwd)"/repos/delphi/delphi-epidata/src/server/api_helpers.php,target=/var/www/html/epidata/api_helpers.php,readonly \
  --network delphi-net --name delphi_web_epidata \
  delphi_web_epidata
```

The command above mounts two specific files into the image. It may be tempting
to bind mount the `src/server` directory rather than specific files, however
that is currently problematic for a couple of reasons:

1. `server/.htaccess` [from the local repository](../src/server/.htaccess) uses
  the `Header` directive. However, the webserver in the container doesn't have
  the corresponding module enabled. This causes the server to deny access to
  the API.
2. `server/database_config.php`
  [in the image](../dev/docker/web/epidata/assets/database_config.php) contains
  database credentials for use in conjunction with the
  `delphi_database_epidata` container during development. However, the same
  file from [the local repository](../src/server/database_config.php) only
  contains placeholder values. This prevents communication with the database.

There is currently no benefit to bind-mounting sources into the database
container because schema changes require restarting the container anyway.
