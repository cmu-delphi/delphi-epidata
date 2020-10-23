# Status

[![Deploy Status](https://delphi.cmu.edu/~automation/public/github_deploy_repo/badge.php?repo=cmu-delphi/delphi-epidata)](#)

# About

This is the home of [Delphi](https://delphi.cmu.edu/)'s epidemiological data
API. See our [API documentation](https://cmu-delphi.github.io/delphi-epidata/)
for details on the available data sets, APIs, and clients.

## COVIDcast

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
