#!/usr/bin/env python3
import pandas as pd
from delphi_utils.logger import get_structured_logger
from logging import Logger
from delphi.epidata.acquisition.wastewater.database import Database

df_tiny = pd.DataFrame()

# todo remove, temp for development
logger = get_structured_logger("csv_ingestion", filename="writingErrorLog")

database = Database(logger, execute=True)
df_tiny.dtypes
df_old = df_tiny.copy()
df_old.version = (pd.Timestamp("today") - pd.Timedelta("7 days")).normalize()
with pd.option_context(
    "display.max_rows", None, "display.max_columns", 700, "display.width", 181
):
    print(df_old.sort_values("wwtp_id"))
    print(df_tiny.sort_values("wwtp_id"))
database.read_table("wastewater_granular_load")
database.read_table("signal_dim")
database.read_table("plant_dim").sort_values("wwtp_id")
database.read_table("sample_site_dim")
database.read_table("wastewater_granular_full")
database.read_table("wastewater_granular_latest")
database.read_table("wastewater_granular_latest_v")
with pd.option_context(
    "display.max_rows", None, "display.max_columns", 700, "display.width", 181
):
    print(database.read_table("wastewater_granular_full"))
    print(database.read_table("wastewater_granular_latest_v"))
    print(database.read_table("wastewater_granular_load"))
database.read_table("wastewater_granular_latest")
database.load_DataFrame(df_tiny)
test_read = """
        SELECT
          lt.`wastewater_id`, sd.`signal_key_id`, ssd.`site_key_id`, sd.`source`, sd.`signal`, sd.`pathogen`, sd.`provider`, sd.`normalization`, pd.`wwtp_jurisdiction`, pd.`wwtp_id`, ssd.`sample_loc_specify`, ssd.`sample_method`
        FROM `wastewater_granular_load` lt
            INNER JOIN signal_dim sd USING (`source`, `signal`, `pathogen`, `provider`, `normalization`)
            INNER JOIN sample_site_dim ssd USING (`sample_loc_specify`, `sample_method`)
            INNER JOIN plant_dim pd ON pd.`wwtp_jurisdiction`=lt.`wwtp_jurisdiction` AND pd.`wwtp_id`=lt.`wwtp_id` AND pd.`plant_id`=ssd.`plant_id`
"""
test_read = """
SELECT * FROM `wastewater_granular_load` load_table
LEFT JOIN `wastewater_granular_latest_v` USING
(`signal_key_id`, `site_key_id`, `reference_date`)
"""
res = 3
with database.engine.connect() as conn:
    res = conn.execute(text(test_read))
    with pd.option_context(
        "display.max_rows", None, "display.max_columns", 700, "display.width", 181
    ):
        print(pd.DataFrame(res))

database.standard_run(df_old)
with pd.option_context(
    "display.max_rows", None, "display.max_columns", 700, "display.width", 181
):
    print(database.read_table("wastewater_granular_load"))
database.read_table("signal_dim")
database.read_table("plant_dim").sort_values("wwtp_id")
database.read_table("sample_site_dim")
database.read_table("wastewater_granular_load").transpose()
database.read_table("wastewater_granular_latest").transpose()
with pd.option_context(
    "display.max_rows", None, "display.max_columns", 700, "display.width", 181
):
    print(database.read_table("wastewater_granular_latest"))
with pd.option_context(
    "display.max_rows", None, "display.max_columns", 700, "display.width", 181
):
    print(database.read_table("wastewater_granular_latest_v"))
database.load_DataFrame(df_tiny)
database.load_DataFrame(df_old)
database.read_table("signal_dim")
database.read_table("wastewater_granular_full").transpose()
database.read_table("sample_site_dim")
database.read_table("wastewater_granular_load")
database.add_new_from_load("signal_dim", database.signal_values, "signal_key_id")
print(database.add_new_from_load("plant_dim", database.plant_values, None))
print(
    database.add_new_from_load(
        "sample_site_dim",
        database.sample_site_values,
        key="site_key_id",
        foreign_table="plant_dim",
        foreign_keys=["plant_id"],
        shared_values=database.plant_values,
        execute=True,
    )
)
print(database.delete_redundant())
print(database.set_latest_flag())
print(database.add_full_latest(database.full_table))
print(database.add_full_latest(database.latest_table))
database.delete_load()
database.add_full_latest(database.full_table)
database.add_full_latest(database.latest_table)
database.load_DataFrame(df_tiny)
load_table = database.read_table("wastewater_granular_load")
load_table.dtypes
database.delete_redundant()
database
database.read_table("wastewater_granular_load")
database.set_latest_flag()
database.read_table("wastewater_granular_load")
# test that add_new_load is idempotent
# test that it adds the correct features
print(database.add_new_from_load("signal_dim", database.signal_values, "source"))
database.read_table("signal_dim")
print(database.add_new_from_load("plant_dim", database.plant_values, "wwtp_id"))
database.read_table("plant_dim")
print(
    database.add_new_from_load(
        "sample_site_dim",
        database.sample_site_values,
        "sample_method",
        foreign_table="plant_dim",
        foreign_keys=["plant_id"],
        shared_values=database.plant_values,
        execute=True,
    )
)
database.read_table("sample_site_dim")
database.add_full_latest(database.full_table)
database.read_table(database.full_table)
database.read_table(database.latest_table)
database.delete_load()


"\n".join([f"{x} = lt.{x}," for x in database.full_table_meta])
load_table = "`wastewater_granular_load`"
latest_view = "`wastewater_granular_latest_v`"
sample_site_values = add_backticks(["sample_loc_specify", "sample_method"])
plant_values = add_backticks(["wwtp_jurisdiction", "wwtp_id"])
signal_values = add_backticks(
    ["source", "signal", "pathogen", "provider", "normalization"]
)
full_table_index = add_backticks(["reference_date", "value", "lag"])
full_table_values = add_backticks(["value", "lag"])


values = signal_values
target_table = "signal_dim"


signal_dim_add_new_load = f"""
    INSERT INTO signal_dim (`source`, `signal`)
        SELECT DISTINCT sl.source, sl.signal
            FROM {self.load_table} AS sl LEFT JOIN signal_dim AS sd
            USING (`source`, `signal`)
            WHERE sd.source IS NULL
"""

meta.tables["wastewater_granular_load"].c.site_key_id
meta.tables["wastewater_granular_load"].primary_key
for table in meta.tables.values():
    print(table.name)
    for column in table.c:
        print("  " + column.name)
a = meta.reflect(bind=engine)
a
# The way epimetrics does it:
# 1. put into load
#
insert_into_loader_sql = f"""
    INSERT INTO `{self.load_table}`
    (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`,
    `value_updated_timestamp` <UNIX_TIMESTAMP(NOW())>, `value`, `stderr`, `sample_size`, `issue`, `lag`,
    `is_latest_issue` 1, `missing_value`, `missing_stderr`, `missing_sample_size`)
    VALUES
    (%s, %s, %s, %s, %s, %s,
    UNIX_TIMESTAMP(NOW()), %s, %s, %s, %s, %s,
    1, %s, %s, %s)
"""
# 2. join latest into load
fix_is_latest_version_sql = f"""
    UPDATE
        `{self.load_table}` JOIN `{self.latest_view}`
            USING (`source`, `signal`, `geo_type`, `geo_value`, `time_type`, `time_value`)
        SET `{self.load_table}`.`is_latest_issue`=0
        WHERE `{self.load_table}`.`version` < `{self.latest_view}`.`version`
"""
# 3. export from load to the other tables
signal_dim_add_new_load = f"""
    INSERT INTO signal_dim (`source`, `signal`)
        SELECT DISTINCT sl.source, sl.signal
            FROM {self.load_table} AS sl LEFT JOIN signal_dim AS sd
            USING (`source`, `signal`)
            WHERE sd.source IS NULL
"""
geo_dim_add_new_load = f"""
    INSERT INTO geo_dim (`geo_type`, `geo_value`)
        SELECT DISTINCT sl.geo_type, sl.geo_value
            FROM {self.load_table} AS sl LEFT JOIN geo_dim AS gd
            USING (`geo_type`, `geo_value`)
            WHERE gd.geo_type IS NULL
"""
epimetric_full_load = f"""
    INSERT INTO {self.history_table}
        (epimetric_id, signal_key_id, geo_key_id, issue, data_as_of_dt,
            time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp,
            computation_as_of_dt, missing_value, missing_stderr, missing_sample_size)
    SELECT
        epimetric_id, sd.signal_key_id, gd.geo_key_id, issue, data_as_of_dt,
            time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp,
            computation_as_of_dt, missing_value, missing_stderr, missing_sample_size
        FROM `{self.load_table}` sl
            INNER JOIN signal_dim sd USING (source, `signal`)
            INNER JOIN geo_dim gd USING (geo_type, geo_value)
    ON DUPLICATE KEY UPDATE
        `epimetric_id` = sl.`epimetric_id`,
        `value_updated_timestamp` = sl.`value_updated_timestamp`,
        `value` = sl.`value`,
        `stderr` = sl.`stderr`,
        `sample_size` = sl.`sample_size`,
        `lag` = sl.`lag`,
        `missing_value` = sl.`missing_value`,
        `missing_stderr` = sl.`missing_stderr`,
        `missing_sample_size` = sl.`missing_sample_size`
"""

epimetric_latest_load = f"""
    INSERT INTO {self.latest_table}
        (epimetric_id, signal_key_id, geo_key_id, issue, data_as_of_dt,
            time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp,
            computation_as_of_dt, missing_value, missing_stderr, missing_sample_size)
    SELECT
        epimetric_id, sd.signal_key_id, gd.geo_key_id, issue, data_as_of_dt,
            time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp,
            computation_as_of_dt, missing_value, missing_stderr, missing_sample_size
        FROM `{self.load_table}` sl
            INNER JOIN signal_dim sd USING (source, `signal`)
            INNER JOIN geo_dim gd USING (geo_type, geo_value)
        WHERE is_latest_issue = 1
    ON DUPLICATE KEY UPDATE
        `epimetric_id` = sl.`epimetric_id`,
        `value_updated_timestamp` = sl.`value_updated_timestamp`,
        `value` = sl.`value`,
        `stderr` = sl.`stderr`,
        `sample_size` = sl.`sample_size`,
        `issue` = sl.`issue`,
        `lag` = sl.`lag`,
        `missing_value` = sl.`missing_value`,
        `missing_stderr` = sl.`missing_stderr`,
        `missing_sample_size` = sl.`missing_sample_size`
"""

epimetric_load_delete_processed = f"""
    DELETE FROM `{self.load_table}`
"""


def add_new_load(
    self,
    target_table: str,
    values: list[str],
    not_null_value: str,
    execute: bool | None = None,
):
    """Add new values from the load table to the target table.

    Values specifies the list of columns as strings; they will be formatted
    to contain backticks if they do not already. `not_null_value` gives a
    column in `target_table` which has a `NOT NULL` restriction; this means
    if it's `NULL`, then that row doesn't exist. The particular column
    doesn't matter much, just that it's non-NULL. Likewise, it will be
    formatted to contain backticks.

    extra_table and extra values give any foreign
    """
    if execute is None:
        execute = self.execute
    values = add_backticks(values)
    not_null_value = add_backticks_single(not_null_value)
    add_new_target = f"""
    INSERT INTO {target_table}
        ({", ".join(values)})
        SELECT DISTINCT load.{", load.".join(values)}
        FROM {self.load_table} AS load
        LEFT JOIN {target_table} AS target
            USING ({", ".join(values)})
        WHERE target.{not_null_value} IS NULL
    """
    if execute:
        with engine.connect() as conn:
            conn.execute(text(add_new_target))
    return add_new_target
