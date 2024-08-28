"""Functions to download the data from NWSS and save into a csv with a shared format."""

import numpy as np
import pandas as pd
from sodapy import Socrata
from logging import Logger
from delphi_utils import get_structured_logger

# first party tools
from .wastewater_utils import sig_digit_round, convert_df_type
from .nwss_database import Database
from delphi_utils import GeoMapper
import delphi_utils

# Sample site names
from .nwss_constants import (
    AUX_INFO_COLUMNS,
    COUNTY_INFO,
    KEY_PLOT_NAMES,
    KEY_PLOT_TYPES,
    METRIC_SIGNALS,
    SIG_DIGITS,
    CONCENTRATION_SIGNALS,
    TIME_SPANNED,
    TYPE_DICT_CONC,
    TYPE_DICT_METRIC,
)


def key_plot_id_parse(key_plot_ids: pd.Series) -> pd.DataFrame:
    """Given a list of key plot id's, extract the various sub-values.

    The Dataframe returned has the following columns
      Provider
      wwtp_jurisdiction
      wwtp_id
      sample_location
      sample_location_specify
      sample_method
    """
    # To understand the regex below, I suggest putting it into
    # https://regex101.com/ to parse how it's getting the names in detail.
    # But here are 2 representative example keys
    # NWSS_mi_1040_Before treatment plant_147_raw wastewater
    # CDC_VERILY_ak_1491_Treatment plant_raw wastewater
    # every variable is separated by `_`, though some may also contain them
    processed_names = key_plot_ids.str.extract(
        (
            r"(?P<provider>.+)_"  # provider, anything before the next one "NWSS"
            r"(?P<wwtp_jurisdiction>[a-z]{2})_"  # state, exactly two letters "mi"
            r"(?P<wwtp_id>[0-9]+)_"  # an id, at least one digits "1040"
            r"(?P<sample_location>[^_]+)_"  # either "Before treatment plant" or "Treatment plant"
            r"(?P<sample_location_specify>[0-9]*)_*"  # a number, may be missing (thus _*)
            r"(?P<sample_method>.*)"  # one of 4 values:
            # 'post grit removal', 'primary effluent', 'primary sludge', 'raw wastewater'
        )
    )
    processed_names.sample_location_specify = pd.to_numeric(
        processed_names.sample_location_specify, errors="coerce"
    ).astype("Int32")
    # representing NULL as -1 so that equality matching actually works well
    processed_names.loc[
        processed_names.sample_location_specify.isna(), "sample_location_specify"
    ] = -1
    processed_names["key_plot_id"] = key_plot_ids
    processed_names = processed_names.set_index("key_plot_id")
    processed_names = processed_names.astype(KEY_PLOT_TYPES)
    # TODO warnings/errors when things don't parse
    return processed_names


def validate_metric_key_plot_ids(
    df_metric: pd.DataFrame, metric_keys: pd.DataFrame, logger: Logger
) -> None:
    """Check that the metric key_plot_ids match the corresponding values in the table.

    One of the weirder edge cases is the `wwtp_jurisdiction`. The `key_plot_id` treats this as state only, whereas the actual `wwtp_jurisdiction` appears to be state + New York City. It is currently setup to warn if another location appears in `wwtp_jurisdiction`, but not error.
    """
    geomapper = GeoMapper()
    df_metric = geomapper.add_geocode(
        df_metric,
        from_code="state_name",
        new_code="state_id",
        from_col="wwtp_jurisdiction",
        dropna=False,
    )
    # NYC is the weird extra jurisdiction that shows up in wwtp_jur but not the actual key_plot_id
    is_not_nyc = (
        df_metric.wwtp_jurisdiction[df_metric.state_id.isna()] != "New York City"
    )
    if any(is_not_nyc):
        logger.warn(
            "There is a wwtp_jurisdiction that is not a state or nyc.",
            not_nyc=df_metric.wwtp_jurisdiction[df_metric.state_id.isna()][is_not_nyc],
        )
    df_metric.loc[df_metric.state_id.isna(), "state_id"] = "ny"
    df_metric["wwtp_jurisdiction"] = df_metric["state_id"]
    df_metric = df_metric.drop(columns="state_id")

    checking_metric_key_plot_ids = metric_keys.reset_index().merge(
        df_metric.drop(columns=["date", *METRIC_SIGNALS]).drop_duplicates(),
        how="outer",
        indicator=True,
    )
    missing_keys = checking_metric_key_plot_ids[
        checking_metric_key_plot_ids["_merge"] != "both"
    ]
    if missing_keys.size > 0:
        logger.error(
            "There are some keys which don't match their values in key_plot_id",
            missing_keys=missing_keys,
        )


def deduplicate_aux(auxiliary_info: pd.DataFrame, logger: Logger) -> pd.DataFrame:
    """Check that first_sample_date, sampling_prior, and counties have unique values across time and space."""
    should_be_site_unique = auxiliary_info.groupby("key_plot_id").agg(
        {
            "county_names": pd.Series.nunique,
            "county_fips": pd.Series.nunique,
            "first_sample_date": pd.Series.nunique,
            "sampling_prior": pd.Series.nunique,
        }
    )
    is_site_unique = should_be_site_unique.max() == 1
    if not all(is_site_unique):
        logger.error(
            f"{is_site_unique.index[~is_site_unique]} are not unique! This means that the sample_site metadata is time dependent."
        )
    auxiliary_info = auxiliary_info.drop_duplicates([*AUX_INFO_COLUMNS, *COUNTY_INFO])
    return auxiliary_info.drop(columns="date")


def download_raw_data(token: str, logger: Logger) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Bare bones download of data from the socrata API."""
    client = Socrata("data.cdc.gov", token)
    results_concentration = client.get("g653-rqe2", limit=10**10)
    results_metric = client.get("2ew6-ywp6", limit=10**10)
    df_metric = pd.DataFrame.from_records(results_metric)
    df_concentration = pd.DataFrame.from_records(results_concentration)
    # Schema checks/conversions.
    df_concentration = convert_df_type(df_concentration, TYPE_DICT_CONC, logger)
    df_metric = convert_df_type(df_metric, TYPE_DICT_METRIC, logger)
    df_metric = df_metric.rename(columns={"date_end": "date"})
    return df_concentration, df_metric


def format_nwss_data(
    df_concentration: pd.DataFrame, df_metric: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Helper to pull_nwss_data, mainly separated to ease debugging without pulling."""
    # pull out the auxiliary_info first so we can drop it
    # this means county, first sample date and sampling_prior, along with the keys to specify those
    auxiliary_info = df_metric.loc[
        :,
        ["date", *AUX_INFO_COLUMNS, *COUNTY_INFO],
    ]

    # make sure there's not duplicates in time and space
    auxiliary_info = deduplicate_aux(auxiliary_info, logger)
    # TODO verify the county names match the codes
    has_right_interval = df_metric.date - df_metric.date_start == TIME_SPANNED
    # making sure that our assumption that date_start is redundant is correct
    # default interval is 14 days as of the time of writing, and is also included in the column names
    if not all(has_right_interval):
        logger.error(
            f"The time difference isn't strictly {TIME_SPANNED}. This means dropping `date_start` loses information now",
            different_examples=df_metric[~has_right_interval],
        )
    # This has been shuttled off to auxiliary_info, so we drop it for efficiency of pivoting
    df_metric = df_metric.drop(
        columns=[
            "county_names",
            "county_fips",
            "sampling_prior",
            "first_sample_date",
            "reporting_jurisdiction",
            "date_start",
        ]
    )

    # Warn if the normalization scheme is ever seen to be NA
    na_columns = df_concentration[df_concentration["normalization"].isna()]
    if na_columns.size != 0:
        logger.info("There are columns without normalization.", na_columns=na_columns)

    conc_keys = key_plot_id_parse(pd.Series(df_concentration.key_plot_id.unique()))
    # get the keys+normalizations where there's an unambiguous choice of normalization
    key_plot_norms = df_concentration.loc[
        :, ["key_plot_id", "normalization"]
    ].drop_duplicates()

    # count the # of normalizations for a given key_plot_id
    key_plot_norms["n_norms"] = key_plot_norms.groupby(
        "key_plot_id"
    ).normalization.transform("count")
    key_plot_norms = (
        key_plot_norms[key_plot_norms.n_norms == 1]
        .drop(columns="n_norms")
        .set_index("key_plot_id")
    )
    # add the unambiguous normalizations
    conc_keys = conc_keys.join(
        key_plot_norms,
        how="left",
    )
    conc_keys.loc[conc_keys.normalization.isna(), "normalization"] = "unknown"
    metric_keys = key_plot_id_parse(pd.Series(df_metric.key_plot_id.unique()))
    validate_metric_key_plot_ids(df_metric, metric_keys, logger)
    # form the joint table of keys found in both, along with a column
    # identifying which direction there is missingness
    joint_keys = conc_keys.reset_index().merge(
        metric_keys.reset_index(), indicator=True, how="outer"
    )
    # set any NA normalizations to "unknown" for reasons of db comparison
    joint_keys.loc[joint_keys.normalization.isna(), "normalization"] = "unknown"
    joint_keys = joint_keys.astype(KEY_PLOT_TYPES)
    only_in_one = joint_keys[joint_keys._merge != "both"]
    if only_in_one.size > 0:
        only_in_one = only_in_one.replace(
            {"left_only": "conc", "right_only": "metric"}
        ).rename(columns={"_merge": "key_in"})
        logger.info(
            "There are locations present in one key_plot_id", only_in_one=only_in_one
        )
        # these can cause 2 problems:
        # in metric but not conc means a lack of normalization.
        # in conc but not metric is harder, as it lacks population,
        # sampling_prior, first_sample_date, county_names, and county_fips. Those
        # will all have to be NA

    # we're dropping _merge since this will already be conveyed by NA's after
    # joining the datasets
    joint_keys = joint_keys.set_index("key_plot_id").drop(columns="_merge")
    # add the key info to axuiliary info, and make sure any locations in the
    # metric are included, even if their values are NA
    auxiliary_info = auxiliary_info.merge(joint_keys, on="key_plot_id", how="outer")
    # adding the key breakdown to df_concentration
    df_conc_long = pd.melt(
        df_concentration,
        id_vars=["date", "key_plot_id", "normalization"],
        value_vars=CONCENTRATION_SIGNALS,
        var_name="signal",
    )
    df_conc_long = df_conc_long.set_index(["key_plot_id", "date"])
    # concentration needs to keep the normalization info b/c it is accurate to the date
    df_conc_long = df_conc_long.join(
        joint_keys.drop(columns=["normalization"]), how="left"
    )
    # forming the long version of the metric data
    # note that melting with the minimal set of columns is significantly faster, even if we're reappending them after during the join
    df_metric = df_metric.drop(
        columns=[
            "wwtp_jurisdiction",
            "wwtp_id",
            "sample_location",
            "sample_location_specify",
        ]
    )

    df_metric_long = pd.melt(
        df_metric,
        id_vars=["date", "key_plot_id"],
        value_vars=METRIC_SIGNALS,
        var_name="signal",
    )
    df_metric_long = df_metric_long.set_index(["key_plot_id", "date"])
    df_metric_long = df_metric_long.join(joint_keys, how="left")

    # join the two datasets
    df = pd.concat([df_conc_long, df_metric_long])
    df = df.astype({"normalization": "category", "signal": "category"})
    # sorting and making sure there aren't duplicates
    df = (
        df.reset_index()
        .set_index(
            [
                "signal",
                "provider",
                "normalization",
                "wwtp_jurisdiction",
                "wwtp_id",
                "sample_location",
                "sample_location_specify",
                "sample_method",
                "date",
            ]
        )
        .sort_index()
    )
    df.drop(columns="key_plot_id").sort_index()
    df = df.reset_index()
    deduped = df.drop_duplicates(
        subset=[
            "signal",
            "provider",
            "normalization",
            "wwtp_jurisdiction",
            "sample_location",
            "sample_location_specify",
            "sample_method",
            "wwtp_id",
            "date",
        ],
    )
    if deduped.shape != df.shape:
        logger.error(
            "there were duplicate entries",
            df_shape=df.shape,
            dedupe_shape=deduped.shape,
        )

    return df, auxiliary_info


def pull_nwss_data(token: str, logger: Logger) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pull the latest NWSS Wastewater data for both the concentration and metric datasets, and conform them into a dataset and a county mapping.

    There are two output datasets:
    The primary data, which has the rows
    - (source_name, signal_name, pathogen, provider, normalization), (wwtp_jurisdiction, wwtp_id, sample_loc_specify), reference_date, value
    There's a second, seperate table that contains just the county-sample_site mapping, which consists of rows that are:
    - date_changed (likely only the first day the sample site is present), wwtp_jurisdictoin, wwtp_id, sample_loc_specify

    Parameters
    ----------
    socrata_token: str
        My App Token for pulling the NWSS data (could be the same as the nchs data)
    logger: the structured logger

    Returns
    -------
    pd.DataFrame
        Dataframe as described above.
    """
    # TODO temp, remove
    import os

    token = os.environ.get("SODAPY_APPTOKEN")
    logger = get_structured_logger("csv_ingestion", filename="writingErrorLog")
    # end temp
    df_concentration, df_metric = download_raw_data(token, logger)
    df, auxiliary_info = format_nwss_data(df_concentration, df_metric)
    df = df.rename(
        columns={
            "date": "reference_date",
            "sample_location_specify": "sample_loc_specify",
        }
    )
    #  sample location is a boolean indictating whether sample_loc_specify is NA
    df = df.drop(columns=["key_plot_id", "sample_location"])
    df["lag"] = pd.Timestamp.today().normalize() - df.reference_date
    df["lag"] = df["lag"].dt.days
    df["source"] = "NWSS"
    # TODO missing value code
    df["missing_value"] = 0
    df["version"] = pd.Timestamp("today").normalize()
    df["pathogen"] = "COVID"
    df["value_updated_timestamp"] = pd.Timestamp("now")
    return df, auxiliary_info


from sqlalchemy import create_engine
from sqlalchemy import text


for table_name in inspector.get_table_names():
    for column in inspector.get_columns(table_name):
        print("Column: %s" % column["name"])

with database.engine.connect() as conn:
    res = conn.execute(text("show tables;"))
    print(pd.DataFrame(res.all()))

# accident
with database.engine.begin() as conn:
    conn.execute(text("DROP TABLE wastewater_granular"))

with database.engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM wastewater_granular_load"))
    for row in result:
        print(row)

with database.engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM `signal_dim`"))
    print(result.keys())
    for row in result:
        print(row)

with database.engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM `plant_dim`"))
    print(result.keys())
    print(pd.DataFrame(result))
stmt = """
SELECT ld.source, ld.signal, ld.pathogen, ld.provider, ld.normalization, td.source, td.signal, td.pathogen, td.provider, td.normalization
FROM `wastewater_granular_load` AS ld
LEFT JOIN `signal_dim` AS td
    USING (`source`, `signal`, `pathogen`, `provider`, `normalization`)
"""
# WHERE td.`source` IS NULL
print(stmt)
with database.engine.connect() as conn:
    result = conn.execute(text(stmt))
    print(result.keys())
    for row in result:
        print(row)

with database.engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM `sample_site_dim`"))
    print(result.keys())
    for row in result:
        print(row)
toClaa = """
INSERT INTO plant_dim (`wwtp_jurisdiction`, `wwtp_id`)
    SELECT DISTINCT ld.wwtp_jurisdiction, ld.wwtp_id
    FROM `wastewater_granular_load` AS ld
    LEFT JOIN `plant_dim` AS td
        USING (`wwtp_jurisdiction`, `wwtp_id`)
    WHERE td.`wwtp_id` IS NULL
"""
with database.engine.connect() as conn:
    result = conn.execute(text(toClaa))
with database.engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM `plant_dim`"))
    print(result.keys())
    for row in result:
        print(row)

toCall = f"""
            SELECT DISTINCT ld.sample_loc_specify, ld.sample_method, ft.plant_id
            FROM `wastewater_granular_load` AS ld
            LEFT JOIN `sample_site_dim` AS td
                USING (`sample_loc_specify`, `sample_method`)
            LEFT JOIN `plant_dim` AS ft
                USING (`wwtp_jurisdiction`, `wwtp_id`)
                        WHERE td.`sample_method` IS NULL
"""
print(toCall)
with database.engine.connect() as conn:
    result = conn.execute(text(toCall))
    print(result.cursor.description)
    print(result.keys())
    for row in result:
        print(row)

df_tiny = df.sample(n=20, random_state=1)
df_tiny2 = df.sample(n=20, random_state=2)
df_tiny
df_tiny.to_sql(
    name=["wastewater_granular_full", "plant_dim"],
    con=engine,
    if_exists="append",
    method="multi",
    index=False,
)


# roughly what needs to happen (unsure which language/where):
# 1. SELECT * FROM latest
# 2. compare and drop if it's redundant
# 3. assign the various id's (I think this may be handled by the load datatable)
# 4. split into seprate tables
# 5. INSERT the new rows
# 6? aggregate to state level (maybe from load,)
# 7. delete load
# Ok but actually, I will also be writing a separate aux table, that shouldn't need a separate load table and will happen separately
# Also, I am going to need to dedupe, which I guess can happen during the join
