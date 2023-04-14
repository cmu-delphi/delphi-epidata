# first party
from delphi.epidata.acquisition.covid_hosp.common.database import Database as BaseDatabase
from delphi.epidata.acquisition.covid_hosp.common.database import Columndef
from delphi.epidata.acquisition.covid_hosp.state_timeseries.network import Network
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething


class Database(BaseDatabase):

  chs = CovidHospSomething()
  TABLE_NAME = chs.get_ds_table_name('state_timeseries')
  KEY_COLS = chs.get_ds_key_cols('state_timeseries')
  ORDERED_CSV_COLUMNS = chs.get_ds_ordered_csv_cols('state_timeseries')

  def __init__(self, *args, **kwargs):
    super().__init__(
        *args,
        **kwargs,
        table_name=Database.TABLE_NAME,
        hhs_dataset_id=Network.DATASET_ID,
        columns_and_types=Database.ORDERED_CSV_COLUMNS,
        key_columns=Database.KEY_COLS,
        additional_fields=[Columndef('T', 'record_type', None)])
