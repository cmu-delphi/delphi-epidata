# run as:
#    python3 -u -m delphi.epidata.acquisition.covidcast.migrate_epidata_to_v4
# ("-u" allows unbuffered print statements so we can watch timing in closer-to-real-time)


#####import delphi.operations.secrets as secrets
#####secrets.db.host = '172.30.n.n' # aka 'epidata-db-qa-01'
#####secrets.db.epi = ('delphi', 'xxxxxxxx')
# ^ these are already set appropriately on qa-automation in/by the operations module ^


# TODO: make cli flags for these two variables:
use_transaction_wrappers = False
use_autocommit = False

# TODO: maybe output: was autocommit enabled?  was table locking used?  what isolation type was used?  were indexes enabled?  were uniqueness checks enabled?

# TODO: consider dropping indexes before moving data and recreating them afterward

'''

mysql> select count(id) from epidata.covidcast;
+------------+
| count(id)  |
+------------+
| 2647381579 |
+------------+
1 row in set (13 min 49.32 sec)

mysql> select max(id) from epidata.covidcast;
+------------+
| max(id)    |
+------------+
| 3740757041 |
+------------+
1 row in set (0.00 sec)

-- so ~71% coverage of actual rows per allocated ids ( 2647381579 / 3740757041 = .70771278379851347314 )

mysql> select time_value, issue from epidata.covidcast where id=3740757041;
+------------+----------+
| time_value | issue    |
+------------+----------+
|   20210927 | 20210930 |
+------------+----------+
1 row in set (0.01 sec)

mysql> select now();
+---------------------+
| now()               |
+---------------------+
| 2022-05-16 16:45:34 |
+---------------------+
1 row in set (0.00 sec)

'''


from delphi.epidata.acquisition.covidcast.database import Database
import time
import argparse

def start_tx(cursor):
  cursor.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;')
  cursor.execute('SET autocommit=0;') # starts a transaction as suggested in https://dev.mysql.com/doc/refman/8.0/en/lock-tables.html
  # NOTE: locks must be specified for any aliases of table names that are used
  cursor.execute('''LOCK TABLES epidata.covidcast AS cc READ,
                                epimetric_load WRITE, epimetric_load AS sl WRITE,
                                epimetric_full WRITE,
                                epimetric_latest WRITE,
                                signal_dim WRITE, signal_dim AS sd READ,
                                geo_dim WRITE, geo_dim AS gd READ;''')
  cursor.execute('SET unique_checks=0;')

def finish_tx(cursor):
  cursor.execute('SET unique_checks=1;')
  cursor.execute('COMMIT;')
  cursor.execute('UNLOCK TABLES;')


def do_batches(db, start, upper_lim, batch_size):
  # NOTE: upper_lim is not actually selected for ; make sure it exceeds any ids you want to include
  batch_lower = start

  while batch_lower < upper_lim:
    batch_upper = min(batch_lower + batch_size, upper_lim)

    # NOTE: first rows of column names are identical, second rows are for specifying a rename and a literal
    batch_sql = f"""
      INSERT INTO epimetric_load (
        `issue`, `source`, `signal`, geo_type, geo_value, time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp, is_latest_issue, missing_value, missing_stderr, missing_sample_size
      ) SELECT
        `issue`, `source`, `signal`, geo_type, geo_value, time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp, is_latest_issue, missing_value, missing_stderr, missing_sample_size
      FROM epidata.covidcast AS cc
      USE INDEX(`PRIMARY`)
      WHERE {batch_lower} <= cc.id AND cc.id < {batch_upper}; """
    # TODO: use LIMIT instead of id range??
    # TODO: might it be worth adding "ORDER BY id ASC" ?

    if use_transaction_wrappers:
      start_tx(db._cursor)

    print(f"-=-=-=-=-=-=-=- RUNNING BATCH STARTING AT {batch_lower} -=-=-=-=-=-=-=-")
    print(f"-=-=-=-=-=-=-=- RUNNING ''INSERT INTO SELECT FROM''... ", end="")
    t = time.time()
    db._cursor.execute(batch_sql)
    print(f"elapsed: {time.time()-t} sec, rows: {db._cursor.rowcount} -=-=-=-=-=-=-=-")

    t = time.time()
    db.run_dbjobs()
    print(f"-=-=-=-=-=-=-=- RAN db_jobs()... elapsed: {time.time()-t} sec -=-=-=-=-=-=-=-")

    print("-=-=-=-=-=-=-=- RUNNING commit()... ", end="")
    t = time.time()
    db.commit()
    if use_transaction_wrappers:
      finish_tx(db._cursor)
    print(f"elapsed: {time.time()-t} sec -=-=-=-=-=-=-=-")

    print("\n\n")
    # move pointer for next batch
    batch_lower = batch_upper


def main(destination_schema, batch_size, start_id, upper_lim_override):
  Database.DATABASE_NAME = destination_schema
  db = Database()
  db.connect()
  if use_autocommit:
    db._connection.autocommit = True

  if upper_lim_override:
    upper_lim = upper_lim_override
  else:
    # find upper limit for data to be imported
    db._cursor.execute("SELECT MAX(id) FROM epidata.covidcast;")
    for (max_id,) in db._cursor:
      upper_lim = 1 + max_id

  print(f"migrating data to schema '{destination_schema}', with batch size {batch_size} and {start_id} <= ids < {upper_lim}")
  if start_id==0:
    print("this WILL truncate any existing v4 tables")
  print()
  if input("type 'yes' to continue: ") != 'yes':
    import sys
    sys.exit('operation cancelled!')

  print(f"starting run at: {time.strftime('%c')}")

  if start_id==0:
    # clear tables in the v4 schema
    print("truncating tables...")
    for table in "epimetric_load  epimetric_latest  epimetric_full  geo_dim  signal_dim".split():
      db._cursor.execute(f"TRUNCATE TABLE {table}")
    db.commit()
    start_id = 1

  # run batch loop
  do_batches(db, start_id, upper_lim, batch_size)

  # get table counts [the quick and dirty way]
  print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
  db._cursor.execute(f"SELECT MAX(epimetric_id) FROM epimetric_full;")
  for (max_id,) in db._cursor:
    print(f"epimetric_full: {max_id}")
  db._cursor.execute(f"SELECT MAX(epimetric_id) FROM epimetric_latest;")
  for (max_id,) in db._cursor:
    print(f"epimetric_latest: {max_id} (this should be <= the number above)")
  db._cursor.execute(f"SELECT COUNT(signal_key_id), MAX(signal_key_id) FROM signal_dim;")
  for (count_id, max_id) in db._cursor:
    print(f"signal_dim: count {count_id} / max {max_id}")
  db._cursor.execute(f"SELECT COUNT(geo_key_id), MAX(geo_key_id) FROM geo_dim;")
  for (count_id, max_id) in db._cursor:
    print(f"geo_dim: count {count_id} / max {max_id}")

  return upper_lim


if __name__ == '__main__':
  argparser = argparse.ArgumentParser()
  argparser.add_argument('--destination_schema', type=str, default='covid')
  argparser.add_argument('--batch_size', type=int, default=20_000_000)
  argparser.add_argument('--start_id', type=int, default=0)
  argparser.add_argument('--upper_lim_override', type=int) # should default to None
  args = argparser.parse_args()

  upper_lim = main(args.destination_schema, args.batch_size, args.start_id, args.upper_lim_override)
  print(f"the next execution of this program should include argument: --start_id={upper_lim}")
