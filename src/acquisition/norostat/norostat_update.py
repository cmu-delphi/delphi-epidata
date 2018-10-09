"""
===============
=== Purpose ===
===============

Fetch NoroSTAT data table from
<https://www.cdc.gov/norovirus/reporting/norostat/data-table.html>;
process and record it in the appropriate databases.
"""

# standard library
import datetime
import re
import os
import time
import collections

# third party
import pandas as pd
import mysql.connector

# first party
from . import norostat_sql
from . import norostat_raw
from delphi.utils.epidate import EpiDate
import delphi.operations.secrets as secrets



def main():
  # Download the data:
  # content = norostat_raw.load_sample_content()
  content = norostat_raw.fetch_content()
  # norostat_raw.save_sample_content(content)
  wide_raw = norostat_raw.parse_content_to_wide_raw(content)
  long_raw = norostat_raw.melt_wide_raw_to_long_raw(wide_raw)
  norostat_sql.ensure_tables_exist()
  norostat_sql.record_long_raw(long_raw)
  norostat_sql.update_point()

if __name__ == '__main__':
  main()
