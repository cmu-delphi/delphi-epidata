def update(table_key= '', first=None, last=None, force_update=False, load_email=True):

    table_name = expected_table_names[table_key]
    field_names = ", ".join(
            f"`{name}`" for name in expected_columns[table_key])
    
    field_values = ", ".join(
           f"%({name})s" for name in expected_columns[table_key])
    # check rvdss for new and/or revised data
    sql = f"""
    INSERT INTO {table_name} ({field_names})
    VALUES ({field_values})
    ON DUPLICATE KEY UPDATE
      `value` = %s
    """
    print(sql)

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

update("count")
update("positive")
update("respiratory_detection")

import pandas as pd

data = pd.read_csv("positive_tests.csv")
b = list(data.itertuples(index=False,name=None))
