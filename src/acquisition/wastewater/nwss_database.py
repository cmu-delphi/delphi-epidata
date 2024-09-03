from os import path
import pandas as pd

from sqlalchemy import Date, create_engine
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy import text
from sqlalchemy import MetaData
from logging import Logger
import sqlalchemy
from .nwss_constants import WASTEWATER_DDL, SIG_DIGITS

# TODO temp
# WASTEWATER_DDL = "/home/dsweber/allHail/delphi/epidataLocalBuild/driver/repos/delphi/delphi-epidata/src/ddl/wastewater.sql"


# TODO add a bunch of try catches and logger stuff
# TODO make sure this catches redundants when value is NULL
def add_backticks(string_array: list[str]):
    """enforce that every entry starts and ends with a backtick."""
    string_array = [x + "`" if not x.endswith("`") else x for x in string_array]
    string_array = ["`" + x if not x.startswith("`") else x for x in string_array]
    return string_array


def subtract_backticks(string_array: list[str]):
    """enforce that no entry starts and ends with a backtick."""
    string_array = [x[:-1] if x.endswith("`") else x for x in string_array]
    string_array = [x[1:] if x.startswith("`") else x for x in string_array]
    return string_array


def subtract_backticks_single(string):
    if string.endswith("`"):
        string = string[:-1]
    if string.startswith("`"):
        string = string[1:]
    return string


def add_backticks_single(string):
    if not string.endswith("`"):
        string = string + "`"
    if not string.startswith("`"):
        string = "`" + string
    return string


def sql_rel_equal(x, y, tol):
    """Are x and y are within tol of one another?

    `x` and `y` are expected to already have backticks, and tol is a positive base 10 exponent.
    """
    within_tolerance = (
        f"(ABS({x} - {y}) / GREATEST(ABS({x}), ABS({y}))  < {10**(-tol)}) "
    )

    return f"({within_tolerance})"


class Database:
    """A collection of wastewater database operations"""

    DATABASE_NAME = "covid"
    load_table = "`wastewater_granular_load`"
    full_table = "`wastewater_granular_full`"
    latest_table = "`wastewater_granular_latest`"
    latest_view = "`wastewater_granular_latest_v`"
    sample_site_values = add_backticks(["sample_loc_specify", "sample_method"])
    plant_values = add_backticks(["wwtp_jurisdiction", "wwtp_id"])
    signal_values = add_backticks(
        ["source", "signal", "pathogen", "provider", "normalization"]
    )
    full_table_core = add_backticks(["reference_date", "value", "lag"])
    full_table_meta = add_backticks(
        ["version", "value_updated_timestamp", "computation_as_of_dt", "missing_value"]
    )
    key_ids = add_backticks(["signal_key_id", "site_key_id"])
    main_id = "`wastewater_id`"

    def __init__(
        self,
        logger: Logger,
        engine: sqlalchemy.engine.base.Engine = create_engine(
            "mysql+pymysql://user:pass@127.0.0.1:13306/epidata"
        ),
        meta: MetaData | None = None,
        execute=True,
    ):
        if meta is None:
            meta = MetaData()
            meta.reflect(bind=engine)
        self.engine = engine
        self.meta = meta
        self.logger = logger
        self.execute = execute

    def load_DataFrame(self, df: pd.DataFrame, chunk_size=2**20):
        """Import a dataframe into the load table."""
        df.to_sql(
            name="wastewater_granular_load",
            con=self.engine,
            if_exists="append",
            index=False,
            method="multi",
            dtype={"version": Date},
            chunksize=chunk_size,
        )

    def standard_run(self, df: pd.DataFrame):
        """Given a Dataframe, perform the entire insertion operation.

        This means:
        1. loading into the load table,
        2. adding any new keys to `signal_dim`, `plant_dim`, and `sample_site_dim`,
        3. removing any values that are indistiguishable from the corresponding value in latest,
        4. inserting into both full and latest, and
        5. deleting the contents of the load table.
        """
        self.load_DataFrame(df)
        self.add_new_from_load("signal_dim", self.signal_values, key="signal_key_id")
        self.add_new_from_load("plant_dim", self.plant_values, key="plant_id")
        self.add_new_from_load(
            "sample_site_dim",
            self.sample_site_values,
            key="site_key_id",
            foreign_table="plant_dim",
            foreign_keys=["plant_id"],
            shared_values=self.plant_values,
            execute=True,
        )
        # have to wait until we've added the keys to efficiently delete
        self.delete_redundant()
        self.set_latest_flag()
        self.add_full_latest(self.full_table)
        self.add_full_latest(self.latest_table)
        self.delete_load()

    def delete_redundant(self, execute=None):
        """Deletes entries which are within tolerance of the corresponding version in latest."""
        # filtering out cases where:
        # 2. both values are null
        # 3. the values are approximately equal
        delete_irrelevant_version_sql = f"""
            DELETE {self.load_table}
              FROM {self.load_table}
              JOIN {self.latest_view} USING
                ({", ".join(self.key_ids)})
            WHERE
              (({self.load_table}.`value` IS NULL) AND ({self.latest_view}.`value` IS NULL))
            OR
              {sql_rel_equal(f"{self.load_table}.`value`", f"{self.latest_view}.`value`", SIG_DIGITS)}
            """
        if execute is None:
            execute = self.execute
        if execute:
            with self.engine.begin() as conn:
                conn.execute(text(delete_irrelevant_version_sql))
        return delete_irrelevant_version_sql

    def delete_redundant_backfill(self, execute=None):
        """Remove redundant versions, comparing against everything and not just latest."""
        self.logger.error("not yet implemented!")
        pass

    def set_latest_flag(self, execute=None):
        """Drop repeated values,and set the `is_latest_version` bit for insertion into latest."""
        # 1. version is older than the latest (unlikely to happen)
        # filtering out cases where:
        # 2. both values are null
        # 3. the values are approximately equal
        filter_relevant_version_sql = f"""
            UPDATE {self.load_table} JOIN {self.latest_view} USING
                ({", ".join(self.signal_values)}, {", ".join(self.sample_site_values)},
                {", ".join(self.plant_values)}, {", ".join(self.full_table_core)})
            SET {self.load_table}.`is_latest_version`=0
            WHERE
            ({self.load_table}.`version` < {self.latest_view}.`version`)
            """
        if execute is None:
            execute = self.execute
        if execute:
            with self.engine.begin() as conn:
                conn.execute(text(filter_relevant_version_sql))
        return filter_relevant_version_sql

    def add_new_from_load(
        self,
        target_table: str,
        values: list[str],
        key: str | None,
        foreign_table: str | None = None,
        shared_values: list[str] | None = None,
        foreign_keys: list[str] | None = None,
        execute: bool | None = None,
    ):
        """Add new values from the load table to the target table.

        Values specifies the list of columns as strings; they will be formatted
        to contain backticks if they do not already. `key` is the name of the
        `key` in the target table, and is used to insert the key value back into
        the load table.

        `foreign_table`, `foreign_values`, and `foreign_keys` allow for inserting
        foreign keys. `foreign_table` is the table with the foreign key, and should
        already be updated. `shared_values` are the values in the load table coming
        from `extra_table`. `foreign_keys` are just that.
        """
        if execute is None:
            execute = self.execute
        if foreign_keys is None:
            foreign_insert = [""]
            foreign_select = ""
        else:
            foreign_insert = [""] + add_backticks(foreign_keys)
            foreign_select = ", foreign_table." + ", foreign_table.".join(
                add_backticks(foreign_keys)
            )
        values_bt = add_backticks(values)
        values_no_bt = subtract_backticks(values)
        target_table = add_backticks_single(target_table)
        add_new_target = f"""
        INSERT INTO {target_table} ({", ".join(values_bt)}{", ".join(foreign_insert)})
            SELECT DISTINCT ld.{", ld.".join(values_no_bt)}{foreign_select}
            FROM {self.load_table} AS ld
            LEFT JOIN {target_table} AS td
                USING ({", ".join(values_bt)})"""
        if foreign_table is not None and shared_values is not None:
            foreign_table = add_backticks_single(foreign_table)
            shared_values = add_backticks(shared_values)
            add_new_target += f"""
            LEFT JOIN {foreign_table} AS foreign_table
                USING ({", ".join(shared_values)})
            """
            # TODO TODO ADD THE ID'S BACK TO THE ORIGINAL

        # this could actually be any column as long as it's required to not be NULL; here every aux table satisfies that
        add_new_target += f"            WHERE td.{values_bt[0]} IS NULL"

        # if we're handed a key, add the value from that back to the load table
        if key is not None:
            key = add_backticks_single(key)
            add_load_ids = f"""
            UPDATE {self.load_table} load_table
                INNER JOIN {target_table} target_table
                    USING ({", ".join(values_bt)})
                """
            if (
                foreign_table is not None
                and shared_values is not None
                and foreign_keys is not None
            ):
                # foreign_table.foo = load_table.foo
                shared = " ".join(
                    [f"foreign_table.{x} = load_table.{x} AND " for x in shared_values]
                )
                foreign = " ".join(
                    [
                        f"foreign_table.{x} = target_table.{x}"
                        for x in add_backticks(foreign_keys)
                    ]
                )
                # to join with a foreign table, we need to use ON so the key from
                # the foreign table can match with the key from the target table,
                # and not the load table (since that is the null we're trying to
                # replace)
                add_load_ids += f"""INNER JOIN {foreign_table} AS foreign_table
                    ON ({shared} {foreign})
                """
            add_load_ids += f"SET load_table.{key} = target_table.{key}"
        else:
            add_load_ids = ""
        if execute:
            with self.engine.begin() as conn:
                conn.execute(text(add_new_target))
                if key is not None:
                    conn.execute(text(add_load_ids))
        return add_new_target, add_load_ids

    def read_table(self, table_name, max_entries: int | None = None, **kwargs):
        if max_entries is None:
            statement = subtract_backticks_single(table_name)
        else:
            table_name = add_backticks_single(table_name)
            statement = f"SELECT top {max_entries} FROM `{table_name}`"
        return pd.read_sql(sql=statement, con=self.engine, **kwargs)

    def add_full_latest(self, target_table, execute: bool | None = None):
        if execute is None:
            execute = self.execute
        target_table = add_backticks_single(target_table)

        add_to_table = f"""
        INSERT INTO {target_table}
          ({self.main_id}, {", ".join(self.key_ids)}, {", ".join(self.full_table_core)}, {", ".join(self.full_table_meta)})
        SELECT
          {self.main_id}, {", ".join(self.key_ids)}, {", ".join(self.full_table_core)}, {", ".join(self.full_table_meta)}
        FROM {self.load_table} lt
        """

        if target_table == self.latest_table:
            add_to_table += "WHERE `is_latest_version` = 1"
            meta_partial = self.full_table_meta
        elif target_table == self.full_table:
            # we don't update version for the full database
            meta_partial = self.full_table_meta.copy()
            meta_partial.remove("`version`")
        else:
            raise AssertionError("can't handle table names other than latest or full")
        core_list = "            \n".join(
            [f"{x} = lt.{x}," for x in self.full_table_core]
        )
        meta_list = "            \n".join([f"{x} = lt.{x}," for x in meta_partial])
        add_to_table += f"""
        ON DUPLICATE KEY UPDATE
            {core_list}
            {meta_list.rstrip()[:-1]}
        """
        if execute:
            with self.engine.begin() as conn:
                res = conn.execute(text(add_to_table))
        return add_to_table

    def delete_load(self, execute=None):
        if execute is None:
            execute = self.execute
        statement = f"DELETE FROM {self.load_table}"
        if execute:
            with self.engine.begin() as conn:
                res = conn.execute(text(statement))
        return statement

    def build_database(self, target_ddl=WASTEWATER_DDL):
        """Strictly for testing purposes."""

        with self.engine.begin() as conn:
            with open(target_ddl) as file:
                ddl = file.read()
                ddl = ddl.split("\n", maxsplit=1)[1]
                res = conn.execute(text(ddl))
                return res
