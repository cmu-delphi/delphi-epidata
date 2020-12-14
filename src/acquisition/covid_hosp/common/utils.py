"""Code shared among multiple `covid_hosp` scrapers."""

# standard library
import json
import re


class CovidHospException(Exception):
  """Exception raised exclusively by `covid_hosp` utilities."""


class Utils:

  # regex to extract issue date from revision field
  # example revision: "Mon, 11/16/2020 - 00:55"
  REVISION_PATTERN = re.compile(r'^.*\s(\d+)/(\d+)/(\d+)\s.*$')

  def launch_if_main(entrypoint, runtime_name):
    """Call the given function in the main entry point, otherwise no-op."""

    if runtime_name == '__main__':
      entrypoint()

  def int_from_date(date):
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
    CovidHospException
      If the field can't be found.
    """

    try:
      for elem in path:
        is_index = isinstance(elem, int)
        is_list = isinstance(obj, list)
        if is_index != is_list:
          raise CovidHospException('index given for non-list or vice versa')
        obj = obj[elem]
      return obj
    except Exception as ex:
      path_str = '/'.join(map(str, path))
      msg = f'unable to access object path "/{path_str}"'
      raise CovidHospException(msg) from ex

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
    CovidHospException
      If the issue can't be extracted.
    """

    match = Utils.REVISION_PATTERN.match(revision)
    if not match:
      raise CovidHospException(f'unable to extract issue from "{revision}"')
    y, m, d = match.group(3), match.group(1), match.group(2)
    return int(y) * 10000 + int(m) * 100 + int(d)

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
    CovidHospException
      If the metadata does not match the expected format.
    """

    # check data integrity
    if Utils.get_entry(metadata, 'success') is not True:
      raise CovidHospException(
          'metadata does not have `success` equal to `True`')
    if len(Utils.get_entry(metadata, 'result')) != 1:
      raise CovidHospException('metadata does not have exactly 1 result')
    if len(Utils.get_entry(metadata, 'result', 0, 'resources')) != 1:
      raise CovidHospException('metadata does not have exactly 1 resource')

    # return resource details
    resource = Utils.get_entry(metadata, 'result', 0, 'resources', 0)
    return resource['url'], resource['revision_timestamp']

  def update_dataset(database, network):
    """Acquire the most recent dataset, unless it was previously acquired.

    Parameters
    ----------
    database : delphi.epidata.acquisition.covid_hosp.common.database.Database
      A `Database` subclass for a particular dataset.
    network : delphi.epidata.acquisition.covid_hosp.common.network.Network
      A `Network` subclass for a particular dataset.

    Returns
    -------
    bool
      Whether a new dataset was acquired.
    """

    # get dataset details from metadata
    metadata = network.fetch_metadata()
    url, revision = Utils.extract_resource_details(metadata)
    issue = Utils.get_issue_from_revision(revision)
    print(f'issue: {issue}')
    print(f'revision: {revision}')

    # connect to the database
    with database.connect() as db:

      # bail if the dataset has already been acquired
      if db.contains_revision(revision):
        print('already have this revision, nothing to do')
        return False

      # add metadata to the database
      metadata_json = json.dumps(metadata)
      db.insert_metadata(issue, revision, metadata_json)

      # download the dataset and add it to the database
      dataset = network.fetch_dataset(url)
      db.insert_dataset(issue, dataset)

      print(f'successfully acquired {len(dataset)} rows')

      # note that the transaction is committed by exiting the `with` block
      return True
