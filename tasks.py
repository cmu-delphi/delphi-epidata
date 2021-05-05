from invoke import task


@task
def start(c):
    c.run("python -m src.server.main")