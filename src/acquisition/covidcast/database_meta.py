from dataclasses import asdict, dataclass, fields
from datetime import datetime
import json
from multiprocessing import cpu_count
from queue import Queue, Empty
import threading
from typing import Dict, List, Tuple

import pandas as pd
from requests import get

# TODO: Switch to delphi_epidata_py when we release it https://github.com/cmu-delphi/delphi-epidata/issues/942.
# from delphi_epidata.request import Epidata, EpiRange

from .logger import get_structured_logger
from .covidcast_row import CovidcastRow, set_df_dtypes
from .database import Database
from .config import GEO_TYPES, ALL_TIME
from ...server.endpoints.covidcast_utils.model import DataSignal, data_signals_by_key


@dataclass
class MetaTableRow:
    data_source: str
    signal: str
    time_type: str
    geo_type: str
    min_time: int
    max_time: int
    num_locations: int
    min_value: float
    max_value: float
    mean_value: float
    stdev_value: float
    last_update: int
    max_issue: int
    min_lag: int
    max_lag: int

    def as_df(self):
        df = pd.DataFrame(
            {
                "data_source": self.data_source,
                "signal": self.signal,
                "time_type": self.time_type,
                "geo_type": self.geo_type,
                "min_time": self.min_time,
                "max_time": self.max_time,
                "num_locations": self.num_locations,
                "min_value": self.min_value,
                "max_value": self.max_value,
                "mean_value": self.mean_value,
                "stdev_value": self.stdev_value,
                "last_update": self.last_update,
                "max_issue": self.max_issue,
                "min_lag": self.min_lag,
                "max_lag": self.max_lag,
            },
            index=[0],
        )
        set_df_dtypes(
            df,
            dtypes={
                "data_source": str,
                "signal": str,
                "time_type": str,
                "geo_type": str,
                "min_time": int,
                "max_time": int,
                "num_locations": int,
                "min_value": float,
                "max_value": float,
                "mean_value": float,
                "stdev_value": float,
                "last_update": int,
                "max_issue": int,
                "min_lag": int,
                "max_lag": int,
            },
        )
        return df

    def as_dict(self):
        return asdict(self)

    @staticmethod
    def _extract_fields(group_df):
        if "source" in group_df.columns:
            assert group_df["source"].unique().size == 1
            source = group_df["source"].iloc[0]
        elif "data_source" in group_df.columns:
            assert group_df["data_source"].unique().size == 1
            source = group_df["data_source"].iloc[0]
        else:
            raise ValueError("Source name not found in group_df.")

        if "signal" in group_df.columns:
            assert group_df["signal"].unique().size == 1
            signal = group_df["signal"].iloc[0]
        else:
            raise ValueError("Signal name not found in group_df.")

        if "time_type" in group_df.columns:
            assert group_df["time_type"].unique().size == 1
            time_type = group_df["time_type"].iloc[0]
        else:
            raise ValueError("Time type not found in group_df.")

        if "geo_type" in group_df.columns:
            assert group_df["geo_type"].unique().size == 1
            geo_type = group_df["geo_type"].iloc[0]
        else:
            raise ValueError("Geo type not found in group_df.")

        if "value_updated_timestamp" in group_df.columns:
            last_updated = max(group_df["value_updated_timestamp"])
        else:
            last_updated = int(datetime.now().timestamp())

        return source, signal, time_type, geo_type, last_updated

    @staticmethod
    def from_group_df(group_df):
        if group_df is None or group_df.empty:
            raise ValueError("Empty group_df given.")

        source, signal, time_type, geo_type, last_updated = MetaTableRow._extract_fields(group_df)

        return MetaTableRow(
            data_source=source,
            signal=signal,
            time_type=time_type,
            geo_type=geo_type,
            min_time=min(group_df["time_value"]),
            max_time=max(group_df["time_value"]),
            num_locations=len(group_df["geo_value"].unique()),
            min_value=min(group_df["value"]),
            max_value=max(group_df["value"]),
            mean_value=group_df["value"].mean().round(7),
            stdev_value=group_df["value"].std(ddof=0).round(7),
            last_update=last_updated,
            max_issue=max(group_df["issue"]),
            min_lag=min(group_df["lag"]),
            max_lag=max(group_df["lag"]),
        )

class DatabaseMeta(Database):
    # TODO: Verify the correct base_url for a local API server.
    def __init__(self, base_url: str = "http://localhost/epidata") -> "DatabaseMeta":
        Database.__init__(self)
        self.epidata_base_url = base_url
        # TODO: Switch to delphi_epidata_py when we release it https://github.com/cmu-delphi/delphi-epidata/issues/942.
        self.delphi_epidata = False

    def compute_covidcast_meta(self, table_name=None, jit=False, parallel=False):
        """This wrapper is here for A/B testing the JIT and non-JIT metadata computation.
        
        TODO: Remove after code review.
        """
        return self.compute_covidcast_meta_new(table_name, parallel) if jit else self.compute_covidcast_meta_old(table_name)

    def compute_covidcast_meta_old(self, table_name=None):
        """This is the old method (not using JIT) to compute and return metadata on all COVIDcast signals.
        
        TODO: This is here for A/B testing. Remove this after code review.
        """
        logger = get_structured_logger("compute_covidcast_meta")

        if table_name is None:
            table_name = self.latest_view

        n_threads = max(1, cpu_count() * 9 // 10)  # aka number of concurrent db connections, which [sh|c]ould be ~<= 90% of the #cores available to SQL server
        # NOTE: this may present a small problem if this job runs on different hardware than the db,
        #       but we should not run into that issue in prod.
        logger.info(f"using {n_threads} workers")

        srcsigs = Queue()  # multi-consumer threadsafe!
        sql = f"SELECT `source`, `signal` FROM `{table_name}` GROUP BY `source`, `signal` ORDER BY `source` ASC, `signal` ASC;"
        self._cursor.execute(sql)
        for source, signal in self._cursor:
            srcsigs.put((source, signal))

        inner_sql = f"""
        SELECT
            `source` AS `data_source`,
            `signal`,
            `time_type`,
            `geo_type`,
            MIN(`time_value`) AS `min_time`,
            MAX(`time_value`) AS `max_time`,
            COUNT(DISTINCT `geo_value`) AS `num_locations`,
            MIN(`value`) AS `min_value`,
            MAX(`value`) AS `max_value`,
            ROUND(AVG(`value`),7) AS `mean_value`,
            ROUND(STD(`value`),7) AS `stdev_value`,
            MAX(`value_updated_timestamp`) AS `last_update`,
            MAX(`issue`) as `max_issue`,
            MIN(`lag`) as `min_lag`,
            MAX(`lag`) as `max_lag`
        FROM
            `{table_name}`
        WHERE
            `source` = %s AND
            `signal` = %s
        GROUP BY
            `time_type`,
            `geo_type`
        ORDER BY
            `time_type` ASC,
            `geo_type` ASC
        """

        meta = []
        meta_lock = threading.Lock()

        def worker():
            name = threading.current_thread().name
            logger.info("starting thread", thread=name)
            #  set up new db connection for thread
            worker_dbc = Database()
            worker_dbc.connect(connector_impl=self._connector_impl, host=self._db_host, user=self._db_credential_user, password=self._db_credential_password, database=self._db_database)
            w_cursor = worker_dbc._cursor
            try:
                while True:
                    (source, signal) = srcsigs.get_nowait()  # this will throw the Empty caught below
                    logger.info("starting pair", thread=name, pair=f"({source}, {signal})")
                    w_cursor.execute(inner_sql, (source, signal))
                    with meta_lock:
                        meta.extend(list(dict(zip(w_cursor.column_names, x)) for x in w_cursor))
                    srcsigs.task_done()
            except Empty:
                logger.info("no jobs left, thread terminating", thread=name)
            finally:
                worker_dbc.disconnect(False)  # cleanup

        threads = []
        for n in range(n_threads):
            t = threading.Thread(target=worker, name="MetacacheThread-" + str(n))
            t.start()
            threads.append(t)

        srcsigs.join()
        logger.info("jobs complete")
        for t in threads:
            t.join()
        logger.info("all threads terminated")

        # sort the metadata because threaded workers dgaf
        sorting_fields = "data_source signal time_type geo_type".split()
        sortable_fields_fn = lambda x: [(field, x[field]) for field in sorting_fields]
        prepended_sortables_fn = lambda x: sortable_fields_fn(x) + list(x.items())
        tuple_representation = list(map(prepended_sortables_fn, meta))
        tuple_representation.sort()
        meta = list(map(dict, tuple_representation))  # back to dict form

        return meta

    def get_source_sig_list(self, data_signal_table: Dict[Tuple[str, str], DataSignal] = data_signals_by_key, derived: bool = False) -> List[Tuple[str]]:
        """Return the source-signal pair names from the database.

        The derived flag determines whether the signals returned are derived or base signals.
        """
        return [(data_signal.source, data_signal.signal) for data_signal in data_signal_table.values() if data_signal.compute_from_base == derived]

    def compute_base_signal_meta(self, source: str, signal: str, table_name: str = None) -> pd.DataFrame:
        """Compute the meta information for base signals.

        A base signal is a signal whose values do not depend on another signal. A derived signal is one whose values are obtained 
        through a transformation of a base signal, e.g. a 7 day average signal or an incidence (compared to cumulative) signal.
        """
        if table_name is None:
            table_name = self.latest_view

        inner_sql = f"""
        SELECT
            `source` AS `data_source`,
            `signal`,
            `time_type`,
            `geo_type`,
            MIN(`time_value`) AS `min_time`,
            MAX(`time_value`) AS `max_time`,
            COUNT(DISTINCT `geo_value`) AS `num_locations`,
            MIN(`value`) AS `min_value`,
            MAX(`value`) AS `max_value`,
            ROUND(AVG(`value`),7) AS `mean_value`,
            ROUND(STD(`value`),7) AS `stdev_value`,
            MAX(`value_updated_timestamp`) AS `last_update`,
            MAX(`issue`) as `max_issue`,
            MIN(`lag`) as `min_lag`,
            MAX(`lag`) as `max_lag`
        FROM
            `{table_name}`
        WHERE
            `source` = %s AND
            `signal` = %s
        GROUP BY
            `time_type`,
            `geo_type`
        ORDER BY
            `time_type` ASC,
            `geo_type` ASC
        """

        # TODO: Consider whether we really need this new object. Maybe for parallel or maybe not.
        db = Database()
        db.connect(connector_impl=self._connector_impl, host=self._db_host, user=self._db_credential_user, password=self._db_credential_password, database=self._db_database)
        db._cursor.execute(inner_sql, (source, signal))
        base_signal_meta = pd.DataFrame(db._cursor.fetchall(), columns=["data_source", "signal", "time_type", "geo_type", "min_time", "max_time", "num_locations", "min_value", "max_value", "mean_value", "stdev_value", "last_update", "max_issue", "min_lag", "max_lag"])

        return base_signal_meta

    def compute_derived_signal_meta(self, source: str, signal: str, base_signal_meta: pd.DataFrame, data_signal_table: Dict[Tuple[str, str], DataSignal] = data_signals_by_key) -> pd.DataFrame:
        """Compute the meta information for a derived signal.
        
        A derived signal is a transformation of a base signal. Since derived signals are not stored in the database, but are computed
        on the fly by the API, we call the API here. It is assumed that we have already computed the meta information for the base
        signals and passed that in base_signal_meta. The latter is needed to set the `last_updated` field.
        """
        logger = get_structured_logger("get_derived_signal_meta")

        meta_table_columns = [field.name for field in fields(MetaTableRow)]
        covidcast_response_columns = [field.name for field in fields(CovidcastRow) if field.name not in CovidcastRow()._api_row_ignore_fields]

        # We should be able to find the signal in our table.
        data_signal = data_signal_table.get((source, signal))
        if not data_signal:
            logger.warn(f"Could not find the requested derived signal {source}:{signal} in the data signal table. Returning no meta results.")
            return pd.DataFrame(columns=meta_table_columns)

        # Request all the data for the derived signal.
        # TODO: Use when delphi_epidata_py is released https://github.com/cmu-delphi/delphi-epidata/issues/942.
        if self.delphi_epidata:
            raise NotImplemented("Use the old epidata client for now.")
            # TODO: Consider refactoring to combine multiple signal requests in one call.
            all_time = EpiRange(19000101, 20500101)
            epidata = Epidata.with_base_url(self.epidata_base_url)
            api_response_df = pd.concat([epidata.covidcast(data_source=source, signals=signal, time_type=data_signal.time_type, geo_type=geo_type, time_values=all_time, geo_values="*").df() for geo_type in GEO_TYPES])
        else:
            base_url = f"{self.epidata_base_url}/covidcast/"
            params = {"data_source": source, "signals": signal, "time_type": data_signal.time_type, "time_values": ALL_TIME, "geo_values": "*"}
            signal_data_dfs = []
            for geo_type in GEO_TYPES:
                params.update({"geo_type": geo_type})
                response = get(base_url, params)
                if response.status_code in [200]:
                    signal_data_dfs.append(pd.DataFrame.from_records(response.json()['epidata'], columns=covidcast_response_columns))
                else:
                    raise Exception(f"The API responded with an error when attempting to get data for the derived signal's {source}:{signal} meta computation. There may be an issue with the API server.") 

        # Group the data by time_type and geo_type and find the statistical summaries for their values.
        meta_rows = [MetaTableRow.from_group_df(group_df).as_df() for signal_data_df in signal_data_dfs for _, group_df in signal_data_df.groupby("time_type")]
        if meta_rows:
            meta_df = pd.concat(meta_rows)
        else:
            logger.warn(f"The meta computation for {source}:{signal} returned no summary statistics. There may be an issue with the API server or the database.")
            return pd.DataFrame(columns=meta_table_columns)

        # Copy the value of 'last_updated' column from the base signal meta to the derived signal meta.
        # TODO: Remove if/when we remove the 'last_updated' column.
        meta_df = pd.merge(
            meta_df.assign(parent_signal = data_signal.signal_basename),
            base_signal_meta[["data_source", "signal", "time_type", "geo_type", "last_update"]],
            left_on = ["data_source", "parent_signal", "time_type", "geo_type"],
            right_on = ["data_source", "signal", "time_type", "geo_type"]
        )
        meta_df = meta_df.assign(signal = meta_df["signal_x"], last_update = meta_df["last_update_y"])

        return meta_df[meta_table_columns]

    def compute_covidcast_meta_new(self, table_name=None, parallel=True, data_signal_table: Dict[Tuple[str, str], DataSignal] = data_signals_by_key) -> Dict:
        """Compute and return metadata on all non-WIP COVIDcast signals."""
        logger = get_structured_logger("compute_covidcast_meta")

        if table_name is None:
            table_name = self.latest_view

        if parallel:
            n_threads = max(1, cpu_count() * 9 // 10)  # aka number of concurrent db connections, which [sh|c]ould be ~<= 90% of the #cores available to SQL server
            # NOTE: this may present a small problem if this job runs on different hardware than the db,
            #       but we should not run into that issue in prod.
            logger.info(f"using {n_threads} workers")

            srcsigs = Queue()  # multi-consumer threadsafe!
            for source, signal in self.get_source_sig_list(table_name):
                srcsigs.put((source, signal))

            meta_dfs = []
            meta_lock = threading.Lock()

            def worker():
                name = threading.current_thread().name
                logger.info("starting thread", thread=name)
                #  set up new db connection for thread
                worker_dbc = DatabaseMeta()
                worker_dbc.connect(connector_impl=self._connector_impl, host=self._db_host, user=self._db_credential_user, password=self._db_credential_password, database=self._db_database)
                try:
                    while True:
                        (source, signal) = srcsigs.get_nowait()  # this will throw the Empty caught below
                        logger.info("starting pair", thread=name, pair=f"({source}, {signal})")

                        df = worker_dbc.covidcast_meta_job(table_name, source, signal)
                        with meta_lock:
                            meta_dfs.append(df)

                        srcsigs.task_done()
                except Empty:
                    logger.info("no jobs left, thread terminating", thread=name)
                finally:
                    worker_dbc.disconnect(False)  # cleanup

            threads = []
            for n in range(n_threads):
                t = threading.Thread(target=worker, name="MetacacheThread-" + str(n))
                t.start()
                threads.append(t)

            srcsigs.join()
            logger.info("jobs complete")

            for t in threads:
                t.join()
            logger.info("all threads terminated")
        else:
            # Here to illustrate the simple logic behind meta computations without the parallel boilerplate
            base_meta_dfs = pd.concat([self.compute_base_signal_meta(source, signal, table_name) for source, signal in self.get_source_sig_list(data_signal_table=data_signal_table, derived=False)])
            derived_meta_dfs = pd.concat([self.compute_derived_signal_meta(source, signal, base_meta_dfs, data_signal_table=data_signal_table) for source, signal in self.get_source_sig_list(data_signal_table=data_signal_table, derived=True)])

        # combine and sort the metadata results
        meta_df = pd.concat([base_meta_dfs, derived_meta_dfs]).sort_values(by="data_source signal time_type geo_type".split())
        return meta_df.to_dict(orient="records")

    def update_covidcast_meta_cache(self, metadata):
        """Updates the `covidcast_meta_cache` table."""

        sql = """
      UPDATE
        `covidcast_meta_cache`
      SET
        `timestamp` = UNIX_TIMESTAMP(NOW()),
        `epidata` = %s
    """
        epidata_json = json.dumps(metadata)

        self._cursor.execute(sql, (epidata_json,))

    def retrieve_covidcast_meta_cache(self):
        """Useful for viewing cache entries (was used in debugging)"""

        sql = """
      SELECT `epidata`
      FROM `covidcast_meta_cache`
      ORDER BY `timestamp` DESC
      LIMIT 1;
    """
        self._cursor.execute(sql)
        cache_json = self._cursor.fetchone()[0]
        cache = json.loads(cache_json)
        cache_hash = {}
        for entry in cache:
            cache_hash[(entry["data_source"], entry["signal"], entry["time_type"], entry["geo_type"])] = entry
        return cache_hash
