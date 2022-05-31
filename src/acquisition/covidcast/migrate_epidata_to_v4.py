# run as:
#    python3 -u -m delphi.epidata.acquisition.covidcast.migrate_epidata_to_v4
# ("-u" allows unbuffered print statements so we can watch timing in closer-to-real-time)


#####import delphi.operations.secrets as secrets
#####secrets.db.host = '172.30.n.n' # aka 'epidata-db-qa-01'
#####secrets.db.epi = ('delphi', 'xxxxxxxx')
# ^ these are already set appropriately on qa-automation in/by the operations module ^


batch_size = 20_000_000
upper_lim_override = False ##### 60_000_000
use_transaction_wrappers = False
use_autocommit = False

# used to continue to experiment with this module on the same DBMS but *not* muck up an already complete and valid 'covid' schema migration
destination_schema = 'covid' ##### 'covid'

# TODO: maybe output: was autocommit enabled?  was table locking used?  what isolation type was used?  were indexes enabled?  were uniqueness checks enabled?
# TODO: make cli flags for various things listed in "outputs" suggestions above, plus: starting id, id upper limit (which id to stop at), batch size, and dbjobs "version"



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

def start_tx(cursor):
  cursor.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;')
  cursor.execute('SET autocommit=0;') # starts a transaction as suggested in https://dev.mysql.com/doc/refman/8.0/en/lock-tables.html
  # NOTE: locks must be specified for any aliases of table names that are used
  cursor.execute('''LOCK TABLES epidata.covidcast AS cc READ,
                                signal_load WRITE, signal_load AS sl WRITE,
                                signal_history WRITE,
                                signal_latest WRITE,
                                signal_dim WRITE, signal_dim AS sd READ,
                                geo_dim WRITE, geo_dim AS gd READ;''')
  cursor.execute('SET unique_checks=0;')

def finish_tx(cursor):
  cursor.execute('SET unique_checks=1;')
  cursor.execute('COMMIT;')
  cursor.execute('UNLOCK TABLES;')


def do_batches(db, start, upper_lim):
  # NOTE: upper_lim is not actually selected for ; make sure it exceeds any ids you want to include
  batch_lower = start

  while batch_lower < upper_lim:
    batch_upper = min(batch_lower + batch_size, upper_lim)

    # NOTE: first rows of column names are identical, second rows are for specifying a rename and a literal
    batch_sql = f"""
      INSERT INTO {destination_schema}.signal_load (
        `issue`, `source`, `signal`, geo_type, geo_value, time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp, is_latest_issue, missing_value, missing_stderr, missing_sample_size,
        `legacy_id`, process_status
      ) SELECT
        `issue`, `source`, `signal`, geo_type, geo_value, time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp, is_latest_issue, missing_value, missing_stderr, missing_sample_size,
        `id`, 'l'
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
    #####db.run_dbjobs_old()
    #####print(f"-=-=-=-=-=-=-=- RAN db_jobs_old()... elapsed: {time.time()-t} sec -=-=-=-=-=-=-=-")

    print("-=-=-=-=-=-=-=- RUNNING commit()... ", end="")
    t = time.time()
    db.commit()
    if use_transaction_wrappers:
      finish_tx(db._cursor)
    print(f"elapsed: {time.time()-t} sec -=-=-=-=-=-=-=-")

    print("\n\n")
    # move pointer for next batch
    batch_lower = batch_upper


def main():
  Database.DATABASE_NAME = destination_schema
  db = Database()
  db.connect()
  if use_autocommit:
    db._connection.autocommit = True

  print(f"starting run at: {time.strftime('%c')}")

  # clear tables in the v4 schema
  # TODO: potentially drop and recreate all tables
  print("truncating tables...")
  for table in "signal_load  signal_latest  signal_history  geo_dim  signal_dim".split():
    db._cursor.execute(f"TRUNCATE TABLE {table}")
  db.commit()

  # TODO: if using "compressed" keys, this operation saves a significant amount of time...  dont forget to restore them afterward!
  #####db._cursor.execute(f"DROP INDEX comp_signal_key ON {destination_schema}.signal_load")
  #####db._cursor.execute(f"DROP INDEX comp_geo_key ON {destination_schema}.signal_load")
  #####db.commit()
  # TODO: should we drop indexes on other tables?  this may not save time in the long run, as the indexes must be rebuilt before going live

  if upper_lim_override:
    upper_lim = upper_lim_override
  else:
    # find upper limit for data to be imported
    db._cursor.execute("SELECT MAX(id) FROM epidata.covidcast;")
    for (max_id,) in db._cursor:
      upper_lim = 1 + max_id

  # run batch loop
  do_batches(db, 1, upper_lim)

  # get table counts [the quick and dirty way]
  print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
  db._cursor.execute(f"SELECT MAX(signal_data_id) FROM {destination_schema}.signal_history;")
  for (max_id,) in db._cursor:
    print(f"signal_history: {max_id}")
  db._cursor.execute(f"SELECT MAX(signal_data_id) FROM {destination_schema}.signal_latest;")
  for (max_id,) in db._cursor:
    print(f"signal_latest: {max_id}")
  db._cursor.execute(f"SELECT COUNT(signal_key_id), MAX(signal_key_id) FROM {destination_schema}.signal_dim;")
  for (count_id, max_id) in db._cursor:
    print(f"signal_dim: {count_id}/{max_id}")
  db._cursor.execute(f"SELECT COUNT(geo_key_id), MAX(geo_key_id) FROM {destination_schema}.geo_dim;")
  for (count_id, max_id) in db._cursor:
    print(f"geo_dim: {count_id}/{max_id}")


if __name__ == '__main__':
  main()
