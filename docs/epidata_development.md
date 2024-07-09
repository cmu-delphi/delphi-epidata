---
title: Epidata API Development Guide
nav_order: 4
---

# Epidata API Development Guide

## Development Quickstart

Requires: Docker, possibly sudo access (depending on your Docker installation and OS).

In the directory where you want to work run the following:

```sh
# Make folder structure, download dependent repos, and symlink Makefile
$ curl "https://raw.githubusercontent.com/cmu-delphi/delphi-epidata/dev/dev/local/install.sh" | bash
```

You should now have the following directory structure:

```sh
├── driver
│   ├── .dockerignore -> repos/delphi/delphi-epidata/dev/local/.dockerignore
│   ├── Makefile -> repos/delphi/delphi-epidata/dev/local/Makefile
│   ├── repos
│   │   └── delphi
│   │       ├── delphi-epidata
│   │       ├── flu-contest
│   │       ├── github-deploy-repo
│   │       ├── nowcast
│   │       ├── operations
│   │       └── utils
```

and you should now be in the `driver` directory.
You can now execute make commands

```sh
# Create all docker containers: db, web, and python
$ [sudo] make all

# Run tests
$ [sudo] make test

# To drop into debugger on error
$ [sudo] make test pdb=1

# To test only a subset of tests
$ [sudo] make test test=repos/delphi/delphi-epidata/integrations/acquisition
```

You can read the commands executed by the Makefile [here](../dev/local/Makefile).

## Rapid Iteration and Bind Mounts

To reduce friction, we
[bind-mount](https://docs.docker.com/storage/bind-mounts/) local source files to
the containers, which replaces the corresponding files from the image and allows
your code changes to be reflected immediately, without needing to rebuild. This
approach comes with some drawbacks you should be aware of:

- the container will be able read and write to your local filesystem (which may
  be a security concern, especially if you are running the containers as root)
- there may be also be strange behaviors with file permissions, especially if
  you are running the containers as root
- bind mounts do not interact well with `selinux` on some systems, leading to
  various access denials at runtime. As a workaround, you may have to use the
  [dangerous "Z"
  flag](https://docs.docker.com/storage/bind-mounts/#configure-the-selinux-label)
  or temporarily disable selinux -- neither of which is advised.
- for more see the [Epicast development
  guide](https://github.com/cmu-delphi/www-epicast/blob/main/docs/epicast_development.md#develop).

## Manual Installation

We recommend using the quickstart above. If you need to customize the install,
please inspect the installation script `install.sh` above and look in the
`Makefile` to find the Docker commands.

## Manual Tests

You can test your changes manually by:

1. inserting test data into the relevant table(s)
2. querying the API using your client of choice (`curl` is handy for sanity
   checks)

What follows is a worked demonstration based on the `fluview` endpoint. Before
starting, make sure that you have the `delphi_database_epidata`,
`delphi_web_epidata`, and `delphi_redis` containers running (with `docker ps`);
if you don't, see the Makefile instructions above.

First, let's insert some fake data into the `fluview` table:

```bash
# If you have the mysql client installed locally:
echo 'insert into fluview values \
  (0, "2020-04-07", 202021, 202020, "nat", 1, 2, 3, 4, 3.14159, 1.41421, \
  10, 11, 12, 13, 14, 15)' | \
  mysql --user=user --password=pass \
  --port 13306 --host 127.0.0.1 epidata

# If you do not have mysql locally, you can use a Docker image that has it:
echo 'insert into fluview values \
    (0, "2020-04-07", 202021, 202020, "nat", 1, 2, 3, 4, 3.14159, 1.41421, \
    10, 11, 12, 13, 14, 15)' | \
    docker run --rm -i --network delphi-net percona:ps-8 \
    mysql --user=user --password=pass \
    --port 3306 --host delphi_database_epidata epidata
```

(The host and port given in the first command are "external" values, which are
locally visible. In the second command, we use the Docker "internal" values,
which are visible to containers on the same virtual network. Port 3306 on the
outside of the container is mapped to 13360, which can be seen in the Makefile.)

For the inserts above, absence of command-line output is a sign of success. On
the other hand, output after the insertion likely indicates failure (like, for
example, attempting to insert a duplicate unique key).

Next, you can query the API directly (and parse with Python's JSON tool):

```bash
curl -s \
  'http://localhost:10080/epidata/api.php?source=fluview&epiweeks=202020&regions=nat' | \
python3 -m json.tool
```

You should expect to see the following response from the server, which is the
data you inserted earlier:

```json
{
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
  "result": 1,
  "message": "success"
}
```

Alternatively, you could query the API using one of the available client
libraries. However, this would require you to modify the base URL within the
client's code, and there is some additional amount of boilerplate involved in
calling the client and displaying the result. For these reasons, client
libraries are better candidates for automated integration tests (and unit tests,
in the case of the python client) than one-off manual tests.

Our API integration tests use this same Docker image and network setup, but
truncate the database tables before running tests, so any manual changes to the
database will be lost after running integration tests.

## Instrumentation with Sentry

Delphi uses [Sentry](https://sentry.io/welcome/) in production for debugging, APM, and other observability purposes. You can instrument your local environment if you want to take advantage of Sentry's features during the development process. In most cases this option is available to internal Delphi team members only.

The bare minimum to set up instrumentation is to supply the DSN for the [epidata-api](https://cmu-delphi.sentry.io/projects/epidata-api/?project=4506123377442816) Sentry project to the application environment.

- You can get the DSN from the Sentry [project's keys config](https://cmu-delphi.sentry.io/settings/projects/epidata-api/keys/), or by asking someone in the prodsys, DevOps, or sysadmin space.
- Once you have the DSN, add it to your local `.env` file and rebuild your containers to start sending telemetry to Sentry.

Additional internal documentation for Sentry can be found [here](https://bookstack.delphi.cmu.edu/books/systems-handbook/page/sentry).
