"""
===============
=== Purpose ===
===============

Defines a mapping of location names from CDC to the Delphi API.

See also:
  - fluview_update.py
"""


# These keys come from CDC's metadata object, which is currently returned in a
# JSON response from:
# https://gis.cdc.gov/grasp/flu2/GetPhase02InitApp?appVersion=Public
# The values are used in queries of Delphi's Epidata API.
cdc_to_delphi = {
  'national': {
    'x': 'nat',
  },
  'hhs regions': {
    'region 1': 'hhs1',
    'region 2': 'hhs2',
    'region 3': 'hhs3',
    'region 4': 'hhs4',
    'region 5': 'hhs5',
    'region 6': 'hhs6',
    'region 7': 'hhs7',
    'region 8': 'hhs8',
    'region 9': 'hhs9',
    'region 10': 'hhs10',
  },
  'census regions': {
    'new england': 'cen1',
    'mid-atlantic': 'cen2',
    'east north central': 'cen3',
    'west north central': 'cen4',
    'south atlantic': 'cen5',
    'east south central': 'cen6',
    'west south central': 'cen7',
    'mountain': 'cen8',
    'pacific': 'cen9',
  },
  'states': {
    # states/territories: two-letter ISO 3166
    'alabama': 'al',
    'alaska': 'ak',
    'arizona': 'az',
    'arkansas': 'ar',
    'california': 'ca',
    'colorado': 'co',
    'connecticut': 'ct',
    'delaware': 'de',
    'florida': 'fl',
    'georgia': 'ga',
    'hawaii': 'hi',
    'idaho': 'id',
    'illinois': 'il',
    'indiana': 'in',
    'iowa': 'ia',
    'kansas': 'ks',
    'kentucky': 'ky',
    'louisiana': 'la',
    'maine': 'me',
    'maryland': 'md',
    'massachusetts': 'ma',
    'michigan': 'mi',
    'minnesota': 'mn',
    'mississippi': 'ms',
    'missouri': 'mo',
    'montana': 'mt',
    'nebraska': 'ne',
    'nevada': 'nv',
    'new hampshire': 'nh',
    'new jersey': 'nj',
    'new mexico': 'nm',
    'new york': 'ny',
    'north carolina': 'nc',
    'north dakota': 'nd',
    'ohio': 'oh',
    'oklahoma': 'ok',
    'oregon': 'or',
    'pennsylvania': 'pa',
    'rhode island': 'ri',
    'south carolina': 'sc',
    'south dakota': 'sd',
    'tennessee': 'tn',
    'texas': 'tx',
    'utah': 'ut',
    'vermont': 'vt',
    'virginia': 'va',
    'washington': 'wa',
    'west virginia': 'wv',
    'wisconsin': 'wi',
    'wyoming': 'wy',
    'american samoa': 'as',
    'commonwealth of the northern mariana islands': 'mp',
    'district of columbia': 'dc',
    'guam': 'gu',
    'puerto rico': 'pr',
    'virgin islands': 'vi',
    # cities: three-letter IATA
    'chicago': 'ord',
    'los angeles': 'lax',
    'new york city': 'jfk',
  },
}


def get_location_name(region_type, region_name):
  """Convert a CDC location type and name pair into a Delphi location name."""
  return cdc_to_delphi[region_type.lower()][region_name.lower()]
