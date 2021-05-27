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
    import requests
    import pathlib

    base_dir = pathlib.Path("./src/server/endpoints/covidcast_utils/")

    def _migrate_file(url: str, filename: str):
        r = requests.get(url).text.replace("\r\n", "\n")
        rows = r.split("\n")
        rows = [r for r in rows if not r.startswith(",")]
        file_ = base_dir / filename
        file_.write_text("\n".join(rows))

    _migrate_file(sources_url, "db_sources.csv")
    _migrate_file(signal_url, "db_signals.csv")
