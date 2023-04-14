# first party
from delphi.epidata.acquisition.covid_hosp.common.database import Database as BaseDatabase
from delphi.epidata.acquisition.covid_hosp.facility.network import Network
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething


class Database(BaseDatabase):

  chs = CovidHospSomething()
  TABLE_NAME = chs.get_ds_table_name('covid_hosp_facility')
  KEY_COLS = chs.get_ds_key_cols('covid_hosp_facility')
  AGGREGATE_KEY_COLS = chs.get_ds_aggregate_key_cols('covid_hosp_facility')
  ORDERED_CSV_COLUMNS = chs.get_ds_ordered_csv_cols('covid_hosp_facility')

  def __init__(self, *args, **kwargs):
    super().__init__(
        *args,
        **kwargs,
        table_name=Database.TABLE_NAME,
        hhs_dataset_id=Network.DATASET_ID,
        key_columns=Database.KEY_COLS,
        columns_and_types=Database.ORDERED_CSV_COLUMNS)
