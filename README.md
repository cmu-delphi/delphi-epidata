# Status

[![Deploy Status](https://delphi.cmu.edu/~automation/public/github_deploy_repo/badge.php?repo=cmu-delphi/delphi-epidata)](#)

# About

This is the home of [Delphi](https://delphi.cmu.edu/)'s epidemiological data
API. See our [API documentation](https://cmu-delphi.github.io/delphi-epidata/)
for details on the available data sets, APIs, and clients.

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

Enabling features like code autocompletion and linting in your editor
requires one extra step (prerequisites: up-to-date pip and setuptools v64+):

```sh
$ cd repos

# Installs the working directory as an "editable package"
$ pip install -e . --config-settings editable_mode=strict
```

## Linting and Formatting

The command `inv lint` will lint your changes (using
[lint-diffs](https://github.com/AtakamaLLC/lint-diffs/)) and `inv format` will
format your changes (using [darker](https://github.com/akaihola/darker)). This
will allow us to incrementally bring this repo up to PEP8 compliance. There is
[a CI action](.github/workflows/lint.yaml) to ensure that all new code is
compliant.

To setup the linter commands locally, run the following commands in the root of
the repository:

```sh
# Create a virtual environment
python -m venv venv
source venv/bin/activate
# Install lint dependencies
pip install -r requirements.lint.txt
# Run lint
inv lint
# Run formatter (will tell you which files it modified)
inv format
```

If you get the error `ERROR:darker.git:fatal: Not a valid commit name <hash>`,
then it's likely because your local main branch is not up to date; either you
need to rebase or merge. Note that `darker` reads from `pyproject.toml` for
default settings.

If the lines you change are in a file that uses 2 space indentation, `darker`
will indent the lines around your changes and not the rest, which will likely
break the code; in that case, you should probably just pass the whole file
through black. You can do that with the following command (using the same
virtual environment as above):

```sh
env/bin/black <file>
```

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
