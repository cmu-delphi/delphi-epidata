"""Computes and updates the `is_latest_issue` column in the `covidcast` table.

This update is only needed to be run once.
"""

# third party
import mysql.connector

# first party
import delphi.operations.secrets as secrets
from delphi.epidata.acquisition.covidcast.logger import get_structured_logger

# partition configuration
###PARTITION_VARIABLE = 'geo_value'
###PARTITION_SPLITS = ["'05101'", "'101'", "'13071'", "'15007'", "'17161'", "'19039'", "'20123'", "'21213'", "'24035'",
###                    "'27005'", "'28115'", "'29510'", "'31161'", "'35100'", "'37117'", "'39081'", "'41013'", "'44140'",
###                    "'47027'", "'48140'", "'48461'", "'51169'", "'55033'"]

PARTITION_VARIABLE = 'time_value'
PARTITION_SPLITS = [20200201 + i*100 for i in range(9)] # dates for the first of the month from feb - oct 2020

if sorted(PARTITION_SPLITS) != PARTITION_SPLITS:
  raise Exception('PARTITION_SPLITS not properly ordered!')

# filtering configuration
_FILTER_CONDITION = "TRUE" # this would indicate no filtering should be done
_FILTER_CONDITION = (
  "`time_type` = 'day'" # TODO: do we not care about issues on week-type data?
  " AND `source` = 'jhu-csse'" # for fixing is_latest on JHU data
)

_CLEAR_LATEST_BY_PARTITION = True


def main(*, CLEAR_LATEST_BY_PARTITION=_CLEAR_LATEST_BY_PARTITION, FILTER_CONDITION=_FILTER_CONDITION):


  logger = get_structured_logger(
      "fill_is_lastest_issue", log_exceptions=False)

  u, p = secrets.db.epi
  connection = mysql.connector.connect(
    host=secrets.db.host,
    user=u,
    password=p,
    database='epidata')
  cursor = connection.cursor()

  set_latest_query = '''
    UPDATE
    (
      SELECT
        `source`,
        `signal`,
        `time_type`,
        `geo_type`,
        `geo_value`,
        `time_value`,
        MAX(`issue`) AS `issue`
      FROM `covidcast`
      WHERE
        %s
      GROUP BY
        `source`,
        `signal`,
        `time_type`,
        `geo_type`,
        `geo_value`,
        `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`)
    SET `is_latest_issue`=1
    '''

  clear_latest_query = '''
    UPDATE `covidcast`
    SET `is_latest_issue` = 0
    WHERE %s;
  '''

  commit = False
  try:
    if not CLEAR_LATEST_BY_PARTITION:
      cursor.execute(clear_latest_query % FILTER_CONDITION)
    for partition_index in range(len(PARTITION_SPLITS)+1):
      # constructing the partition condition from partition index
      ge_condition = 'TRUE' if partition_index == 0 else \
      f'`{PARTITION_VARIABLE}` >= {PARTITION_SPLITS[partition_index - 1]}'
      l_condition = 'TRUE' if partition_index == len(PARTITION_SPLITS) else \
        f'`{PARTITION_VARIABLE}` < {PARTITION_SPLITS[partition_index]}'
      partition_condition = f'({FILTER_CONDITION}) AND ({ge_condition}) AND ({l_condition})'

      if CLEAR_LATEST_BY_PARTITION:
        cursor.execute(clear_latest_query % partition_condition)
      cursor.execute(set_latest_query % partition_condition)

      commit = True
  except Exception as e:
    connection.rollback()
    logger.exception("exception raised at partition %s (partition index #%s) of column `%s`" % (PARTITION_SPLITS[partition_index], partition_index, PARTITION_VARIABLE))
    raise e
  finally:
    cursor.close()
    if commit:
      connection.commit()
    connection.close()

if __name__=='__main__':
  main()
