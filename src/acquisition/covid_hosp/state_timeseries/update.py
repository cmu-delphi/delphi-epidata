"""
Acquires the "COVID-19 Reported Patient Impact and Hospital Capacity by State
Timeseries" dataset provided by the US Department of Health & Human Services
via healthdata.gov.
"""

# first party
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.state_timeseries.database import Database


# main entry point
if __name__ == '__main__':
  Utils.update_dataset(Database)
