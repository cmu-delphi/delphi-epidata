"""Utility functions only used in tests.

This code is not used in production.

The functions in this file are used by both unit and integration tests.
However, unit tests can't import code that lives in integration tests, and vice
versa. As a result, common test code has to live under the top-level `/src`
dir, hence the existence of this file.
"""

# standard library
import json
from pathlib import Path

# third party
import pandas


class TestUtils:

  def __init__(self, abs_path_to_caller):
    # navigate to the root of the delphi-epidata repo
    path_to_repo = Path(abs_path_to_caller)
    while not (path_to_repo / 'testdata').exists():
      if not path_to_repo.name:
        raise Exception('unable to determine path to delphi-epidata repo')
      path_to_repo = path_to_repo.parent

    # path to the data, relative to the root of the repo
    rel_data_path = 'testdata/acquisition/covid_hosp/state_timeseries/'
    self.data_dir = (path_to_repo / rel_data_path).resolve()

  def load_sample_metadata(self):
    with open(self.data_dir / 'metadata.json', 'rb') as f:
      return json.loads(f.read().decode('utf-8'))

  def load_sample_dataset(self):
    return pandas.read_csv(self.data_dir / 'dataset.csv')
