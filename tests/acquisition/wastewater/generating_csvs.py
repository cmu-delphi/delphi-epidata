# these don't need to be run, but are kept as a recording of how these csv's were generated
import pandas as pd
import os

test_data = "../../../testdata/acquisition/wastewater/"
df_read_first = pd.read_csv(
    os.path.join(test_data, "nwss_test_data.csv"),
    index_col=0,
    parse_dates=["reference_date", "version", "value_updated_timestamp"],
)
# as if written 2 days later, with 5 entries that ~ correspond to the same days
# but varying changes to the values and versions
df_read_second = pd.read_csv(
    os.path.join(test_data, "nwss_test_data_second_round.csv"),
    index_col=0,
    parse_dates=["reference_date", "version", "value_updated_timestamp"],
)


signal_columns = ["source", "signal", "pathogen", "provider", "normalization"]
first_signal_values = (
    df_read_first.loc[:, signal_columns]
    .drop_duplicates()
    .sort_values(by=signal_columns)
)
first_signal_values.to_csv(
    os.path.join(test_data, "first_signal_values.csv"), index=False
)
second_signal_values = (
    df_read_second.loc[:, signal_columns]
    .drop_duplicates()
    .sort_values(by=signal_columns)
)
# this is a hack to get a set difference (removing the values in first_signal_values from second_signal_values)
only_new = pd.concat(
    [
        second_signal_values,
        first_signal_values,
        first_signal_values,
    ]
).drop_duplicates(keep=False)
only_new.to_csv(os.path.join(test_data, "added_signal_values.csv"), index=False)


# similar idea, but for the rows in site join plant
site_columns = [
    "wwtp_jurisdiction",
    "wwtp_id",
    "sample_loc_specify",
    "sample_method",
]
first_site_values = (
    df_read_first.loc[:, site_columns].drop_duplicates().sort_values(by=site_columns)
)
first_site_values.to_csv(os.path.join(test_data, "first_site_values.csv"), index=False)
second_site_values = (
    df_read_second.loc[:, site_columns].drop_duplicates().sort_values(by=site_columns)
)
# this is a hack to get a set difference (removing the values in first_site_values from second_site_values)
only_new = pd.concat(
    [
        second_site_values,
        first_site_values,
        first_site_values,
    ]
).drop_duplicates(keep=False)
only_new.to_csv(os.path.join(test_data, "added_site_values.csv"), index=False)
df_read_first.dtypes
