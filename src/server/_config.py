import json
import os
from datetime import date
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

VERSION = "4.1.9"

MAX_RESULTS = int(10e6)
MAX_COMPATIBILITY_RESULTS = int(3650)

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///test.db")
SQLALCHEMY_DATABASE_URI_PRIMARY = os.environ.get("SQLALCHEMY_DATABASE_URI_PRIMARY")

# defaults
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,  # enable ping test for validity of recycled pool connections on connect() calls
    "pool_recycle": 5,  # seconds after which a recycled pool connection is considered invalid
}
# update with overrides of defaults or additions from external configs
SQLALCHEMY_ENGINE_OPTIONS.update(json.loads(os.environ.get("SQLALCHEMY_ENGINE_OPTIONS", "{}")))

SECRET = os.environ.get("FLASK_SECRET", "secret")
URL_PREFIX = os.environ.get("FLASK_PREFIX", "") # if not empty, this value should begin but not end in a slash ('/')


"""
REVERSE_PROXY_DEPTH is an integer value that indicates how many "chained" and trusted reverse proxies (like nginx) this
 server instance is running behind.  "chained" refers to proxies forwarding to other proxies, and then ultimately
 forwarding to the app server itself.  each of these proxies appends the remote address of the request to the
 "X-Forwarded-For" header.  in many situations, the most externally facing proxy (the first in the chain, the one that
 faces the "open internet") can and should be set to write its own "X-Forwarded-For" header, ignoring and replacing
 (or creating anew, if it didnt exist) such a header from the client request -- thus preserving the chain of trusted
 proxies under our control.

however, in our typical production environment, the most externally facing "proxy" is the AWS application load balancer,
 which seemingly cannot be configured to provide this trust boundary without losing the referring client address
 (see: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html ).  accordingly, in
 our current typical production environment, REVERSE_PROXY_DEPTH should be set to "2": one for the AWS application load
 balancer, and one for our own nginx/haproxy instance.  thus "2" is our default value.

it is important that REVERSE_PROXY_DEPTH is set accurately for two reasons...

setting it too high (or to -1) will respect more of the entries in the "X-Forwarded-For" header than are appropriate.
 this can allow remote addresses to be "spoofed" when a client fakes this header, carrying security/identity
 implications.  in dev and testing, it is not particularly dangerous for this variable to be set to -1 (special case
 for an "infinite" depth, where any and all proxy hops will be trusted).

setting it too low can hinder logging accuracy -- that can cause an intermediate proxy IP address to be used as the
 "real" client IP address, which could cause requests to be rate-limited inappropriately.

setting REVERSE_PROXY_DEPTH to "0" essentially indicates there are no proxies between this server and the outside
 world.  in this case, the "X-Forwarded-For" header is ignored.
"""
REVERSE_PROXY_DEPTH = int(os.environ.get("PROXY_DEPTH", 4))
# TODO: ^ this value should be "4" for the prod CC API server processes, and is currently unclear
#       for prod AWS API server processes (but should be the same or lower)...  when thats properly
#       determined, set the default to the minimum of the two environments and special case the
#       other in conf file(s).


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

# password needed for the admin application if not set the admin routes won't be available
ADMIN_PASSWORD = os.environ.get("API_KEY_ADMIN_PASSWORD", "abc")
# secret for the google form to give to the admin/register endpoint
REGISTER_WEBHOOK_TOKEN = os.environ.get("API_KEY_REGISTER_WEBHOOK_TOKEN")

REDIS_HOST = os.environ.get("REDIS_HOST", "delphi_redis")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "1234")

# mode to reduce number of required requests to hit rate limit while running tests,
# by default is set to False
TESTING_MODE = os.environ.get("TESTING_MODE", False)

# https://flask-limiter.readthedocs.io/en/stable/#rate-limit-string-notation
RATE_LIMIT = os.environ.get("RATE_LIMIT", "60/hour")

if TESTING_MODE is not False:
    RATE_LIMIT = "5/hour"

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
