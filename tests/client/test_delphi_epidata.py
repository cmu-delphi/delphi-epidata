"""Unit tests for delphi_epidata.py."""

# standard library
import unittest
import time
from datetime import date

import pandas as pd

# py3tester coverage target
__test_target__ = 'delphi.epidata.client.delphi_epidata'

from delphi.epidata.client.delphi_epidata import Epidata

class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  # TODO: Unit tests still need to be written. This no-op test will pass unless
  # the target file can't be loaded. In effect, it's a syntax checker.
  def test_syntax(self):
    pass



def test_requests_caching():
    data_source = "chng"
    signal = "smoothed_outpatient_covid"
    time_type = "day"
    start_day = date(2021, 1, 2)
    end_day = date(2021, 1, 12)
    # day_str = "-".join(
    #   [date.strftime("%Y%m%d") for date in pd.date_range(start_day, end_day)]
    # )
    day_str = date(2021, 4, 15).strftime("%Y%m%d")
    day_strs = [date.strftime("%Y%m%d") for date in pd.date_range(start_day, end_day)]
    geo_type = "state"

    then = int(time.time())
    dfs = []
    breakpoint()
    for day_str in day_strs:
      res = Epidata.covidcast(
        data_source, signal, time_type=time_type,
        geo_type=geo_type, time_values=day_str,
        geo_value="ca", cache_timeout=20
      )
      df = pd.DataFrame.from_dict(res['epidata'])
      dfs.append(df)
    df1 = pd.concat(dfs)
    now = int(time.time())
    time_delta1 = now - then

    then = int(time.time())
    for i in range(20):
      df2 = Epidata.covidcast(
      data_source, signal, time_type=time_type,
      geo_type=geo_type, time_values=day_str,
      geo_value="*", cache_timeout=20
    )
    now = int(time.time())
    time_delta2 = now - then

    time.sleep(20)
    then = int(time.time())
    for i in range(20):
      df3 = Epidata.covidcast(
        data_source, signal, time_type=time_type,
        geo_type=geo_type, time_values=day_str,
        geo_value="*", cache_timeout=20
      )
    now = int(time.time())
    time_delta3 = now - then

    breakpoint()
    print("Rows retrieved: {1}, Time taken: {0}".format(df1.size, time_delta1))
    print("Rows retrieved: {1}, Time taken: {0}".format(df2.size, time_delta2))
    print("Rows retrieved: {1}, Time taken: {0}".format(df3.size, time_delta3))
    2
