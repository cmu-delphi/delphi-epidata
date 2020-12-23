from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from . import _config as default_config

app = Flask("EpiData")
app.config.from_object(default_config)
# app.config.
db = SQLAlchemy(app)
