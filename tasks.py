"""Repo tasks."""
import pathlib
import sys

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
def lint(c, incremental=True, format=True, revision="origin/dev...", diff=False):  # pylint: disable=redefined-builtin
    """Lint and format.

    Additional linter settings can be found in `pyproject.toml` (this invocation
    will use those settings as well).

    Parameters
    ----------
    incremental : bool
        Only lint changed files.
    format : bool
        Apply formatting changes.
    revision : str
        Revision to compare against.
    diff : bool
        Only show formatting changes, do not apply.
    """
    diff = "--diff" if diff else ""
    if incremental:
        if format:
            c.run(f"darker --revision {revision} {diff} .")
        out = c.run(f"git diff -U0 {revision} | lint-diffs")
        if out.stdout.strip() != "=== pylint: mine=0, always=0":
            print(out.stdout)
            sys.exit(1)
    else:
        if format:
            reponse = input("This will format all files in this repo, continue? [y/N]")
            if reponse.lower() not in ("y", "yes"):
                return
            c.run(f"black {diff} .")
            c.run(f"isort {diff} .")
        c.run("pylint src/ tests/ integrations/")
