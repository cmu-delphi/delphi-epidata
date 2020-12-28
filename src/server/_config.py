import os
from dotenv import load_dotenv
from flask import Flask
import json

load_dotenv()

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///test.db")
SQLALCHEMY_ENGINE_OPTIONS = json.loads(
    os.environ.get("SQLALCHEMY_ENGINE_OPTIONS", "{}")
)
SECRET = os.environ["SECRET"]

AUTH = {"fluview": "xxx"}
