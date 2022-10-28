import os
from dotenv import load_dotenv
import json
from datetime import date

from flask.app import Flask

load_dotenv()

VERSION = "0.4.0"

MAX_RESULTS = int(10e6)
MAX_COMPATIBILITY_RESULTS = int(3650)

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///test.db")

# defaults
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True, # enable ping test for validity of recycled pool connections on connect() calls
    "pool_recycle": 5      # seconds after which a recycled pool connection is considered invalid
}
# update with overrides of defaults or additions from external configs
SQLALCHEMY_ENGINE_OPTIONS.update(
    json.loads(os.environ.get("SQLALCHEMY_ENGINE_OPTIONS", "{}")))

SECRET = os.environ.get("FLASK_SECRET", "secret")
URL_PREFIX = os.environ.get("FLASK_PREFIX", "/")

AUTH = {
    "twitter": os.environ.get("SECRET_TWITTER"),
    "ght": os.environ.get("SECRET_GHT"),
    "fluview": os.environ.get("SECRET_FLUVIEW"),
    "cdc": os.environ.get("SECRET_CDC"),
    "sensors": os.environ.get("SECRET_SENSORS"),
    "quidel": os.environ.get("SECRET_QUIDEL"),
    "norostat": os.environ.get("SECRET_NOROSTAT"),
    "afhsb": os.environ.get("SECRET_AFHSB"),
}

# begin sensor query authentication configuration
#   A multimap of sensor names to the "granular" auth tokens that can be used to access them; excludes the "global" sensor auth key that works for all sensors:
GRANULAR_SENSOR_AUTH_TOKENS = {
    "twtr": os.environ.get("SECRET_SENSOR_TWTR", "").split(","),
    "gft": os.environ.get("SECRET_SENSOR_GFT", "").split(","),
    "ght": os.environ.get("SECRET_SENSOR_GHT", "").split(","),
    "ghtj": os.environ.get("SECRET_SENSOR_GHTJ", "").split(","),
    "cdc": os.environ.get("SECRET_SENSOR_CDC", "").split(","),
    "quid": os.environ.get("SECRET_SENSOR_QUID", "").split(","),
    "wiki": os.environ.get("SECRET_SENSOR_WIKI", "").split(","),
}

#   A set of sensors that do not require an auth key to access:
OPEN_SENSORS = [
    "sar3",
    "epic",
    "arch",
]

REGION_TO_STATE = {
    "hhs1": ["VT", "CT", "ME", "MA", "NH", "RI"],
    "hhs2": ["NJ", "NY"],
    "hhs3": ["DE", "DC", "MD", "PA", "VA", "WV"],
    "hhs4": ["AL", "FL", "GA", "KY", "MS", "NC", "TN", "SC"],
    "hhs5": ["IL", "IN", "MI", "MN", "OH", "WI"],
    "hhs6": ["AR", "LA", "NM", "OK", "TX"],
    "hhs7": ["IA", "KS", "MO", "NE"],
    "hhs8": ["CO", "MT", "ND", "SD", "UT", "WY"],
    "hhs9": ["AZ", "CA", "HI", "NV"],
    "hhs10": ["AK", "ID", "OR", "WA"],
    "cen1": ["CT", "ME", "MA", "NH", "RI", "VT"],
    "cen2": ["NJ", "NY", "PA"],
    "cen3": ["IL", "IN", "MI", "OH", "WI"],
    "cen4": ["IA", "KS", "MN", "MO", "NE", "ND", "SD"],
    "cen5": ["DE", "DC", "FL", "GA", "MD", "NC", "SC", "VA", "WV"],
    "cen6": ["AL", "KY", "MS", "TN"],
    "cen7": ["AR", "LA", "OK", "TX"],
    "cen8": ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY"],
    "cen9": ["AK", "CA", "HI", "OR", "WA"],
}
NATION_REGION = "nat"

API_KEY_REQUIRED_STARTING_AT = date.fromisoformat(os.environ.get('API_REQUIRED_STARTING_AT', '3000-01-01'))

# password needed for the admin application if not set the admin routes won't be available
ADMIN_PASSWORD = os.environ.get('API_KEY_ADMIN_PASSWORD')
# secret for the google form to give to the admin/register endpoint
REGISTER_WEBHOOK_TOKEN = os.environ.get('API_KEY_REGISTER_WEBHOOK_TOKEN')
# see recaptcha
RECAPTCHA_SITE_KEY= os.environ.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY= os.environ.get('RECAPTCHA_SECRET_KEY')

# https://flask-limiter.readthedocs.io/en/stable/#rate-limit-string-notation
RATE_LIMIT = os.environ.get('RATE_LIMIT', '10/hour')
# fixed-window, fixed-window-elastic-expiry, or moving-window
# see also https://flask-limiter.readthedocs.io/en/stable/#rate-limiting-strategies
RATELIMIT_STRATEGY = os.environ.get('RATELIMIT_STRATEGY', 'fixed-window')
# see https://flask-limiter.readthedocs.io/en/stable/#configuration
RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')


def patch_flask_config(app: Flask):
    """
    patch the configration with some environment variables
    """
    sub = {}
    for k,v in os.environ.items():
        if k.startswith('RATELIMIT'):
            sub[k] = v
    sub.update({
        'SECRET': SECRET,
        'RATELIMIT_STRATEGY': RATELIMIT_STRATEGY,
        'RATELIMIT_STORAGE_URL': RATELIMIT_STORAGE_URL
    })
    app.config.update(sub)
