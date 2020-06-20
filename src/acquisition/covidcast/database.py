"""A utility class that handles database operations related to covidcast.

See src/ddl/covidcast.sql for an explanation of each field.
"""

# third party
import mysql.connector

# first party
import delphi.operations.secrets as secrets


class Database:
  """A collection of covidcast database operations."""

  DATABASE_NAME = 'epidata'

  def connect(self, connector_impl=mysql.connector):
    """Establish a connection to the database."""

    u, p = secrets.db.epi
    self._connection = connector_impl.connect(
        host=secrets.db.host,
        user=u,
        password=p,
        database=Database.DATABASE_NAME)
    self._cursor = self._connection.cursor()

  def disconnect(self, commit):
    """Close the database connection.

    commit: if true, commit changes, otherwise rollback
    """

    self._cursor.close()
    if commit:
      self._connection.commit()
    self._connection.close()

  def count_all_rows(self):
    """Return the total number of rows in table `covidcast`."""

    self._cursor.execute('SELECT count(1) FROM `covidcast`')

    for (num,) in self._cursor:
      return num

  def insert_or_update(
      self,
      source,
      signal,
      time_type,
      geo_type,
      time_value,
      geo_value,
      value,
      stderr,
      sample_size):
    """
    Insert a new row, or update an existing row, in the `covidcast` table.

    This has the intentional side effect of updating the primary timestamp.
    """

    sql = '''
      INSERT INTO `covidcast` VALUES
        (0, %s, %s, %s, %s, %s, %s, UNIX_TIMESTAMP(NOW()), %s, %s, %s, 0, NULL)
      ON DUPLICATE KEY UPDATE
        `timestamp1` = VALUES(`timestamp1`),
        `value` = VALUES(`value`),
        `stderr` = VALUES(`stderr`),
        `sample_size` = VALUES(`sample_size`)
    '''

    args = (
      source,
      signal,
      time_type,
      geo_type,
      time_value,
      geo_value,
      value,
      stderr,
      sample_size,
    )

    self._cursor.execute(sql, args)

  def get_data_stdev_across_locations(self, max_day):
    """
    Return the standard deviation of daily data over all locations, for all
    (source, signal, geo_type) tuples.

    `max_day`: base the standard deviation on data up to, and including, but
      not after, this day (e.g. for a stable result over time)
    """

    sql = '''
      SELECT
        `source`,
        `signal`,
        `geo_type`,
        COALESCE(STD(`value`), 0) AS `aggregate_stdev`
      FROM
        `covidcast`
      WHERE
        `time_type` = 'day' AND
        `time_value` <= %s
      GROUP BY
        `source`,
        `signal`,
        `geo_type`
    '''

    args = (max_day,)
    self._cursor.execute(sql, args)
    return list(self._cursor)

  def update_direction(
      self,
      source,
      signal,
      time_type,
      geo_type,
      time_value,
      geo_value,
      direction):
    """
    Update the `direction` column for a given row in the `covidcast` table.

    This has the intentional side effect of updating the secondary timestamp.
    """

    sql = '''
      UPDATE
        `covidcast`
      SET
        `timestamp2` = UNIX_TIMESTAMP(NOW()),
        `direction` = %s
      WHERE
        `source` = %s AND
        `signal` = %s AND
        `time_type` = %s AND
        `geo_type` = %s AND
        `time_value` = %s AND
        `geo_value` = %s
    '''

    args = (
      direction,
      source,
      signal,
      time_type,
      geo_type,
      time_value,
      geo_value,
    )

    self._cursor.execute(sql, args)

  def get_keys_with_potentially_stale_direction(self):
    """
    Return the `covidcast` table composite key for each unique time-series for
    which all `direction` values can not be guaranteed to be fresh.

    Note that this is limited to `time_type` of 'day' as direction is not yet
    defined at other time scales.
    """

    sql = '''
      SELECT
        `source`,
        `signal`,
        `geo_type`,
        `geo_value`,
        MAX(`timestamp1`) AS `max_timestamp1`,
        MIN(`timestamp2`) AS `min_timestamp2`,
        MIN(`time_value`) AS `min_day`,
        MAX(`time_value`) AS `max_day`,
        COUNT(1) AS `series_length`
      FROM
        `covidcast`
      WHERE
        `time_type` = 'day'
      GROUP BY
        `source`,
        `signal`,
        `time_type`,
        `geo_type`,
        `geo_value`
      HAVING
        MAX(`timestamp1`) > MIN(`timestamp2`)
    '''

    self._cursor.execute(sql)
    return list(self._cursor)

  def get_daily_timeseries_for_direction_update(
      self, source, signal, geo_type, geo_value, min_day, max_day):
    """Return the indicated `covidcast` time-series, including timestamps."""

    sql = '''
      SELECT
        DATEDIFF(`time_value`, %s) AS `offset`,
        `time_value` AS `day`,
        `value`,
        `timestamp1`,
        `timestamp2`
      FROM
        `covidcast`
      WHERE
        `source` = %s AND
        `signal` = %s AND
        `time_type` = 'day' AND
        `geo_type` = %s AND
        `geo_value` = %s AND
        `time_value` BETWEEN %s AND %s
      ORDER BY
        `time_value` ASC
    '''

    args = (min_day, source, signal, geo_type, geo_value, min_day, max_day)
    self._cursor.execute(sql, args)
    return list(self._cursor)

  def update_timeseries_timestamp2(
      self, source, signal, time_type, geo_type, geo_value):
    """Update the `timestamp2` column for an entire time-series.

    For daily time-series, this implies that all `direction` values in the
    specified time-series are confirmed fresh as of the current time. Even if
    they happened to be computed at an earlier time, this update indicates that
    those values are still fresh.

    This has no meaningful implication for non-daily time-series.
    """

    sql = '''
      UPDATE
        `covidcast`
      SET
        `timestamp2` = UNIX_TIMESTAMP(NOW())
      WHERE
        `source` = %s AND
        `signal` = %s AND
        `time_type` = %s AND
        `geo_type` = %s AND
        `geo_value` = %s
    '''

    args = (source, signal, time_type, geo_type, geo_value)
    self._cursor.execute(sql, args)

  def get_covidcast_meta(self):
    """Compute and return metadata on all non-WIP COVIDcast signals."""

    sql = '''
      SELECT
        t.`source` AS `data_source`,
        t.`signal`,
        t.`time_type`,
        t.`geo_type`,
        MIN(t.`time_value`) AS `min_time`,
        MAX(t.`time_value`) AS `max_time`,
        COUNT(DISTINCT t.`geo_value`) AS `num_locations`,
        MIN(`value`) AS `min_value`,
        MAX(`value`) AS `max_value`,
        AVG(`value`) AS `mean_value`,
        STD(`value`) AS `stdev_value`,
        MAX(`timestamp1`) AS `last_update`
      FROM
        `covidcast` t
      WHERE
        t.`signal` NOT LIKE 'wip_%'
      GROUP BY
        t.`source`,
        t.`signal`,
        t.`time_type`,
        t.`geo_type`
      ORDER BY
        t.`source` ASC,
        t.`signal` ASC,
        t.`time_type` ASC,
        t.`geo_type` ASC
'''
    FIELDS="data_source signal time_type geo_type min_time max_time num_locations min_value max_value mean_value stdev_value last_update".split()
    self._cursor.execute(sql)
    return list(dict(zip(FIELDS,x)) for x in self._cursor)

  def update_covidcast_meta_cache(self, epidata_json):
    """Updates the `covidcast_meta_cache` table."""

    sql = '''
      UPDATE
        `covidcast_meta_cache`
      SET
        `timestamp` = UNIX_TIMESTAMP(NOW()),
        `epidata` = %s
    '''

    self._cursor.execute(sql, (epidata_json,))
