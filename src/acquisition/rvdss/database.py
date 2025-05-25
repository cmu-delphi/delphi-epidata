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

# standard library
import argparse
import numpy as np

# third party
import mysql.connector

# first party
from delphi.epidata.acquisition.rvdss import rvdss
import delphi.operations.secrets as secrets
from delphi.utils.epidate import EpiDate
import delphi.utils.epiweek as flu
from delphi.utils.geo.locations import Locations
from delphi_utils import get_structured_logger
from delphi.epidata.acquisition.rvdss.constants import LOGGER_FILENAME



respiratory_detections_cols= (
    "epiweek",
    "time_value",
    "issue",
    "geo_type",
    "geo_value",
    "sarscov2_tests",
    "sarscov2_positive_tests",
    "flu_tests",
    "flu_positive_tests",
    "fluah1n1pdm09_positive_tests",
    "fluah3_positive_tests",
    "fluauns_positive_tests",
    "flua_positive_tests",
    "flub_positive_tests",
    "rsv_tests",
    "rsv_positive_tests",
    "hpiv_tests",
    "hpiv1_positive_tests",
    "hpiv2_positive_tests",
    "hpiv3_positive_tests",
    "hpiv4_positive_tests",
    "hpivother_positive_tests",
    "adv_tests",
    "adv_positive_tests",
    "hmpv_tests",
    "hmpv_positive_tests",
    "evrv_tests",
    "evrv_positive_tests",
    "hcov_tests",
    "hcov_positive_tests",
    "week",
    "weekorder",
    "year"
)

pct_positive_cols = ( 
    "epiweek",
    "time_value",
    "issue",
    "geo_type",
    "geo_value",
    "evrv_pct_positive",
    "evrv_tests",
    "evrv_positive_tests",
    "hpiv_pct_positive",
    "hpiv_tests",
    "hpiv_positive_tests",
    "adv_pct_positive",
    "adv_tests",
    "hcov_pct_positive",
    "hcov_tests",
    "hcov_positive_tests",
    "flua_pct_positive",
    "flub_pct_positive",
    "flu_tests",
    "flua_positive_tests",
    "flua_tests",
    "flub_tests",
    "flub_positive_tests",
    "flu_positive_tests",
    "flu_pct_positive",
    "hmpv_pct_positive",
    "hmpv_tests",
    "hmpv_positive_tests",
    "rsv_pct_positive",
    "rsv_tests",
    "rsv_positive_tests",
    "sarscov2_pct_positive",
    "sarscov2_tests",
    "sarscov2_positive_tests",
    "region",
    "week",
    "weekorder",
    "year"
)

detections_counts_cols = (
    "epiweek",
    "time_value",
    "issue" ,
    "geo_type",
    "geo_value",
    "hpiv_positive_tests",
    "adv_positive_tests",
    "hmpv_positive_tests",
    "evrv_positive_tests",
    "hcov_positive_tests",
    "rsv_positive_tests",
    "flu_positive_tests"
)

expected_table_names = {
    "respiratory_detection":"rvdss_repiratory_detections",
    "positive":"rvdss_pct_positive" ,
    "count": "rvdss_detections_counts"
}

expected_columns = {
    "respiratory_detection":respiratory_detections_cols,
    "positive": pct_positive_cols,
    "count":detections_counts_cols
}

def get_num_rows(cursor, table_name):
    cursor.execute("SELECT count(1) `num` FROM `{table_name}`")
    for (num,) in cursor:
        pass
    return num

def update(data_dict,logger):
    # connect to the database
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(user=u, password=p, database="epidata")
    cur = cnx.cursor()
    
    # add filename for logger and exceptions
    
    logger = get_structured_logger(
            __name__,
            filename= LOGGER_FILENAME,
            log_exceptions=True,
        )

    for tt in data_dict.keys():
        data = data_dict[tt]
        data_tuples = list(data.itertuples(index=False,name=None))
        # loop though table types
        table_name = expected_table_names[tt]
        cols =  expected_columns[tt]
        place_holders= ', '.join(["?" for _ in cols])
        field_names = ", ".join(
                f"`{name}`" for name in cols)
        
        field_values = ", ".join(
                f"%({name})s" for name in cols)
        
        #check rvdss for new and/or revised data
        sql = f"""
        INSERT INTO {table_name} ({field_names})
        VALUES ({field_values})
        """
        
        # keep track of how many rows were added
        rows_before = get_num_rows(cur,table_name)
        total_rows = 0
        
        #insert data 
        cur.executemany(sql, data_tuples)
        
        # keep track of how many rows were added
        rows_after = get_num_rows(cur,table_name)
        logger.info(f"Inserted {int(rows_after - rows_before)}/{int(total_rows)} row(s) into table {table_name}")

    # cleanup
    cur.close()
    cnx.commit()
    cnx.close()
