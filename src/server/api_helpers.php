<?php
// load database connection parameters
require_once(__DIR__ . '/database_config.php');

// connects to the database
function database_connect() {
  global $DATABASE_CONFIG;
  $host = $DATABASE_CONFIG['host'];
  $port = $DATABASE_CONFIG['port'];
  $username = Secrets::$db['epi'][0];
  $password = Secrets::$db['epi'][1];
  $database = 'epidata';
  // bind database handle to global; could also pass around
  global $dbh;
  $dbh = mysqli_connect($host, $username, $password, $database, $port);
  return $dbh;
}

// returns true if all fields are present in the request
//   $output: output array to set an error message
//   $values: an array of field names
function require_all(&$output, $values) {
  foreach($values as $value) {
    if(!isset($_REQUEST[$value])) {
      $output['message'] = 'missing parameter: need [' . $value . ']';
      return false;
    }
  }
  return true;
}

// returns true if any fields are present in the request
//   $output: output array to set an error message
//   $values: an array of field names
function require_any(&$output, $values) {
  foreach($values as $value) {
    if(isset($_REQUEST[$value])) {
      return true;
    }
  }
  $output['message'] = 'missing parameter: need one of [' . implode(', ', $values) . ']';
  return false;
}

// stores the epidata array as part of the output object, setting the result and message fields appropriately
//   $output: the output array
//   $epidata: epidata fetched for the request
function store_result(&$output, &$epidata) {
  global $MAX_RESULTS;
  if($epidata !== null) {
    // success!
    $output['epidata'] = $epidata;
    if(count($epidata) < $MAX_RESULTS) {
      $output['result'] = 1;
      $output['message'] = 'success';
    } else {
      $output['result'] = 2;
      $output['message'] = 'too many results, data truncated';
    }
  } else {
    // failure
    $output['result'] = -2;
    $output['message'] = 'no results';
  }
}

// converts a date integer (YYYYMMDD) into a date string (YYYY-MM-DD)
//   $value: the date as an 8-digit integer
function date_string($value) {
  $year = intval($value / 10000) % 10000;
  $month = intval($value / 100) % 100;
  $day = $value % 100;
  return sprintf('%04d-%02d-%02d', $year, $month, $day);
}

// builds a SQL expression to filter values/ranges of dates
//   $field: name of the field to filter
//   $dates: array of date values/ranges
function filter_dates($field, $dates) {
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

// executes a query, casts the results, and returns an array of the data
// the number of results is limited to $MAX_RESULTS
//   $query (required): a SQL query string
//   $epidata (required): an array for storing the data
//   $fields_string (optional): an array of names of string fields
//   $fields_int (optional): an array of names of integer fields
//   $fields_float (optional): an array of names of float fields
function execute_query($query, &$epidata, $fields_string, $fields_int, $fields_float) {
  global $dbh;
  global $MAX_RESULTS;
  $result = mysqli_query($dbh, $query . " LIMIT {$MAX_RESULTS}");
  error_log("Query: ".$query);
  if (!$result) {
    error_log(sprintf("Error: %s\n",mysqli_error($dbh)));
    return;
  }
  while($row = mysqli_fetch_array($result)) {
    if(count($epidata) < $MAX_RESULTS) {
      $values = array();
      if($fields_string !== null) {
        foreach($fields_string as $field) {
          $values[$field] = $row[$field];
        }
      }
      if($fields_int !== null) {
        foreach($fields_int as $field) {
          if($row[$field] === null) {
            $values[$field] = null;
          } else {
            $values[$field] = intval($row[$field]);
          }
        }
      }
      if($fields_float !== null) {
        foreach($fields_float as $field) {
          if($row[$field] === null) {
            $values[$field] = null;
          } else {
            $values[$field] = floatval($row[$field]);
          }
        }
      }
      array_push($epidata, $values);
    }
  }
}

// extracts an array of values and/or ranges from a string
//   $str: the string to parse
//   $type:
//     - 'int': interpret dashes as ranges, cast values to integers
//     - 'ordered_string': interpret dashes as ranges, keep values as strings
//     - otherwise: ignore dashes, keep values as strings
function extract_values($str, $type) {
  if($str === null || strlen($str) === 0) {
    // nothing to do
    return null;
  }
  // whether to parse a value with a dash as a range of values
  $shouldParseRange = $type === 'int' || $type === 'ordered_string';
  // maintain a list of values and/or ranges
  $values = array();
  // split on commas and loop over each entry, which could be either a single value or a range of values
  $parts = explode(',', $str);
  foreach($parts as $part) {
    if($shouldParseRange && strpos($part, '-') !== false) {
      // split on the dash
      $range = explode('-', $part);
      // get the range endpoints
      $first = $range[0];
      $last = $range[1];
      if ($type === 'int') {
        $first = intval($first);
        $last = intval($last);
      }
      if($last === $first) {
        // the first and last numbers are the same, just treat it as a singe value
        array_push($values, $first);
      } else if($last > $first) {
        // add the range as an array
        array_push($values, array($first, $last));
      } else {
        // the range is inverted, this is an error
        return null;
      }
    } else {
      // this is a single value
      if($type === 'int') {
        // cast to integer
        $value = intval($part);
      } else {
        // interpret the string literally
        $value = $part;
      }
      // add the extracted value to the list
      array_push($values, $value);
    }
  }
  // success, return the list
  return $values;
}

// give a comma-separated, quoted list of states in an HHS or Census region
function get_region_states($region) {
  switch($region) {
    case 'hhs1': return "'VT', 'CT', 'ME', 'MA', 'NH', 'RI'";
    case 'hhs2': return "'NJ', 'NY'";
    case 'hhs3': return "'DE', 'DC', 'MD', 'PA', 'VA', 'WV'";
    case 'hhs4': return "'AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'TN', 'SC'";
    case 'hhs5': return "'IL', 'IN', 'MI', 'MN', 'OH', 'WI'";
    case 'hhs6': return "'AR', 'LA', 'NM', 'OK', 'TX'";
    case 'hhs7': return "'IA', 'KS', 'MO', 'NE'";
    case 'hhs8': return "'CO', 'MT', 'ND', 'SD', 'UT', 'WY'";
    case 'hhs9': return "'AZ', 'CA', 'HI', 'NV'";
    case 'hhs10': return "'AK', 'ID', 'OR', 'WA'";
    case 'cen1': return "'CT', 'ME', 'MA', 'NH', 'RI', 'VT'";
    case 'cen2': return "'NJ', 'NY', 'PA'";
    case 'cen3': return "'IL', 'IN', 'MI', 'OH', 'WI'";
    case 'cen4': return "'IA', 'KS', 'MN', 'MO', 'NE', 'ND', 'SD'";
    case 'cen5': return "'DE', 'DC', 'FL', 'GA', 'MD', 'NC', 'SC', 'VA', 'WV'";
    case 'cen6': return "'AL', 'KY', 'MS', 'TN'";
    case 'cen7': return "'AR', 'LA', 'OK', 'TX'";
    case 'cen8': return "'AZ', 'CO', 'ID', 'MT', 'NV', 'NM', 'UT', 'WY'";
    case 'cen9': return "'AK', 'CA', 'HI', 'OR', 'WA'";
  }
  return null;
}

function record_analytics($source, $data) {
  global $dbh;
  $ip = mysqli_real_escape_string($dbh, isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '');
  $ua = mysqli_real_escape_string($dbh, isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : '');
  $source = mysqli_real_escape_string($dbh, isset($source) ? $source : '');
  $result = intval($data['result']);
  $num_rows = intval(isset($data['epidata']) ? count($data['epidata']) : 0);
  mysqli_query($dbh, "INSERT INTO `api_analytics` (`datetime`, `ip`, `ua`, `source`, `result`, `num_rows`) VALUES (now(), '{$ip}', '{$ua}', '{$source}', {$result}, {$num_rows})");
}


?>
