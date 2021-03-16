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

  def parse_bool(value):
    """Convert a string to a boolean.

    Parameters
    ----------
    value : str
      Boolean-like value, like "true" or "false".

    Returns
    -------
    bool
      If the string contains some version of "true" or "false".
    None
      If the string is None or empty.

    Raises
    ------
    CovidHospException
      If the string constains something other than a version of "true" or
      "false".
    """

    if not value:
      return None
    if value.lower() == 'true':
      return True
    if value.lower() == 'false':
      return False
    raise CovidHospException(f'cannot convert "{value}" to bool')

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
    issue = max(metadata.index)
    revision = metadata.loc[issue, "Archive Link"]
    print(f'issue: {issue}')
    print(f'revision: {revision}')

    # connect to the database
    with database.connect() as db:

      # bail if the dataset has already been acquired
      if db.contains_revision(revision):
        print('already have this revision, nothing to do')
        return False

      # add metadata to the database
      metadata_json = metadata.loc[issue].to_json()
      issue_int = int(issue.strftime("%Y%m%d"))
      db.insert_metadata(issue_int, revision, metadata_json)

      # download the dataset and add it to the database
      dataset = network.fetch_dataset(metadata.loc[issue, "Archive Link"])
      db.insert_dataset(issue_int, dataset)

      print(f'successfully acquired {len(dataset)} rows')

      # note that the transaction is committed by exiting the `with` block
      return True
