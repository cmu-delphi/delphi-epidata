# standard library
import re
import datetime

# first party
from delphi.utils.epidate import EpiDate

# helper funs for checking expectations, throwing exceptions on violations:
def expect_value_eq(encountered, expected, mismatch_format):
  if encountered != expected:
    raise Exception([mismatch_format.format(expected), encountered])
def expect_result_eq(f, value, expected, mismatch_format):
  result = f(value)
  if result != expected:
    raise Exception([mismatch_format.format(expected), result, value])
def expect_value_in(encountered, expected_candidates, mismatch_format):
  if encountered not in expected_candidates:
    raise Exception([mismatch_format.format(expected_candidates), encountered])
def expect_result_in(f, value, expected_candidates, mismatch_format):
  result = f(value)
  if result not in expected_candidates:
    raise Exception([mismatch_format.format(expected_candidates), result, value])
def expect_str_contains(encountered, regex, mismatch_format):
  if re.search(regex, encountered) is None:
    raise Exception([mismatch_format.format(regex), encountered])

# helper fun used with expect_* funs to check value of <obj>.dtype.kind:
def dtype_kind(numpy_like):
  return numpy_like.dtype.kind

# helper fun used to convert season string ("YYYY-YY" or "YYYY-YYYY") and
# "Week" string (strptime format "%d-%b") to the corresponding epiweek; assumes
# by default that dates >= 1-Aug correspond to weeks of the first year:
def season_db_to_epiweek(season_str, db_date_str, first_db_date_of_season_str="1-Aug"):
  year_strs = season_str.split("-")
  first_year = int(year_strs[0])
  second_year = first_year + 1
  # FIXME check/enforce locale
  first_date_of_season = datetime.datetime.strptime(first_db_date_of_season_str+"-"+str(first_year), "%d-%b-%Y").date()
  date_using_first_year = datetime.datetime.strptime(db_date_str+"-"+str(first_year), "%d-%b-%Y").date()
  date_using_second_year = datetime.datetime.strptime(db_date_str+"-"+str(second_year), "%d-%b-%Y").date()
  date = date_using_first_year if date_using_first_year >= first_date_of_season else date_using_second_year
  epiweek = EpiDate(date.year, date.month, date.day).get_ew()
  return epiweek
