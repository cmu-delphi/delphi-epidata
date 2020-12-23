from invoke import task

@task
def start(c):
    c.run("uvicorn src.server.main:app --reload")