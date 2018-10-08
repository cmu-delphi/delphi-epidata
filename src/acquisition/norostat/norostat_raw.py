"""
Functions to fetch, save, load, and format the NoroSTAT data-table. Formatting
functions include conversion from html content to "wide_raw" --- a wide data
frame in a tuple along with metadata --- and then to "long_raw" --- a long/tall
data frame in a tuple along with metadata. Metadata: release_date, parse_time,
and (constant) location. Here, the location will be (a str representing) a set
of states.
"""



# standard library
import datetime
import re
import pickle

# third party
import requests
import lxml.html
import pandas as pd

# first party
from norostat_utils import *

def fetch_content(norostat_datatable_url="https://www.cdc.gov/norovirus/reporting/norostat/data-table.html"):
  """Download NoroSTAT data-table.  Returns the html content."""
  headers = {
    'User-Agent': 'delphibot/1.0 (+https://delphi.midas.cs.cmu.edu/)',
  }
  resp = requests.get(norostat_datatable_url, headers=headers)
  expect_value_eq(resp.status_code, 200,
                  'Wanted status code {}.  Received: ')
  expect_value_eq(resp.headers.get("Content-Type"), "text/html",
                  'Expected Content-Type "{}"; Received ')
  return resp.content

def save_sample_content(content, f="sample_content.pickle"):
  """Save the content from fetch_content into a pickle file for most testing (don't download unnecessarily)."""
  with open(f, "wb") as handle:
    pickle.dump(content, handle)

def load_sample_content(f="sample_content.pickle"):
  """Load data from a past call to fetch_content from a pickle file for most testing (don't download unnecessarily)."""
  with open(f, "rb") as handle:
    content = pickle.load(handle)
  return content

def parse_content_to_wide_raw(content):
  """Convert the html content for the data-table into a wide data frame, then stick it in a tuple along with the release_date, parse_time, and (constant) location."""
  parse_time = datetime.datetime.now()
  html_root = lxml.html.fromstring(content)
  # Extract the release date, a.k.a. dateModified, a.k.a. "Page last updated" date
  [dateModified_elt] = html_root.xpath('//span[@itemprop="dateModified"]')
  # FIXME check/enforce locale
  release_date = datetime.datetime.strptime(dateModified_elt.text, "%B %d, %Y").date()
  # Check that table description still specifies suspected&confirmed norovirus
  # outbreaks, then extract list of states from the description:
  [description_elt] = html_root.xpath('''//p[
    starts-with(text(), "Suspected and Confirmed Norovirus Outbreaks Reported by State Health Departments in") and
    contains(text(), "to the")
  ]''')
  location = re.match(".*?Departments in (.*?) to the.*$", description_elt.text).group(1)
  # Attempt to find exactly 1 table (note: it would be nice to filter on the
  # associated caption, but no such caption is present in earlier versions):
  [table] = html_root.xpath('//table')
  # Convert html table to DataFrame:
  #   Directly reading in the table with pd.read_html performs unwanted dtype
  #   inference, but reveals the column names:
  [wide_raw_df_with_unwanted_conversions] = pd.read_html(lxml.html.tostring(table))
  #   We want all columns to be string columns. However, there does not appear
  #   to be an option to disable dtype inference in pd.read_html. Hide all
  #   entries inside 1-tuple wrappers using pre-dtype-inference converters,
  #   then unpack afterward (the entries fed to the converters should already
  #   be strings, but "convert" them to strings just in case):
  [wide_raw_df_with_wrappers] = pd.read_html(
      lxml.html.tostring(table),
      converters= {col: lambda entry: (str(entry),)
                   for col in wide_raw_df_with_unwanted_conversions.columns}
  )
  #   Unwrap entries:
  wide_raw_df = wide_raw_df_with_wrappers.applymap(lambda wrapper: wrapper[0])
  # Check format:
  expect_value_eq(wide_raw_df.columns[0], "Week",
                  'Expected raw_colnames[0] to be "{}"; encountered ')
  for colname in wide_raw_df.columns:
    expect_result_eq(dtype_kind, wide_raw_df[colname].head(), "O",
                     'Expected (head of) "%s" column to have dtype kind "{}"; instead had dtype kind & head '%(colname))
  # Pack up df with metadata:
  wide_raw = (wide_raw_df, release_date, parse_time, location)
  return wide_raw

def melt_wide_raw_to_long_raw(wide_raw):
  (wide_raw_df, release_date, parse_time, location) = wide_raw
  long_raw_df = wide_raw_df \
                .melt(id_vars=["Week"], var_name="measurement_type", value_name="value") \
                .rename(index=str, columns={"Week": "week"})
  long_raw = (long_raw_df, release_date, parse_time, location)
  return long_raw
