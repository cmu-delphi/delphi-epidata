# Status

[![Deploy Status](https://delphi.cmu.edu/~automation/public/github_deploy_repo/badge.php?repo=cmu-delphi/delphi-epidata)](#)

# About

This is the home of [Delphi](https://delphi.cmu.edu/)'s epidemiological data
API. See our [API documentation](https://cmu-delphi.github.io/delphi-epidata/)
for details on the available data sets, APIs, and clients.

# Development Quickstart

## Setup

Requires: Docker, possibly sudo access (depending on your Docker installation and OS).

In the directory where you want to work run the following:

```sh
# Make folder structure, download dependent repos, and symlink Makefile
$ curl "https://raw.githubusercontent.com/cmu-delphi/delphi-epidata/dev/dev/local/install.sh" | bash && cd driver
```

You should now have the following directory structure:

```sh
├── driver
│   ├── .dockerignore -> repos/delphi/delphi-epidata/dev/local/.dockerignore
│   ├── Makefile -> repos/delphi/delphi-epidata/dev/local/Makefile
│   ├── repos
│   │   ├── pyproject.toml -> delphi/delphi-epidata/dev/local/pyproject.toml
│   │   ├── setup.cfg -> delphi/delphi-epidata/dev/local/setup.cfg
│   │   └── delphi
│   │       ├── delphi-epidata
│   │       ├── flu-contest
│   │       ├── github-deploy-repo
│   │       ├── nowcast
│   │       ├── operations
│   │       └── utils
```

and you should be in the `driver` directory.
You can now execute `make` commands (but only from the `driver` directory).

```sh
# Create all docker containers: db, web, redis, and python
$ [sudo] make all

# Run python tests
$ [sudo] make test

# To drop into debugger on error
# Warning: this can hang, so as an alternative import pdb and add a `pdb.set_trace()` in the failing test.
$ [sudo] make test pdb=1

# To test only a subset of tests, specify the path to the directory or file of interest.
$ [sudo] make test test=repos/delphi/delphi-epidata/integrations/acquisition
$ [sudo] make test test=repos/delphi/delphi-epidata/integrations/acquisition/covid_hosp/facility/test_scenarios.py

# Run R tests
$ [sudo] make r-test
```

Enabling features like code autocompletion and linting in your editor
requires one extra step (prerequisites: up-to-date pip and setuptools v64+):

```sh
$ cd repos

# Installs the working directory as an "editable package"
$ pip install -e . --config-settings editable_mode=strict
```

## Running local epidata acquisition

From the `driver` directory, run

```sh
# If containers are not already started
$ [sudo] make all

# Starts a bash session inside the `delphi_web_python` container
$ [sudo] make bash
```

If the container was successfully started, you should see a prompt that looks like `root@containerhash:/usr/src/app#`.

From the container, run

```sh
# In production, acquisition injects secrets automatically, but for local runs we need to replace them manually. The values are found in the `sqlalchemy_uri` variable defined eariler in the Makefile.
$ sed -i -e 's/{SECRET_DB_USERNAME_EPI}/user/g' -e 's/{SECRET_DB_PASSWORD_EPI}/pass/g' -e 's/{SECRET_DB_HOST}/delphi_database_epidata/g' delphi/operations/secrets.py
# May need to run
$ pip install --upgrade mysql-connector-python
# Run an acquisition pipeline, e.g.
$ python -m delphi.epidata.acquisition.flusurv.flusurv_update all
```

You may need to add '$(M1)' flag to subcommands if using a new M\* chip Mac. The '$(M1)' flag is added to commands within the [Makefile](https://github.com/cmu-delphi/delphi-epidata/blob/cae43f8/dev/local/Makefile), so take a look there for guidance.

## Running local epidata API

From the `driver` directory, run

```sh
# Starts a MySQL prompt that can be used to query the local database.
# This connection can be kept open while adding data to the database.
$ [sudo] make sql
```

If the container was successfully started, you should see a prompt that looks like `root@containerhash:/usr/src/app#`.

From the container, open a Python session with `python` and then run

```python
from delphi.epidata.client.delphi_epidata import Epidata

# use the local instance of the Epidata API
Epidata.BASE_URL = 'http://delphi_web_epidata/epidata'

# Run API calls as normal, e.g.
Epidata.fluview(regions = "ny", epiweeks = Epidata.range(202340, 202342))
```


## Other useful commands and information

```sh
# Removes dangling docker images (old images after you've created a new build of the image)
$ [sudo] make clean
```

The structure of the `driver` directory is largely replicated inside of the `delphi_web_python` container, with the following exceptions:

  - Python package names can't contain hyphens, so hyphens in repo names are
    replaced with underscores in the package hierarchy. (An exception is the
    repo `delphi-epidata`, which is renamed to simply `epidata`.)
  - Repos are organized such that the main code for the package is inside of
    a `src/` directory. When deployed,
    [the contents of `src/` are moved](https://github.com/cmu-delphi/delphi-epidata/blob/cae43f8/dev/docker/python/setup.sh#L22-L27).
    (An [exception is the legacy `undef-analysis` repo](https://github.com/cmu-delphi/delphi-epidata/blob/cae43f8/dev/docker/python/setup.sh#L17-L18),
    which has sources at the top-level.)

Dependencies in [`delphi-epidata/requirements.api.txt` and `delphi-epidata/requirements.dev.txt` are installed](https://github.com/cmu-delphi/delphi-epidata/blob/cae43f8/dev/docker/python/Dockerfile#L13).

The [`delphi-epidata` code is mounted](https://github.com/cmu-delphi/delphi-epidata/blob/cae43f8/dev/local/Makefile#L203-L204) for `test`, `r-test`, and `bash` Make targets so any changes to `delphi-epidata` code or tests are automatically reflected in the Docker container without needing to rebuild.

The `delphi-epidata` (and other repos) found in `driver/repos/delphi` is a full copy of the repo, using the default branch.
Other branches can be checked out too, so development can happen directly in this copy of the repo (_recommended_).
If you have pre-existing work elsewhere on your machine that would be inconvenient to move into the `driver` directory, it is possible to locally change the mount path in the Makefile or perhaps to create a symlink to your other local copy of the repo.

Depending on your GitHub authentication method, [the clone method used during setup](https://github.com/cmu-delphi/delphi-epidata/blob/cae43f8/dev/local/install.sh#L34) may not allow you to push changes or new branches to the remote. In this case, please re-authenticate, or re-clone the repo within `driver/repos/delphi` using your standard method.

# COVIDcast

At the present, our primary focus is developing and expanding the
[COVIDcast API](https://cmu-delphi.github.io/delphi-epidata/api/covidcast.html),
which offers a number of data streams relating to the ongoing COVID-19
pandemic and powers the [COVIDcast project](https://covidcast.cmu.edu/).

Our other, non-COVID data sources remain generally available on a best-effort
basis. However, non-COVID sources should be held to scrutiny at this time since
they were designed to serve as indicators of typical seasonal ILI
(influenza-like illness), not pandemic ILI or CLI (COVID-like illness).

For a high-level introduction to the COVIDcast API, see our recent
[blog post](https://delphi.cmu.edu/blog/2020/10/07/accessing-open-covid-19-data-via-the-covidcast-epidata-api/).

# Contributing

If you are interested in contributing:

- For development of the API itself, see the
  [development guide](docs/epidata_development.md).
- To suggest changes, additions, or other ways to improve,
  [open an issue](https://github.com/cmu-delphi/delphi-epidata/issues/new)
  describing your idea.

# Citing

We hope that this API is useful to others outside of our group, especially for
epidemiological and other scientific research. If you use this API and would
like to cite it, we would gratefully recommend the following copy:

> David C. Farrow,
> Logan C. Brooks,
> Ryan J. Tibshirani,
> Roni Rosenfeld
> (2015).
> _Delphi Epidata API_.
> https://github.com/cmu-delphi/delphi-epidata

See [related work](docs/related_work.md) for a sample of additional work in
this area.
