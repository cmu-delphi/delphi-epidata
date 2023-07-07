"""Code shared among multiple `covid_hosp` scrapers."""

# standard library
import datetime
import re

import pandas as pd

from delphi.epidata.acquisition.covid_hosp.common.network import Network

class CovidHospException(Exception):
  """Exception raised exclusively by `covid_hosp` utilities."""


class Utils:

  # regex to extract issue date from revision field
  # example revision: "Mon, 11/16/2020 - 00:55"
  REVISION_PATTERN = re.compile(r'^.*\s(\d+)/(\d+)/(\d+)\s.*$')

  def int_from_date(date):
    """Convert a YYYY/MM/DD date from a string to a YYYYMMDD int.

    Parameters
    ----------
    date : str
      Date in "YYYY/MM/DD.*" format.

    Returns
    -------
    int
      Date in YYYYMMDD format.
    """
    if isinstance(date, str):
      return int(date[:10].replace('/', '').replace('-', ''))
    return date

  def parse_bool(value):
    """Convert a string to a boolean.

    Parameters
    ----------
    value : str
      Boolean-like value, like "true" or "false".

    Returns
    -------
    bool
      If the string contains some version of "true" or "false".
    None
      If the string is None or empty.

    Raises
    ------
    CovidHospException
      If the string constains something other than a version of "true" or
      "false".
    """

    if not value:
      return None
    if value.lower() == 'true':
      return True
    if value.lower() == 'false':
      return False
    raise CovidHospException(f'cannot convert "{value}" to bool')

  def limited_string_fn(length):
    def limited_string(value):
      value = str(value)
      if len(value) > length:
        raise CovidHospException(f"Value '{value}':{len(value)} longer than max {length}")
      return value
    return limited_string

  GEOCODE_LENGTH = 32
  GEOCODE_PATTERN = re.compile(r'POINT \((-?[0-9.]+) (-?[0-9.]+)\)')
  def limited_geocode(value):
    if len(value) < Utils.GEOCODE_LENGTH:
      return value
    # otherwise parse and set precision to 6 decimal places
    m = Utils.GEOCODE_PATTERN.match(value)
    if not m:
      raise CovidHospException(f"Couldn't parse geocode '{value}'")
    return f'POINT ({" ".join(f"{float(x):.6f}" for x in m.groups())})'
