"""
Acquires the "COVID-19 Reported Patient Impact and Hospital Capacity by
Facility" dataset provided by the US Department of Health & Human Services via
healthdata.gov.
"""
from delphi.epidata.acquisition.covid_hosp.facility.database import Database


if __name__ == '__main__':
  Database().update_dataset()
