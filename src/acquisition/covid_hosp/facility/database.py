# first party
from delphi.epidata.acquisition.covid_hosp.common.database import Database as BaseDatabase
from delphi.epidata.acquisition.covid_hosp.facility.network import Network
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething


class Database(BaseDatabase):

  # ORDERED_CSV_COLUMNS are 3-tuples of (
  #   CSV header name,
  #   SQL db column name,
  #   data type
  # ) for all the columns in the CSV file.
  # Note that the corresponding database column names may be shorter
  # due to constraints on the length of column names. See
  # /src/ddl/covid_hosp.sql for more information.
  TABLE_NAME, KEY_COLS, ORDERED_CSV_COLUMNS = CovidHospSomething("../../../common/covid_hosp/covid_hosp_schemadefs.yaml").get_ds_info('covid_hosp_facility')

  def __init__(self, *args, **kwargs):
    super().__init__(
        *args,
        **kwargs,
        table_name=Database.TABLE_NAME,
        hhs_dataset_id=Network.DATASET_ID,
        key_columns=Database.KEY_COLS,
        columns_and_types=Database.ORDERED_CSV_COLUMNS)
