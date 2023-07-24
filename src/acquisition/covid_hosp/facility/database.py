# first party
from delphi.epidata.acquisition.covid_hosp.common.database import Database as BaseDatabase


class Database(BaseDatabase):

  DATASET_NAME = 'covid_hosp_facility'
