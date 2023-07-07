"""
Acquires the "COVID-19 Reported Patient Impact and Hospital Capacity by State
Timeseries" dataset provided by the US Department of Health & Human Services
via healthdata.gov.
"""
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.state_timeseries.database import Database


if __name__ == '__main__':
  Database().update_dataset()
