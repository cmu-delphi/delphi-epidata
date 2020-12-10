# standard library
from contextlib import contextmanager
import math

# third party
import mysql.connector

# first party
import delphi.operations.secrets as secrets


class Database:

  # These are the names that appear in the CSV header, in order of appeareance
  # in the database table. However, note that the corresponding database column
  # names may be shorter due to constraints on the length of column names. See
  # /src/ddl/covid_hosp.sql for more information.
  ORDERED_CSV_COLUMNS = [
    'state',
    'date',
    'hospital_onset_covid',
    'hospital_onset_covid_coverage',
    'inpatient_beds',
    'inpatient_beds_coverage',
    'inpatient_beds_used',
    'inpatient_beds_used_coverage',
    'inpatient_beds_used_covid',
    'inpatient_beds_used_covid_coverage',
    'previous_day_admission_adult_covid_confirmed',
    'previous_day_admission_adult_covid_confirmed_coverage',
    'previous_day_admission_adult_covid_suspected',
    'previous_day_admission_adult_covid_suspected_coverage',
    'previous_day_admission_pediatric_covid_confirmed',
    'previous_day_admission_pediatric_covid_confirmed_coverage',
    'previous_day_admission_pediatric_covid_suspected',
    'previous_day_admission_pediatric_covid_suspected_coverage',
    'staffed_adult_icu_bed_occupancy',
    'staffed_adult_icu_bed_occupancy_coverage',
    'staffed_icu_adult_patients_confirmed_and_suspected_covid',
    'staffed_icu_adult_patients_confirmed_and_suspected_covid_coverage',
    'staffed_icu_adult_patients_confirmed_covid',
    'staffed_icu_adult_patients_confirmed_covid_coverage',
    'total_adult_patients_hospitalized_confirmed_and_suspected_covid',
    'total_adult_patients_hospitalized_confirmed_and_suspected_covid_coverage',
    'total_adult_patients_hospitalized_confirmed_covid',
    'total_adult_patients_hospitalized_confirmed_covid_coverage',
    'total_pediatric_patients_hospitalized_confirmed_and_suspected_covid',
    'total_pediatric_patients_hospitalized_confirmed_and_suspected_covid_coverage',
    'total_pediatric_patients_hospitalized_confirmed_covid',
    'total_pediatric_patients_hospitalized_confirmed_covid_coverage',
    'total_staffed_adult_icu_beds',
    'total_staffed_adult_icu_beds_coverage',
    'inpatient_beds_utilization',
    'inpatient_beds_utilization_coverage',
    'inpatient_beds_utilization_numerator',
    'inpatient_beds_utilization_denominator',
    'percent_of_inpatients_with_covid',
    'percent_of_inpatients_with_covid_coverage',
    'percent_of_inpatients_with_covid_numerator',
    'percent_of_inpatients_with_covid_denominator',
    'inpatient_bed_covid_utilization',
    'inpatient_bed_covid_utilization_coverage',
    'inpatient_bed_covid_utilization_numerator',
    'inpatient_bed_covid_utilization_denominator',
    'adult_icu_bed_covid_utilization',
    'adult_icu_bed_covid_utilization_coverage',
    'adult_icu_bed_covid_utilization_numerator',
    'adult_icu_bed_covid_utilization_denominator',
    'adult_icu_bed_utilization',
    'adult_icu_bed_utilization_coverage',
    'adult_icu_bed_utilization_numerator',
    'adult_icu_bed_utilization_denominator',
  ]

  def __init__(self, connection):
    """Create a new Database object.

    Parameters
    ----------
    connection
      An open connection to a database.
    """

    self.connection = connection

  @contextmanager
  def connect(mysql_connector_impl=mysql.connector):
    """Connect to a database and provide the connection as a context manager.

    As long as the context manager exits normally, the connection's transaction
    will be committed. Otherwise, if the context is exited by an Exception, the
    transaction will be rolled back.

    In any case, the connection will be gracefully closed upon exiting the
    context manager.
    """

    # connect to the database
    user, password = secrets.db.epi
    connection = mysql_connector_impl.connect(
        host=secrets.db.host,
        user=user,
        password=password,
        database='epidata')

    try:
      # provide the connection to the context manager
      yield Database(connection)

      # rollback by default; the following commit will only take place if no
      # exception was raised in calling code
      connection.commit()
    finally:
      # close the connection in any case
      connection.close()

  @contextmanager
  def new_cursor(self):
    """Create and provide a database cursor as a context manager.

    The cursor will be gracefully closed upon exiting the context manager.
    """

    cursor = self.connection.cursor()
    try:
      yield cursor
    finally:
      cursor.close()

  def contains_revision(self, revision):
    """Return whether the given revision already exists in the database.

    Parameters
    ----------
    revision : str
      Unique revision string.

    Returns
    -------
    bool
      True iff the revision already exists.
    """

    with self.new_cursor() as cursor:
      cursor.execute('''
        SELECT
          count(1) > 0
        FROM
          `covid_hosp_meta`
        WHERE
          `revision_timestamp` = %s
      ''', (revision,))
      for (result,) in cursor:
        return bool(result)

  def insert_metadata(self, issue, revision, meta_json):
    """Add revision metadata to the database.

    Parameters
    ----------
    issue : int
      Issue of the dataset in YYYYMMDD format.
    revision : str
      Unique revision string.
    meta_json : str
      Metadata serialized as a JSON string.
    """

    with self.new_cursor() as cursor:
      cursor.execute('''
        INSERT INTO
          `covid_hosp_meta` (
            `issue`,
            `revision_timestamp`,
            `metadata_json`,
            `acquisition_datetime`
          )
        VALUES
          (%s, %s, %s, NOW())
      ''', (issue, revision, meta_json))

  def insert_dataset(self, issue, dataframe):
    """Add revision metadata to the database.

    Parameters
    ----------
    issue : int
      Issue of the dataset in YYYYMMDD format.
    dataframe : pandas.DataFrame
      The dataset.
    """

    # the database requires `nan` to be converted to `None` for `NULL` values
    dataframe = dataframe.replace({math.nan: None})

    num_columns = 2 + len(Database.ORDERED_CSV_COLUMNS)
    value_placeholders = ', '.join(['%s'] * num_columns)
    sql = f'''
      INSERT INTO
        `covid_hosp`
      VALUES
        ({value_placeholders})
    '''

    id_and_issue = (0, issue)
    with self.new_cursor() as cursor:
      for _, row in dataframe.iterrows():
        values = tuple(row[name] for name in Database.ORDERED_CSV_COLUMNS)
        cursor.execute(sql, id_and_issue + values)
