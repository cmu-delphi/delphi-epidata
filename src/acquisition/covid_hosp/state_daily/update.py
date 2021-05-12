"""
Acquires the "COVID-19 Reported Patient Impact and Hospital Capacity by State"
dataset provided by the US Department of Health & Human Services
via healthdata.gov.
"""
# standard library
import json

# third party
import pandas as pd

# first party
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.state_daily.database import Database
from delphi.epidata.acquisition.covid_hosp.state_daily.network import Network


class Update:

  @staticmethod
  def run(network=Network):
    """Acquire the most recent dataset, unless it was previously acquired.

    Returns
    -------
    bool
      Whether a new dataset was acquired.
    """

    return Utils.update_dataset(Database, network)

# main entry point
Utils.launch_if_main(Update.run, __name__)
