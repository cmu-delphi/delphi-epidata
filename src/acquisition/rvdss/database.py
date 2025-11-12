"""
===============
=== Purpose ===
===============

Stores data provided by rvdss Corp., which contains flu lab test results.
See: rvdss.py


=======================
=== Data Dictionary ===
=======================

`rvdss` is the table where rvdss data is stored.
"""

# standard libraries

# third party
import mysql.connector

# first party
from delphi.epidata.acquisition.rvdss import rvdss
import delphi.operations.secrets as secrets


rvdss_cols= (
  "epiweek",
  "time_value",
  "issue",
  "geo_type",
  "geo_value",
  "sarscov2_tests",
  "sarscov2_positive_tests",
  "sarscov2_pct_positive",
  "flu_tests",
  "flu_positive_tests",
  "flu_pct_positive",
  "fluah1n1pdm09_positive_tests",
  "fluah3_positive_tests",
  "fluauns_positive_tests",
  "flua_positive_tests",
  "flua_tests",
  "flua_pct_positive",
  "flub_positive_tests",
  "flub_tests",
  "flub_pct_positive",
  "rsv_tests",
  "rsv_positive_tests",
  "rsv_pct_positive",
  "hpiv_tests",
  "hpiv1_positive_tests",
  "hpiv2_positive_tests",
  "hpiv3_positive_tests",
  "hpiv4_positive_tests",
  "hpivother_positive_tests",
  "hpiv_positive_tests",
  "hpiv_pct_positive",
  "adv_tests",
  "adv_positive_tests",
  "adv_pct_positive",
  "hmpv_tests",
  "hmpv_positive_tests",
  "hmpv_pct_positive",
  "evrv_tests",
  "evrv_positive_tests",
  "evrv_pct_positive",
  "hcov_tests",
  "hcov_positive_tests",
  "hcov_pct_positive",
  "year",
  "region"
)

def get_num_rows(cursor):
    cursor.execute("SELECT count(1) `num` FROM `rvdss`")
    for (num,) in cursor:
        pass
    return num

def update(data,logger):
    # connect to the database
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(user=u, password=p, database="epidata")
    cur = cnx.cursor()
    

    data_tuples = list(data.itertuples(index=False,name=None))
    
    rvdss_cols_subset = [col for col in rvdss_cols if col in data.columns]
    field_names = ", ".join(f"`{name}`" for name in rvdss_cols_subset)
    field_values = ", ".join(f"%({name})s" for name in rvdss_cols_subset)
        
    #check rvdss for new and/or revised data
    sql = f"""
    INSERT INTO rvdss ({field_names})
    VALUES ({field_values})
    """
        
    # keep track of how many rows were added
    rows_before = get_num_rows(cur)
    total_rows = 0
        
    #insert data 
    cur.executemany(sql, data_tuples)
        
    # keep track of how many rows were added
    rows_after = get_num_rows(cur)
    logger.info(f"Inserted {int(rows_after - rows_before)}/{int(total_rows)} row(s) into table rvdss")
    
    # cleanup
    cur.close()
    cnx.commit()
    cnx.close()
