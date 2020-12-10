"""
Acquires the "COVID-19 Reported Patient Impact and Hospital Capacity by State
Timeseries" dataset provided by the US Department of Health & Human Services
via healthdata.gov.
"""

# standard library
import json
import re

# first party
from delphi.epidata.acquisition.covid_hosp.state_timeseries.database import Database
from delphi.epidata.acquisition.covid_hosp.state_timeseries.network import Network


class UpdateException(Exception):
  """Exception raised exclusively by the Update class."""


class Update:

  # regex to extract issue date from revision field
  # example revision: "Mon, 11/16/2020 - 00:55"
  REVISION_PATTERN = re.compile(r'^.*\s(\d+)/(\d+)/(\d+)\s.*$')

  def get_entry(obj, *path):
    """Get a deeply nested field from an arbitrary object.

    Parameters
    ----------
    obj : dict
      The object to traverse.
    path : tuple of names and indices
      Path to the desired field in the object.

    Returns
    -------
    object
      The nested object.

    Raises
    ------
    UpdateException
      If the field can't be found.
    """

    try:
      for elem in path:
        is_index = isinstance(elem, int)
        is_list = isinstance(obj, list)
        if is_index != is_list:
          raise UpdateException('index given for non-list or vice versa')
        obj = obj[elem]
      return obj
    except Exception as ex:
      path_str = '/'.join(map(str, path))
      msg = f'unable to access object path "/{path_str}"'
      raise UpdateException(msg) from ex

  def get_issue_from_revision(revision):
    """Extract and return an issue from a revision string.

    Parameters
    ----------
    revision : str
      The free-form revision string.

    Returns
    -------
    int
      The issue in YYYYMMDD format.

    Raises
    ------
    UpdateException
      If the issue can't be extracted.
    """

    match = Update.REVISION_PATTERN.match(revision)
    if not match:
      raise UpdateException(f'unable to extract issue from "{revision}"')
    y, m, d = match.group(3), match.group(1), match.group(2)
    return int(y) * 10000 + int(m) * 100 + int(d)

  def get_date_as_int(date):
    """Convert a YYYY-MM-DD date from a string to a YYYYMMDD int.

    Parameters
    ----------
    date : str
      Date in YYYY-MM-DD format.

    Returns
    -------
    int
      Date in YYYYMMDD format.
    """

    return int(date.replace('-', ''))

  def extract_resource_details(metadata):
    """Extract resource details, like URL and revision, from metadata.

    Parameters
    ----------
    metadata : dict
      Metadata object as returned from healthcare.gov.

    Returns
    -------
    url : str
      URL of the dataset.
    revision : str
      Free-form revision timestamp of the dataset.

    Raises
    ------
    UpdateException
      If the metadata does not match the expected format.
    """

    # check data integrity
    if Update.get_entry(metadata, 'success') is not True:
      raise UpdateException('metadata does not have `success` equal to `True`')
    if len(Update.get_entry(metadata, 'result')) != 1:
      raise UpdateException('metadata does not have exactly 1 result')
    if len(Update.get_entry(metadata, 'result', 0, 'resources')) != 1:
      raise UpdateException('metadata does not have exactly 1 resource')

    # return resource details
    resource = Update.get_entry(metadata, 'result', 0, 'resources', 0)
    return resource['url'], resource['revision_timestamp']

  def run(database_impl=Database, network_impl=Network):
    """Acquire the most recent dataset, unless it was previously acquired.

    Returns
    -------
    bool
      Whether a new dataset was acquired.
    """

    # get dataset details from metadata
    metadata = network_impl.fetch_metadata()
    url, revision = Update.extract_resource_details(metadata)
    issue = Update.get_issue_from_revision(revision)
    print(f'issue: {issue}')
    print(f'revision: {revision}')

    # connect to the database
    with database_impl.connect() as database:

      # bail if the dataset has already been acquired
      if database.contains_revision(revision):
        print('already have this revision, nothing to do')
        return False

      # add metadata to the database
      metadata_json = json.dumps(metadata)
      database.insert_metadata(issue, revision, metadata_json)

      # download the dataset and add it to the database
      # the date column needs to be reformatted as an int to match the table
      # definition
      dataset = network_impl.fetch_dataset(url)
      dataset['date'] = dataset['date'].apply(Update.get_date_as_int)
      database.insert_dataset(issue, dataset)

      print(f'successfully acquired {len(dataset)} rows')

      # note that the transaction is committed by exiting the `with` block
      return True


# main entry point
(Update.run if __name__ == '__main__' else lambda: None)()
