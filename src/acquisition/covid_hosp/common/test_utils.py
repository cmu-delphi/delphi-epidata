"""Utility functions only used in tests.

This code is not used in production.

The functions in this file are used by both unit and integration tests.
However, unit tests can't import code that lives in integration tests, and vice
versa. As a result, common test code has to live under the top-level `/src`
dir, hence the existence of this file.
"""

# standard library
from pathlib import Path
from unittest.mock import patch

# third party
import pandas

from delphi.epidata.acquisition.covid_hosp.common.database import Database
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething
import delphi.operations.secrets as secrets

class TestDatabase(Database):
  DATASET_NAME = 'mock_dataset'

  @staticmethod
  def create_mock_database(table_name=None,
                           dataset_id=None,
                           metadata_id=None,
                           issue_col=None,
                           csv_cols=[],
                           key_cols=[],
                           aggregate_cols=[]):
    with patch.object(CovidHospSomething, 'get_ds_table_name', return_value=table_name), \
        patch.object(CovidHospSomething, 'get_ds_dataset_id', return_value=dataset_id), \
        patch.object(CovidHospSomething, 'get_ds_metadata_id', return_value=metadata_id), \
        patch.object(CovidHospSomething, 'get_ds_issue_column', return_value=issue_col), \
        patch.object(CovidHospSomething, 'get_ds_ordered_csv_cols', return_value=csv_cols), \
        patch.object(CovidHospSomething, 'get_ds_key_cols', return_value=key_cols), \
        patch.object(CovidHospSomething, 'get_ds_aggregate_key_cols', return_value=aggregate_cols):
      return TestDatabase()

class UnitTestUtils:

  # path to `covid_hosp` test data, relative to the top of the repo
  PATH_TO_TESTDATA = 'testdata/acquisition/covid_hosp'

  def __init__(self, abs_path_to_caller):
    # navigate to the root of the delphi-epidata repo
    dataset_name = None
    current_path = Path(abs_path_to_caller)
    while not (current_path / 'testdata').exists():

      # bail if we made it all the way to root
      if not current_path.name:
        raise Exception('unable to determine path to delphi-epidata repo')

      # looking for a path like .../acquisition/covid_hosp/<dataset>
      if current_path.parent.name == 'covid_hosp':
        dataset_name = current_path.name

      # move up one level
      current_path = current_path.parent

    # the loop above stops at the top of the repo
    path_to_repo = current_path

    if not dataset_name:
      raise Exception('unable to determine name of dataset under test')

    # path dataset-specific test data, relative to the root of the repo
    self.data_dir = (
        path_to_repo / UnitTestUtils.PATH_TO_TESTDATA / dataset_name
    ).resolve()

  def load_sample_metadata(self, metadata_name='metadata.csv'):
    df = pandas.read_csv(self.data_dir / metadata_name, dtype=str)
    df["Update Date"] = pandas.to_datetime(df["Update Date"])
    df.sort_values("Update Date", inplace=True)
    df.set_index("Update Date", inplace=True)
    return df

  def load_sample_dataset(self, dataset_name='dataset.csv'):
    return pandas.read_csv(self.data_dir / dataset_name, dtype=str)

  def truncate_tables(self, database, tables):
    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    # clear relevant tables
    with database.connect() as db:
      with db.new_cursor() as cur:
        for table in tables:
          cur.execute(f'truncate table {table}')
