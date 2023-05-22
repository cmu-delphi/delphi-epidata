import json
import os
from datetime import date
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

VERSION = "0.4.12"

MAX_RESULTS = int(10e6)
MAX_COMPATIBILITY_RESULTS = int(3650)

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///test.db")

# defaults
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,  # enable ping test for validity of recycled pool connections on connect() calls
    "pool_recycle": 5,  # seconds after which a recycled pool connection is considered invalid
}
# update with overrides of defaults or additions from external configs
SQLALCHEMY_ENGINE_OPTIONS.update(json.loads(os.environ.get("SQLALCHEMY_ENGINE_OPTIONS", "{}")))

SECRET = os.environ.get("FLASK_SECRET", "secret")
URL_PREFIX = os.environ.get("FLASK_PREFIX", "") # if not empty, this value should begin but not end in a slash ('/')

# REVERSE_PROXIED is a boolean value that indicates whether or not this server instance
# is running behind a reverse proxy (like nginx).
# in dev and testing, it is fine (or even preferable) for this variable to be set to 'TRUE'
# even if it is not actually the case.  in prod, it is very important that this is set accurately --
# it should _only_ be set to 'TRUE' if it really is behind a reverse proxy, as remote addresses can be "spoofed"
# which can carry security/identity implications.  conversely, if this is set to 'FALSE' when in fact
# running behind a reverse proxy, it can hinder logging accuracy.  it defaults to 'FALSE' for safety.
REVERSE_PROXIED = os.environ.get("REVERSE_PROXIED", "FALSE").upper() == "TRUE"

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

API_KEY_REQUIRED_STARTING_AT = date.fromisoformat(os.environ.get("API_KEY_REQUIRED_STARTING_AT", "2023-06-21"))
TEMPORARY_API_KEY = os.environ.get("TEMPORARY_API_KEY", "TEMP-API-KEY-EXPIRES-2023-06-28")
# password needed for the admin application if not set the admin routes won't be available
ADMIN_PASSWORD = os.environ.get("API_KEY_ADMIN_PASSWORD", "abc")
# secret for the google form to give to the admin/register endpoint
REGISTER_WEBHOOK_TOKEN = os.environ.get("API_KEY_REGISTER_WEBHOOK_TOKEN")

REDIS_HOST = os.environ.get("REDIS_HOST", "delphi_redis")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "1234")

# https://flask-limiter.readthedocs.io/en/stable/#rate-limit-string-notation
RATE_LIMIT = os.environ.get("RATE_LIMIT", "60/hour")
# fixed-window, fixed-window-elastic-expiry, or moving-window
# see also https://flask-limiter.readthedocs.io/en/stable/#rate-limiting-strategies
RATELIMIT_STRATEGY = os.environ.get("RATELIMIT_STRATEGY", "fixed-window")

# see https://flask-limiter.readthedocs.io/en/stable/#configuration
RATELIMIT_STORAGE_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379"

API_KEY_REGISTRATION_FORM_LINK = "https://forms.gle/hkBr5SfQgxguAfEt7"
# ^ shortcut to "https://docs.google.com/forms/d/e/1FAIpQLSe5i-lgb9hcMVepntMIeEo8LUZUMTUnQD3hbrQI3vSteGsl4w/viewform?usp=sf_link"
API_KEY_REGISTRATION_FORM_LINK_LOCAL = "https://api.delphi.cmu.edu/epidata/admin/registration_form"
# ^ redirects to API_KEY_REGISTRATION_FORM_LINK

API_KEY_REMOVAL_REQUEST_LINK = "https://forms.gle/GucFmZHTMgEFjH197"
# ^ shortcut to "https://docs.google.com/forms/d/e/1FAIpQLSff30tsq4xwPCoUbvaIygLSMs_Mt8eDhHA0rifBoIrjo8J5lw/viewform"
API_KEY_REMOVAL_REQUEST_LINK_LOCAL = "https://api.delphi.cmu.edu/epidata/admin/removal_request"
# ^ redirects to API_KEY_REMOVAL_REQUEST_LINK
