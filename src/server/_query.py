from ._db import metadata
from typing import Optional, List, Union, Tuple
from ._validate import DateRange

def date_string(value: int) -> str:
    # converts a date integer (YYYYMMDD) into a date string (YYYY-MM-DD)
    # $value: the date as an 8-digit integer
    year = int(value / 10000) % 10000
    month = int(value / 100) % 100
    day = value % 100
    return "{0:04d}-{1:02d}-{2:%02d}".format(year, month, day)


def filter_dates(field: str, dates: Optional[List[DateRange]]) -> str:
    """
    builds a SQL expression to filter values/ranges of dates
    :param field: name of the field to filter
    :param data: array of date values/ranges
    """
    if not dates:
        return None
    
    $filter = null;
    foreach($dates as $date) {
        if($filter === null) {
        $filter = '';
        } else {
        $filter .= ' OR ';
        }
        if(is_array($date)) {
        // range of values
        $first = date_string($date[0]);
        $last = date_string($date[1]);
        $filter .= "({$field} BETWEEN '{$first}' AND '{$last}')";
        } else {
        // single value
        $date = date_string($date);
        $filter .= "({$field} = '{$date}')";
        }
    }
    return $filter;
    }

// builds a SQL expression to filter values/ranges of integers (ex: epiweeks)
//   $field: name of the field to filter
//   $values: array of integer values/ranges
function filter_integers($field, $values) {
  $filter = null;
  foreach($values as $value) {
    if($filter === null) {
      $filter = '';
    } else {
      $filter .= ' OR ';
    }
    if(is_array($value)) {
      // range of values
      $filter .= "({$field} BETWEEN {$value[0]} AND {$value[1]})";
    } else {
      // single value
      $filter .= "({$field} = {$value})";
    }
  }
  return $filter;
}

// builds a SQL expression to filter strings (ex: locations)
//   $field: name of the field to filter
//   $values: array of values
function filter_strings($field, $values) {
  global $dbh;
  $filter = null;
  foreach($values as $value) {
    if($filter === null) {
      $filter = '';
    } else {
      $filter .= ' OR ';
    }
    if(is_array($value)) {
      // range of values
      $value0 = mysqli_real_escape_string($dbh, $value[0]);
      $value1 = mysqli_real_escape_string($dbh, $value[1]);
      $filter .= "({$field} BETWEEN '{$value0}' AND '{$value1}')";
    } else {
      // single value
      $value = mysqli_real_escape_string($dbh, $value);
      $filter .= "({$field} = '{$value}')";
    }
  }
  return $filter;
}