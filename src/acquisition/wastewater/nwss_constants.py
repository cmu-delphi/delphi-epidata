import pandas as pd

from os import path

WASTEWATER_DDL = path.join(path.dirname(__file__), "../../ddl/wastewater.sql")

CONCENTRATION_SIGNALS = ["pcr_conc_lin"]
METRIC_SIGNALS = ["detect_prop_15d", "percentile", "ptc_15d", "population_served"]

TYPE_DICT_CONC = {key: float for key in CONCENTRATION_SIGNALS}
TYPE_DICT_CONC.update(
    {"date": "datetime64[ns]", "key_plot_id": str, "normalization": str}
)
TYPE_DICT_METRIC = {key: float for key in METRIC_SIGNALS}

SIG_DIGITS = 4

TYPE_DICT_METRIC.update(
    {
        "key_plot_id": str,
        "date_start": "datetime64[ns]",
        "date_end": "datetime64[ns]",
        "first_sample_date": "datetime64[ns]",
        "wwtp_jurisdiction": "category",
        "wwtp_id": "Int32",
        "reporting_jurisdiction": "category",
        "sample_location": "category",
        "county_names": "category",
        "county_fips": "category",
        "population_served": float,
        "sampling_prior": bool,
        "sample_location_specify": "Int32",
    }
)
KEY_PLOT_NAMES = [
    "provider",
    "wwtp_jurisdiction",
    "wwtp_id",
    "sample_location",
    "sample_location_specify",
    "sample_method",
]
KEY_PLOT_TYPES = {
    "provider": "category",
    "wwtp_jurisdiction": "category",
    "wwtp_id": "Int32",
    "sample_location": "category",
    "sample_location_specify": "Int32",
    "sample_method": "category",
}
AUX_INFO_COLUMNS = [
    "key_plot_id",
    "wwtp_jurisdiction",
    "wwtp_id",
    "reporting_jurisdiction",
    "sample_location",
    "sample_location_specify",
    "sampling_prior",
    "first_sample_date",
]
COUNTY_INFO = [
    "county_names",
    "county_fips",
]

TIME_SPANNED = pd.Timedelta(14, unit="days")
