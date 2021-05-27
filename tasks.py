from invoke import task, Context


@task
def start(c):
    c.run("python -m src.server.main")


@task
def update_gdoc(
    c,
    sources_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRfXo-qePhrYGAoZqewVnS1kt9tfnUTLgtkV7a-1q7yg4FoZk0NNGuB1H6k10ah1Xz5B8l1S1RB17N6/pub?gid=0&single=true&output=csv",
    signal_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRfXo-qePhrYGAoZqewVnS1kt9tfnUTLgtkV7a-1q7yg4FoZk0NNGuB1H6k10ah1Xz5B8l1S1RB17N6/pub?gid=329338228&single=true&output=csv",
):
    import pandas as pd
    import pathlib

    def _clean_column(c: str) -> str:
        return c.lower().replace(" ", "_").replace("-", "_")

    base_dir = pathlib.Path("./src/server/config/")

    def _migrate_file(url: str, filename: str):
        df: pd.DataFrame = pd.read_csv(url)
        df.columns = map(_clean_column, df.columns)
        file_ = base_dir / filename
        df = df[df.source.notnull()]
        df.to_json(file_, orient="records", indent=2)

    _migrate_file(sources_url, "db_sources.json")
    _migrate_file(signal_url, "db_signals.json")
