import os
from dotenv import load_dotenv
from flask import Flask
import json

load_dotenv()


MAX_RESULTS = 10e6
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///test.db")
SQLALCHEMY_ENGINE_OPTIONS = json.loads(
    os.environ.get("SQLALCHEMY_ENGINE_OPTIONS", "{}")
)
SECRET = os.environ["SECRET"]

AUTH = {"fluview": "xxx"}

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
