import json
import os
from dotenv import load_dotenv
import json
from enum import Enum
from datetime import date

load_dotenv()

VERSION = "0.4.7"

MAX_RESULTS = int(10e6)
MAX_COMPATIBILITY_RESULTS = int(3650)

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///test.db")

# defaults
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,  # enable ping test for validity of recycled pool connections on connect() calls
    "pool_recycle": 5       # seconds after which a recycled pool connection is considered invalid
}
# update with overrides of defaults or additions from external configs
SQLALCHEMY_ENGINE_OPTIONS.update(
    json.loads(os.environ.get("SQLALCHEMY_ENGINE_OPTIONS", "{}")))

SECRET = os.environ.get("FLASK_SECRET", "secret")
URL_PREFIX = os.environ.get("FLASK_PREFIX", "/")

# REVERSE_PROXIED is a boolean value that indicates whether or not this server instance
# is running behind a reverse proxy (like nginx).
# in dev and testing, it is fine (or even preferable) for this variable to be set to 'TRUE'
# even if it is not actually the case.  in prod, it is very important that this is set accurately --
# it should _only_ be set to 'TRUE' if it really is behind a reverse proxy, as remote addresses can be "spoofed"
# which can carry security/identity implications.  conversely, if this is set to 'FALSE' when in fact
# running behind a reverse proxy, it can hinder logging accuracy.  it defaults to 'FALSE' for safety.
REVERSE_PROXIED = (os.environ.get("REVERSE_PROXIED", "FALSE").upper() == 'TRUE')

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
ADMIN_PASSWORD = os.environ.get('API_KEY_ADMIN_PASSWORD', 'abc')
# secret for the google form to give to the admin/register endpoint
REGISTER_WEBHOOK_TOKEN = os.environ.get('API_KEY_REGISTER_WEBHOOK_TOKEN')
# see recaptcha
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')

REDIS_HOST = os.environ.get('REDIS_HOST', 'delphi_redis')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '1234')

# https://flask-limiter.readthedocs.io/en/stable/#rate-limit-string-notation
RATE_LIMIT = os.environ.get('RATE_LIMIT', '100/hour')
# fixed-window, fixed-window-elastic-expiry, or moving-window
# see also https://flask-limiter.readthedocs.io/en/stable/#rate-limiting-strategies
RATELIMIT_STRATEGY = os.environ.get('RATELIMIT_STRATEGY', 'fixed-window')

# see https://flask-limiter.readthedocs.io/en/stable/#configuration
RATELIMIT_STORAGE_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379'


class UserRole(str, Enum):
    afhsb = "afhsb"
    cdc = "cdc"
    fluview = "fluview"
    ght = "ght"
    norostat = "norostat"
    quidel = "quidel"
    sensors = "sensors"
    sensor_twtr = "sensor_twtr"
    sensor_gft = "sensor_gft"
    sensor_ght = "sensor_ght"
    sensor_ghtj = "sensor_ghtj"
    sensor_cdc = "sensor_cdc"
    sensor_quid = "sensor_quid"
    sensor_wiki = "sensor_wiki"
    twitter = "twitter"

# Begin sensor query authentication configuration
# A multimap of sensor names to the "granular" auth tokens that can be used to access them;
# excludes the "global" sensor auth key that works for all sensors:
GRANULAR_SENSOR_ROLES = {
    "twtr": UserRole.sensor_twtr,
    "gft": UserRole.sensor_gft,
    "ght": UserRole.sensor_ght,
    "ghtj": UserRole.sensor_ghtj,
    "cdc": UserRole.sensor_cdc,
    "quid": UserRole.sensor_quid,
    "wiki": UserRole.sensor_wiki,
}

# A set of sensors that do not require an auth key to access:
OPEN_SENSORS = [
    "sar3",
    "epic",
    "arch",
]
