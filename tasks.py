"""Repo tasks."""

import pathlib

import requests
from invoke import task


@task
def start(c):
    c.run("python -m src.server.main")


@task
def update_gdoc(
    c,
    sources_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRfXo-qePhrYGAoZqewVnS1kt9tfnUTLgtkV7a-1q7yg4FoZk0NNGuB1H6k10ah1Xz5B8l1S1RB17N6/pub?gid=0&single=true&output=csv",
    signal_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRfXo-qePhrYGAoZqewVnS1kt9tfnUTLgtkV7a-1q7yg4FoZk0NNGuB1H6k10ah1Xz5B8l1S1RB17N6/pub?gid=329338228&single=true&output=csv",
):
    base_dir = pathlib.Path("./src/server/endpoints/covidcast_utils/")

    def _migrate_file(url: str, filename: str):
        r = requests.get(url).text.replace("\r\n", "\n")
        rows = r.split("\n")
        rows = [r for r in rows if not r.startswith(",")]
        file_ = base_dir / filename
        file_.write_text("\n".join(rows), encoding="utf8")

    _migrate_file(sources_url, "db_sources.csv")
    _migrate_file(signal_url, "db_signals.csv")


@task
def lint(c, revision="origin/dev"):
    """Lint.

    Linters automatically read from `pyproject.toml`.
    """
    c.run(f"darker --diff --check --revision {revision} .", warn=True)
    c.run("echo '\n'")
    out = c.run(f"git diff -U0 {revision} | lint-diffs")
    if out.stdout.strip() != "=== pylint: mine=0, always=0":
        print(out.stdout)


@task
def format(c, revision="origin/dev"):  # pylint: disable=redefined-builtin
    """Format.

    Darker will format files for you and print which ones changed.
    """
    c.run(f"darker --verbose --revision {revision} .", warn=True)
