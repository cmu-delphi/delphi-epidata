"""Column mapping tuple used by covid_hosp, matching columns in the CSV files and SQL database."""

# standard library
from collections import namedtuple

Columndef = namedtuple("Columndef", "csv_name sql_name dtype")
