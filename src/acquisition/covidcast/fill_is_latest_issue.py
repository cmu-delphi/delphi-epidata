"""Computes and updates the `is_latest_issue` column in the `covidcast` table.

This update is only needed to be run once.
"""

# third party
import mysql.connector

# first party
import delphi.operations.secrets as secrets


# partition configuration
PARTITION_VARIABLE = 'geo_value'
PARTITION_SPLITS = ["'05101'", "'101'", "'13071'", "'15007'", "'17161'", "'19039'", "'20123'", "'21213'", "'24035'",
                    "'27005'", "'28115'", "'29510'", "'31161'", "'35100'", "'37117'", "'39081'", "'41013'", "'44140'",
                    "'47027'", "'48140'", "'48461'", "'51169'", "'55033'"]

def main():

  u, p = secrets.db.epi
  connection = mysql.connector.connect(
    host=secrets.db.host,
    user=u,
    password=p,
    database='epidata')
  cursor = connection.cursor()

  set_partition_to_one_query = '''
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
        `time_type` = 'day' AND
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

  set_to_zero_query = '''
    UPDATE `covidcast`
    SET `is_latest_issue` = 0;
  '''

  commit = False
  try:
    cursor.execute(set_to_zero_query)
    for partition_index in range(24):
      # constructing the partitoin condition from partition index
      ge_condition = 'TRUE' if partition_index == 0 else \
      f'`{PARTITION_VARIABLE}` >= {PARTITION_SPLITS[partition_index - 1]}'
      l_condition = 'TRUE' if partition_index == len(PARTITION_SPLITS) else \
        f'`{PARTITION_VARIABLE}` < {PARTITION_SPLITS[partition_index]}'
      partition_condition = f'({ge_condition}) AND ({l_condition})'

      cursor.execute(set_partition_to_one_query % partition_condition)

      commit = True
  except Exception as e:
    connection.rollback()
    raise e
  finally:
    cursor.close()
    if commit:
      connection.commit()
    connection.close()

if __name__=='__main__':
  main()