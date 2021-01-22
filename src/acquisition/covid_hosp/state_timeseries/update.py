"""
Acquires the "COVID-19 Reported Patient Impact and Hospital Capacity by State
Timeseries" dataset provided by the US Department of Health & Human Services
via healthdata.gov.
"""

# first party
import argparse

from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.state_timeseries.database import Database
from delphi.epidata.acquisition.covid_hosp.state_timeseries.network import Network


class Update:

  def run(network=Network):
    """Acquire the most recent dataset, unless it was previously acquired.

    Returns
    -------
    bool
      Whether a new dataset was acquired.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", help="Select a past revision to reload")
    args = parser.parse_args()
    return Utils.update_dataset(Database, network, args.revision)

# main entry point
Utils.launch_if_main(Update.run, __name__)
