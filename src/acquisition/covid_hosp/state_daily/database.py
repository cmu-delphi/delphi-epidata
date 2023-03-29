# first party
from delphi.epidata.acquisition.covid_hosp.common.database import Database as BaseDatabase
from delphi.epidata.acquisition.covid_hosp.common.database import Columndef
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.state_daily.network import Network
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething


class Database(BaseDatabase):

  # note we share a database with state_timeseries

  # ORDERED_CSV_COLUMNS are 3-tuples of (
  #   CSV header name,
  #   SQL db column name,
  #   data type
  # ) for all the columns in the CSV file.
  # Note that the corresponding database column names may be shorter
  # due to constraints on the length of column names. See
  # /src/ddl/covid_hosp.sql for more information.
  TABLE_NAME, KEY_COLS, ORDERED_CSV_COLUMNS = CovidHospSomething.get_ds_info('state_daily')

  def __init__(self, *args, **kwargs):
    super().__init__(
        *args,
        **kwargs,
        table_name=Database.TABLE_NAME,
        hhs_dataset_id=Network.DATASET_ID,
        columns_and_types=Database.ORDERED_CSV_COLUMNS,
        key_columns=Database.KEY_COLS,
        additional_fields=[Columndef('D', 'record_type', None)])
