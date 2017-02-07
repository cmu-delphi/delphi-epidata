<?php
/*
===============
=== Purpose ===
===============

An API for DELPHI's epidemiological data.

Documentation and sample code are on GitHub:
https://github.com/cmu-delphi/delphi-epidata


=======================
=== Data Dictionary ===
=======================

See also:
  - load_epidata_fluview.py
  - old/gft_update.py
  - twitter_update.py
  - wiki.py
  - taiwan_update.py
  - submission_loader.py
  - ght_update.py
  - signal_update.py
  - sensor_update.py
  - nowcast.py
  - cdc_extract.py
  - flusurv_update.py

Unlike most of the other data sources, the state-level ILINet data isn't
updated automatically. The data was obtained around 2015-09-10 from the various
states' websites, linked here: http://www.cdc.gov/flu/weekly/
This data was re-obtained around June 2016, and uploaded 2016-11-14. The
process is lossy, and so the two version don't entirely agree. Because of this,
we now also store a version tag with the data.
The `state_ili` table stores this data:
+---------+-------------+------+-----+---------+----------------+
| Field   | Type        | Null | Key | Default | Extra          |
+---------+-------------+------+-----+---------+----------------+
| id      | int(11)     | NO   | PRI | NULL    | auto_increment |
| epiweek | int(11)     | NO   | MUL | NULL    |                |
| state   | varchar(12) | NO   | MUL | NULL    |                |
| ili     | double      | NO   |     | NULL    |                |
| version | int(11)     | NO   | MUL | NULL    |                |
+---------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
epiweek: the epiweek during which the data was collected
state: two-letter U.S. state abbreviation
ili: percent ILI
version: 1 => 2015-09; 2 => 2016-06

Similarly, we received a one-time data dump from the CDC containing true
state-level ILINet data. The data was received on 2016-02-17 and uploaded to
the database on 2016-02-18. This data is not to be distributed outside of
the DELPHI group---and maybe not even within the group---without prior
discussion.
The `fluview_state` table stores this data (similar to the `fluview` table):
+---------------+---------+------+-----+---------+----------------+
| Field         | Type    | Null | Key | Default | Extra          |
+---------------+---------+------+-----+---------+----------------+
| id            | int(11) | NO   | PRI | NULL    | auto_increment |
| epiweek       | int(11) | NO   | MUL | NULL    |                |
| state         | char(2) | NO   | MUL | NULL    |                |
| num_ili       | int(11) | YES  |     | NULL    |                |
| num_patients  | int(11) | YES  |     | NULL    |                |
| num_providers | int(11) | YES  |     | NULL    |                |
| ili           | double  | YES  |     | NULL    |                |
| num_age_0     | int(11) | YES  |     | NULL    |                |
| num_age_1     | int(11) | YES  |     | NULL    |                |
| num_age_2     | int(11) | YES  |     | NULL    |                |
| num_age_3     | int(11) | YES  |     | NULL    |                |
| num_age_4     | int(11) | YES  |     | NULL    |                |
| num_age_5     | int(11) | YES  |     | NULL    |                |
+---------------+---------+------+-----+---------+----------------+
id: unique identifier for each record
epiweek: the epiweek during which the data was collected
state: two-letter U.S. state abbreviation
num_ili: the number of ILI cases (numerator)
num_patients: the total number of patients (denominator)
num_providers: the number of reporting healthcare providers
ili: percent ILI
num_age_0: number of cases in ages 0-4
num_age_1: number of cases in ages 5-24
num_age_2: number of cases in ages 25-64
num_age_3: number of cases in ages 25-49
num_age_4: number of cases in ages 50-64
num_age_5: number of cases in ages 65+

Google stopped producing GFT after 2015w32, so the table is no longer being
updated. For convenience, the data dictionary from the GFT updater is copied
here:
`gft` is the table where the data is stored.
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| epiweek  | int(11)     | NO   | MUL | NULL    |                |
| location | varchar(64) | NO   | MUL | NULL    |                |
| num      | int(11)     | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
epiweek: the epiweek during which the data was collected
location: where the data was collected (region, state, or city)
num: the value, roughly corresponding to ILI * 1000


=================
=== Changelog ===
=================

2017-02-07
  + added source `flusurv`
2016-11-15
  + support `version` for data from `ilinet_state`
2016-11-12
  * remove hardcoded secrets
2016-04-16
  * function `get_region_states` instead of hardcoded arrays
  * use new cdc data from table `cdc_extract`
2016-04-09
  * filter out unreasonable twitter rows
2016-04-07
  + added sources `cdc` and `sensors`
2016-04-06
  + added source `stateili`
2016-04-02
  + census regions for source `twitter`
2016-02-18
  + include more fields from `fluview` in `ilinet`
  + include optional `auth` parameter for CDC-provided state-level ILI
  * properly handle (don't cast) SQL `NULL` in `execute_query`
2016-01-18
  + added source `meta`
2015-12-15
  + added source `nowcast`
2015-12-11
  + added source `signals`
2015-12-03
  * move passwords to $AUTH variable
  + added source `ght`
2015-11-19
  * using the new `forecasts` table for source `delphi`
2015-10-02
  + source `delphi` uses the `forecasts` table
2015-09-15
  + static placeholder for source `delphi`
2015-09-14
  + storing basic analytics in table `api_analytics`
  * patched SQL injection vulnerability in `get_nidss_dengue`
  * fixed a collation problem with the `nidss_dengue` table (see https://stackoverflow.com/questions/1008287/illegal-mix-of-collations-mysql-error)
2015-09-11
  + added source `ilinet`
2015-09-04
  + in `wiki`, added field `value` (1e6 * count / total)
2015-08-20
  + added source `nidss_dengue`
  * renamed source `nidss` to `nidss_flu`
2015-08-12
  * fixed SQL typo for daily wiki
2015-08-11
  + using `wiki_meta` for better performance and total hits
2015-08-10
  + added source `nidss`
2015-08-04
  + added message for invalid `auth`
2015-07-31
  + added `auth` parameter for twitter
2015-06-24
  + fully supporting twitter dataset
  + fully supporting wiki dataset
  + several utility methods to reduce duplicated code
  * heavy refactoring, additional documentation
2015-06-23
  + query fluview by specific lag
  + finished GFT support
  * rearranged get_fluview parameters
2015-06-08
  + basic support for the GFT dataset
2015-06-04
  + enabled multiple values and ranges
  + optional sort field
  + more documentation
2015-06-01
  * changes to fluview parameter names
  - removed all authentication code (most was commented out already)
2014-??-??
  * original version
*/

// secrets
require_once('/var/www/html/secrets.php');

// passwords
$AUTH = array(
  'twitter'  => Secrets::$api['twitter'],
  'ght'      => Secrets::$api['ght'],
  'signals'  => Secrets::$api['signals'],
  'ilinet'   => Secrets::$api['ilinet'],
  'stateili' => Secrets::$api['stateili'],
  'cdc'      => Secrets::$api['cdc'],
  'sensors'  => Secrets::$api['sensors']
);

// result limit, ~10 years of daily data
$MAX_RESULTS = 3650;

// connects to the database
function database_connect() {
  $host = 'localhost';
  $port = 3306;
  $username = Secrets::$db['epi'][0];
  $password = Secrets::$db['epi'][1];
  $database = 'epidata';
  $dbh = mysql_connect("{$host}:{$port}", $username, $password);
  if($dbh) {
    mysql_select_db($database, $dbh);
  }
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
//   $epiweeks: array of integer values/ranges
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
  $filter = null;
  foreach($values as $value) {
    if($filter === null) {
      $filter = '';
    } else {
      $filter .= ' OR ';
    }
    $value = mysql_real_escape_string($value);
    $filter .= "({$field} = '{$value}')";
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
  global $MAX_RESULTS;
  $result = mysql_query($query . " LIMIT {$MAX_RESULTS}");
  while($row = mysql_fetch_array($result)) {
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
//   $type: the data type ('int' for integers, otherwise assumes string)
function extract_values($str, $type) {
  if($str === null || strlen($str) === 0) {
    // nothing to do
    return null;
  }
  // maintain a list of values and/or ranges
  $values = array();
  // split on commas and loop over each entry, which could be either a single value or a range of values
  $parts = explode(',', $str);
  foreach($parts as $part) {
    if($type === 'int' && strpos($part, '-') !== false) {
      // split on the dash
      $range = explode('-', $part);
      // get the range endpoints
      $first = intval($range[0]);
      $last = intval($range[1]);
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

// queries the `fluview` table
//   $epiweeks (required): array of epiweek values/ranges
//   $regions (required): array of region names
//   $issues (optional): array of epiweek values/ranges
//     overrides $lag
//     default: most recent issue
//   $lag (optional): number of weeks between each epiweek and its issue
//     overridden by $issues
//     default: most recent issue
//   $sort (optional): field order and direction
//     default: sort is 'ERI'
function get_fluview($epiweeks, $regions, $issues, $lag, $sort) {
  // basic query info
  $table = '`fluview` fv';
  $fields = "fv.`release_date`, fv.`issue`, fv.`epiweek`, fv.`region`, fv.`lag`, fv.`num_ili`, fv.`num_patients`, fv.`num_providers`, fv.`wili`, fv.`ili`, fv.`num_age_0`, fv.`num_age_1`, fv.`num_age_2`, fv.`num_age_3`, fv.`num_age_4`, fv.`num_age_5`";
  // sorting by region is tricky
  // the natural sort order would be: nat, hhs1, hhs10, hhs2, ..., hhs9
  // but it makes more sense to be: nat, hhs1, hhs2, ..., hhs9, hhs10
  // this is one way to do that
  $regionSort = "(substring(concat(fv.`region`, '0'), 4) + 0)";
  $order = "fv.`epiweek` ASC, {$regionSort} ASC, fv.`issue` ASC";
  if($sort !== null) {
    // override the default sort
    $order = null;
    // make sure the three fields (issue, region, epiweek) are all present
    $key = strtolower($sort);
    $posIssue = strpos($key, 'i');
    $posEpiweek = strpos($key, 'e');
    $posRegion = strpos($key, 'r');
    if($posIssue === False || $posEpiweek === False || $posRegion === False || strlen($key) !== 3) {
      // unknown fields
      return null;
    }
    // decode the sort string
    for($i = 0; $i < strlen($key); $i++) {
      if($order === null) {
        $order = '';
      } else {
        $order .= ', ';
      }
      switch(substr($sort, $i, 1)) {
        case 'i': $order .= 'fv.`issue` DESC'; break;
        case 'I': $order .= 'fv.`issue` ASC'; break;
        case 'e': $order .= 'fv.`epiweek` DESC'; break;
        case 'E': $order .= 'fv.`epiweek` ASC'; break;
        case 'r': $order .= "{$regionSort} DESC"; break;
        case 'R': $order .= "{$regionSort} ASC"; break;
      }
    }
  }
  // build the epiweek filter
  $condition_epiweek = filter_integers('fv.`epiweek`', $epiweeks);
  // build the region filter
  $condition_region = filter_strings('fv.`region`', $regions);
  if($issues !== null) {
    // build the issue filter
    $condition_issue = filter_integers('fv.`issue`', $issues);
    // final query using specific issues
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_issue}) ORDER BY {$order}";
  } else if($lag !== null) {
    // build the lag filter
    $condition_lag = "(fv.`lag` = {$lag})";
    // final query using lagged issues
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_lag}) ORDER BY {$order}";
  } else {
    // final query using most recent issues
    $subquery = "(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) GROUP BY `epiweek`, `region`) x";
    $condition = "x.`max_issue` = fv.`issue` AND x.`epiweek` = fv.`epiweek` AND x.`region` = fv.`region`";
    $query = "SELECT {$fields} FROM {$table} JOIN {$subquery} ON {$condition} ORDER BY {$order}";
  }
  // get the data from the database
  $epidata = array();
  $fields_string = array('release_date', 'region');
  $fields_int = array('issue', 'epiweek', 'lag', 'num_ili', 'num_patients', 'num_providers', 'num_age_0', 'num_age_1', 'num_age_2', 'num_age_3', 'num_age_4', 'num_age_5');
  $fields_float = array('wili', 'ili');
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `flusurv` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of locations names
//   $issues (optional): array of epiweek values/ranges
//     overrides $lag
//     default: most recent issue
//   $lag (optional): number of weeks between each epiweek and its issue
//     overridden by $issues
//     default: most recent issue
function get_flusurv($epiweeks, $locations, $issues, $lag) {
  // basic query info
  $table = '`flusurv` fs';
  $fields = "fs.`release_date`, fs.`issue`, fs.`epiweek`, fs.`location`, fs.`lag`, fs.`rate_age_0`, fs.`rate_age_1`, fs.`rate_age_2`, fs.`rate_age_3`, fs.`rate_age_4`, fs.`rate_overall`";
  $order = "fs.`epiweek` ASC, fs.`location` ASC, fs.`issue` ASC";
  // build the epiweek filter
  $condition_epiweek = filter_integers('fs.`epiweek`', $epiweeks);
  // build the location filter
  $condition_location = filter_strings('fs.`location`', $locations);
  if($issues !== null) {
    // build the issue filter
    $condition_issue = filter_integers('fs.`issue`', $issues);
    // final query using specific issues
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_location}) AND ({$condition_issue}) ORDER BY {$order}";
  } else if($lag !== null) {
    // build the lag filter
    $condition_lag = "(fs.`lag` = {$lag})";
    // final query using lagged issues
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_location}) AND ({$condition_lag}) ORDER BY {$order}";
  } else {
    // final query using most recent issues
    $subquery = "(SELECT max(`issue`) `max_issue`, `epiweek`, `location` FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_location}) GROUP BY `epiweek`, `location`) x";
    $condition = "x.`max_issue` = fs.`issue` AND x.`epiweek` = fs.`epiweek` AND x.`location` = fs.`location`";
    $query = "SELECT {$fields} FROM {$table} JOIN {$subquery} ON {$condition} ORDER BY {$order}";
  }
  // get the data from the database
  $epidata = array();
  $fields_string = array('release_date', 'location');
  $fields_int = array('issue', 'epiweek', 'lag');
  $fields_float = array('rate_age_0', 'rate_age_1', 'rate_age_2', 'rate_age_3', 'rate_age_4', 'rate_overall');
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `fluview`, `fluview_state`, and `state_ili` tables
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of region/state names
//   $version (optional): specific version of `state_ili` rows to use (average by default)
//   $authorized (optional): whether to include CDC-provided values
function get_ilinet($epiweeks, $locations, $version, $authorized) {
  // possibly include protected data
  $fluview_state = $authorized === true;
  // pass national and regional locations to the fluview function
  $fluview_regions = array();
  $ilinet_states = array();
  foreach ($locations as $location) {
    // if the location label is more than two characters, it can't be a state
    if(strlen($location) > 2) {
      array_push($fluview_regions, $location);
    } else {
      array_push($ilinet_states, $location);
    }
  }
  // `state_ili` version specifier (will use average of all versions by default)
  if($version !== null) {
    $version = intval($version);
  }
  // initialize the data array
  $epidata = array();
  // get the national/regional data
  if(count($fluview_regions) > 0) {
    // use the most recent issue (most stable values)
    $temp = get_fluview($epiweeks, $fluview_regions);
    if($temp !== null) {
      foreach($temp as $row) {
        // map fluview fields to ilinet fields
        array_push($epidata, array(
          'location' => $row['region'],
          'epiweek' => $row['epiweek'],
          'num_ili' => $row['num_ili'],
          'num_patients' => $row['num_patients'],
          'num_providers' => $row['num_providers'],
          'num_age_0' => $row['num_age_0'],
          'num_age_1' => $row['num_age_1'],
          'num_age_2' => $row['num_age_2'],
          'num_age_3' => $row['num_age_3'],
          'num_age_4' => $row['num_age_4'],
          'num_age_5' => $row['num_age_5'],
          'ili' => $row['ili'],
          'wili' => $row['wili'],
        ));
      }
    }
  }
  // get the state data
  if(count($ilinet_states) > 0) {
    // basic query info
    $fields_string = array('location');
    $fields_int = array('epiweek', 'num_ili', 'num_patients', 'num_providers', 'num_age_0', 'num_age_1', 'num_age_2', 'num_age_3', 'num_age_4', 'num_age_5');
    $fields_float = array('ili', 'ili_estimate');
    $order = 'si.`epiweek` ASC, si.`state` ASC';
    if($fluview_state) {
      // need a full outer join to combine `fluview_state` and `state_ili`
      $common_fields = "
        f.`ili` `fili`,
        s.`ili` `sili`,
        f.`num_ili`,
        f.`num_patients`,
        f.`num_providers`,
        f.`num_age_0`,
        f.`num_age_1`,
        f.`num_age_2`,
        f.`num_age_3`,
        f.`num_age_4`,
        f.`num_age_5`
      ";
      // build the epiweek filters
      $left_epiweek = filter_integers('f.`epiweek`', $epiweeks);
      $right_epiweek = filter_integers('s.`epiweek`', $epiweeks);
      // build the state filters
      $left_state = filter_strings('f.`state`', $ilinet_states);
      $right_state = filter_strings('s.`state`', $ilinet_states);
      // create a derived view of `state_ili` using the specified version
      $condition_version = $version === null ? 'TRUE' : "s.`version` = {$version}";
      $state_ili_versioned = "
        SELECT
          s.`epiweek`, s.`state`, avg(s.`ili`) `ili`
        FROM
          `state_ili` s
        WHERE
          ({$right_epiweek}) AND ({$right_state}) AND ({$condition_version})
        GROUP BY
          s.`epiweek`, s.`state`
      ";
      // left join
      $left = "
        SELECT
          f.`epiweek`,
          f.`state`,
          {$common_fields}
        FROM
          `fluview_state` f
        LEFT JOIN
          ({$state_ili_versioned}) s
        ON
          s.`state` = f.`state` AND s.`epiweek` = f.`epiweek`
        WHERE
          ({$left_epiweek}) AND ({$left_state})
      ";
      // right join
      $right = "
        SELECT
          s.`epiweek`,
          s.`state`,
          {$common_fields}
        FROM
          `fluview_state` f
        RIGHT JOIN
          ({$state_ili_versioned}) s
        ON
          s.`state` = f.`state` AND s.`epiweek` = f.`epiweek`
        WHERE
          (f.`id` IS NULL) AND ({$right_epiweek}) AND ({$right_state})
      ";
      // emulate outer join with a union (mysql only does inner join)
      $table = "({$left} UNION ALL {$right}) si";
      $fields = 'si.`epiweek`, si.`state` `location`, coalesce(si.`fili`, si.`sili`) `ili`, si.`sili` `ili_estimate`, si.`num_ili`, si.`num_patients`, si.`num_providers`, si.`num_age_0`, si.`num_age_1`, si.`num_age_2`, si.`num_age_3`, si.`num_age_4`, si.`num_age_5`';
      // final query
      $query = "SELECT {$fields} FROM {$table} ORDER BY {$order}";
    } else {
      // only use the `state_ili` table
      $table = '`state_ili` si';
      $fields = 'si.`epiweek`, si.`state` `location`, avg(si.`ili`) `ili`, avg(si.`ili`) `ili_estimate`';
      // build the epiweek filter
      $condition_epiweek = filter_integers('si.`epiweek`', $epiweeks);
      // build the state filter
      $condition_state = filter_strings('si.`state`', $ilinet_states);
      // build the version filter
      $condition_version = $version === null ? 'TRUE' : "si.`version` = {$version}";
      // group by fields
      $group = "si.`epiweek`, si.`state`";
      // final query
      $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_state}) AND ({$condition_version}) GROUP BY {$group} ORDER BY {$order}";
    }
    // get the data from the database
    execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  }
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `state_ili_imputed` table
//   $epiweeks (required): array of epiweek values/ranges
//   states (required): array of state abbreviations
function get_stateili($epiweeks, $states) {
  // basic query info
  $table = '`state_ili_imputed` s';
  $fields = "s.`state`, s.`epiweek`, s.`ili`";
  $order = "s.`epiweek` ASC";
  // build the epiweek filter
  $condition_epiweek = filter_integers('s.`epiweek`', $epiweeks);
  // build the location filter
  $condition_state = filter_strings('s.`state`', $states);
  // final query using specific issues
  $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_state}) ORDER BY {$order}";
  // get the data from the database
  $epidata = array();
  execute_query($query, $epidata, array('state'), array('epiweek'), array('ili'));
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `gft` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of location names
function get_gft($epiweeks, $locations) {
  // basic query info
  $table = '`gft` g';
  $fields = "g.`epiweek`, g.`location`, g.`num`";
  $order = "g.`epiweek` ASC, g.`location` ASC";
  // build the epiweek filter
  $condition_epiweek = filter_integers('g.`epiweek`', $epiweeks);
  // build the location filter
  $condition_location = filter_strings('g.`location`', $locations);
  // final query using specific issues
  $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_location}) ORDER BY {$order}";
  // get the data from the database
  $epidata = array();
  execute_query($query, $epidata, array('location'), array('epiweek', 'num'), null);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `ght` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of location names
//   $query (required): search query or topic ID
function get_ght($epiweeks, $locations, $query) {
  // basic query info
  $table = '`ght` g';
  $fields = "g.`epiweek`, g.`location`, g.`value`";
  $order = "g.`epiweek` ASC, g.`location` ASC";
  // build the epiweek filter
  $condition_epiweek = filter_integers('g.`epiweek`', $epiweeks);
  // build the location filter
  $condition_location = filter_strings('g.`location`', $locations);
  // build the query filter
  $condition_query = filter_strings('g.`query`', array($query));
  // final query using specific issues
  $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_location}) AND ({$condition_query}) ORDER BY {$order}";
  // get the data from the database
  $epidata = array();
  execute_query($query, $epidata, array('location'), array('epiweek'), array('value'));
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `twitter` table
//   $locations (required): array of location names
//   $dates (required): array of date or epiweek values/ranges
//   $resolution (required): either 'daily' or 'weekly'
function get_twitter($locations, $dates, $resolution) {
  // basic query info
  $table = '`twitter` t';
  // build the date filter and set field names
  $fields_string = array('location');
  $fields_int = array('num', 'total');
  $fields_float = array('percent');
  if($resolution === 'daily') {
    $date_field = 't.`date`';
    $date_name = 'date';
    $condition_date = filter_dates($date_field, $dates);
    array_push($fields_string, $date_name);
  } else {
    $date_field = 'yearweek(t.`date`, 6)';
    $date_name = 'epiweek';
    $condition_date = filter_integers($date_field, $dates);
    array_push($fields_int, $date_name);
  }
  $fields = "{$date_field} `{$date_name}`, sum(t.`num`) `num`, sum(t.`total`) `total`, round(100 * sum(t.`num`) / sum(t.`total`), 8) `percent`";
  // for consistency (some rows have low `total`, or `num` > `total`), filter out 2% of rows with highest `percent`
  $condition_filter = 't.`num` / t.`total` <= 0.019';
  // split locations into national/regional/state
  $regions = array();
  $states = array();
  foreach($locations as $location) {
    $location = strtolower($location);
    if(in_array($location, array('nat', 'hhs1', 'hhs2', 'hhs3', 'hhs4', 'hhs5', 'hhs6', 'hhs7', 'hhs8', 'hhs9', 'hhs10', 'cen1', 'cen2', 'cen3', 'cen4', 'cen5', 'cen6', 'cen7', 'cen8', 'cen9'))) {
      array_push($regions, $location);
    } else {
      array_push($states, $location);
    }
  }
  // initialize the epidata array
  $epidata = array();
  // query each region type individually (the data is stored by state, so getting regional data requires some extra processing)
  foreach($regions as $region) {
    $region = mysql_real_escape_string($region);
    if($region === 'nat') {
      // final query for U.S. National
      $query = "SELECT {$fields}, '{$region}' `location` FROM {$table} WHERE ({$condition_filter}) AND ({$condition_date}) GROUP BY {$date_field} ORDER BY {$date_field} ASC";
    } else {
      // build the location filter
      $condition_location = "`state` IN (" . get_region_states($region) . ")";
      // final query for HHS Regions
      $query = "SELECT {$fields}, '{$region}' `location` FROM {$table} WHERE ({$condition_filter}) AND ({$condition_date}) AND ({$condition_location}) GROUP BY {$date_field} ORDER BY {$date_field} ASC";
    }
    // append query results to the epidata array
    execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  }
  // query all states together
  if(count($states) !== 0) {
    // build the location filter
    $condition_location = filter_strings('t.`state`', $states);
    // final query for states
    $query = "SELECT {$fields}, t.`state` `location` FROM {$table} WHERE ({$condition_filter}) AND ({$condition_date}) AND ({$condition_location}) GROUP BY {$date_field}, t.`state` ORDER BY {$date_field} ASC, t.`state` ASC";
    // append query results to the epidata array
    execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  }
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `wiki` table
//   $articles (required): array of article titles
//   $dates (required): array of date or epiweek values/ranges
//   $resolution (required): either 'daily' or 'weekly'
//   $hours (optional): array of hour values/ranges
// if present, $hours determines which counts are used within each day; otherwise all counts are used
// for example, if hours=[4], then only the 4 AM (UTC) stream is returned
function get_wiki($articles, $dates, $resolution, $hours) {
  // basic query info
  // in a few rare instances (~6 total), `total` is unreasonably high; something glitched somewhere, just ignore it
  $table = '`wiki` w JOIN (SELECT * FROM `wiki_meta` WHERE `total` < 100000000) m ON m.`datetime` = w.`datetime`';
  // build the date filter and set field names
  $fields_string = array('article');
  $fields_int = array('count', 'total', 'hour');
  $fields_float = array('value');
  if($resolution === 'daily') {
    $date_field = 'm.`date`';
    $date_name = 'date';
    $condition_date = filter_dates($date_field, $dates);
    array_push($fields_string, $date_name);
  } else {
    $date_field = 'm.`epiweek`';
    $date_name = 'epiweek';
    $condition_date = filter_integers($date_field, $dates);
    array_push($fields_int, $date_name);
  }
  $fields = "{$date_field} `{$date_name}`, w.`article`, sum(w.`count`) `count`, sum(m.`total`) `total`, round(sum(w.`count`) / (sum(m.`total`) * 1e-6), 8) `value`";
  // build the article filter
  $condition_article = filter_strings('w.`article`', $articles);
  if($hours !== null) {
    // filter by specific hours
    $condition_hour = filter_integers('hour(m.`datetime`)', $hours);
    // final query, only taking counts from specific hours of the day
    $query = "SELECT {$fields}, hour(m.`datetime`) `hour` FROM {$table} WHERE ({$condition_date}) AND ({$condition_article}) AND ({$condition_hour}) GROUP BY {$date_field}, w.`article`, hour(m.`datetime`) ORDER BY {$date_field} ASC, w.`article` ASC, hour(m.`datetime`) ASC";
  } else {
    // final query, summing over all hours of the day
    $query = "SELECT {$fields}, -1 `hour` FROM {$table} WHERE ({$condition_date}) AND ({$condition_article}) GROUP BY {$date_field}, w.`article` ORDER BY {$date_field} ASC, w.`article` ASC";
  }
  // get the data from the database
  $epidata = array();
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `nidss_flu` table
//   $epiweeks (required): array of epiweek values/ranges
//   $regions (required): array of region names
//   $issues (optional): array of epiweek values/ranges
//     overrides $lag
//     default: most recent issue
//   $lag (optional): number of weeks between each epiweek and its issue
//     overridden by $issues
//     default: most recent issue
function get_nidss_flu($epiweeks, $regions, $issues, $lag) {
  // basic query info
  $table = '`nidss_flu` nf';
  $fields = "nf.`release_date`, nf.`issue`, nf.`epiweek`, nf.`region`, nf.`lag`, nf.`visits`, nf.`ili`";
  $order = "nf.`epiweek` ASC, nf.`region` ASC, nf.`issue` ASC";
  // build the epiweek filter
  $condition_epiweek = filter_integers('nf.`epiweek`', $epiweeks);
  // build the region filter
  $condition_region = filter_strings('nf.`region`', $regions);
  if($issues !== null) {
    // build the issue filter
    $condition_issue = filter_integers('nf.`issue`', $issues);
    // final query using specific issues
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_issue}) ORDER BY {$order}";
  } else if($lag !== null) {
    // build the lag filter
    $condition_lag = "(nf.`lag` = {$lag})";
    // final query using lagged issues
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_lag}) ORDER BY {$order}";
  } else {
    // final query using most recent issues
    $subquery = "(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) GROUP BY `epiweek`, `region`) x";
    $condition = "x.`max_issue` = nf.`issue` AND x.`epiweek` = nf.`epiweek` AND x.`region` = nf.`region`";
    $query = "SELECT {$fields} FROM {$table} JOIN {$subquery} ON {$condition} ORDER BY {$order}";
  }
  // get the data from the database
  $epidata = array();
  $fields_string = array('release_date', 'region');
  $fields_int = array('issue', 'epiweek', 'lag', 'visits');
  $fields_float = array('ili');
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `nidss_dengue` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of region and/or location names
function get_nidss_dengue($epiweeks, $locations) {
  // build the epiweek filter
  $condition_epiweek = filter_integers('nd.`epiweek`', $epiweeks);
  // get the data from the database
  $epidata = array();
  $fields_string = array('location');
  $fields_int = array('epiweek', 'count');
  foreach($locations as $location) {
    $location = mysql_real_escape_string($location);
    $query = "
      SELECT
        nd2.`epiweek`, nd2.`location`, count(1) `num_locations`, sum(nd2.`count`) `count`
      FROM (
        SELECT
          nd1.`epiweek`, CASE WHEN q.`query` = nd1.`location` THEN nd1.`location` WHEN q.`query` = nd1.`region` THEN nd1.`region` ELSE nd1.`nat` END `location`, nd1.`count`
        FROM (
          SELECT
            `epiweek`, `location`, `region`, 'nationwide' `nat`, `count`
          FROM
            `nidss_dengue` nd
          WHERE {$condition_epiweek}
        ) nd1
        JOIN (
          SELECT
            '{$location}' `query`
        ) q
        ON
          q.`query` IN (nd1.`location`, nd1.`region`, nd1.`nat`)
      ) nd2
      GROUP BY
        nd2.`epiweek`, nd2.`location`
      ";
    execute_query($query, $epidata, $fields_string, $fields_int, null);
  }
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `forecasts` table
//   $system (required): system name
//   $epiweek (required): epiweek on which the forecast was made
function get_forecast($system, $epiweek) {
  // get the data from the database
  $system = mysql_real_escape_string($system);
  $query = "SELECT `system`, `epiweek`, `json` FROM `forecasts` WHERE `system` = '{$system}' AND `epiweek` = {$epiweek}";
  $epidata = array();
  $fields_string = array('system', 'json');
  $fields_int = array('epiweek');
  execute_query($query, $epidata, $fields_string, $fields_int, null);
  // parse forecast data
  if(count($epidata) === 1 && array_key_exists('json', $epidata[0])) {
    $epidata[0]['forecast'] = json_decode($epidata[0]['json']);
    unset($epidata[0]['json']);
  }
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `signals` table
//   $names (required): array of signal names
//   $locations (required): array of location names
//   $epiweeks (required): array of epiweek values/ranges
function get_signals($names, $locations, $epiweeks) {
  // basic query info
  $table = '`signals` s';
  $fields = "s.`name`, s.`location`, s.`epiweek`, s.`value`";
  $order = "s.`epiweek` ASC, s.`name` ASC, s.`location` ASC";
  // data type of each field
  $fields_string = array('name', 'location');
  $fields_int = array('epiweek');
  $fields_float = array('value');
  // build the name filter
  $condition_name = filter_strings('s.`name`', $names);
  // build the location filter
  $condition_location = filter_strings('s.`location`', $locations);
  // build the epiweek filter
  $condition_epiweek = filter_integers('s.`epiweek`', $epiweeks);
  // the query
  $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_name}) AND ({$condition_location}) AND ({$condition_epiweek}) ORDER BY {$order}";
  // get the data from the database
  $epidata = array();
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `cdc_extract` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of location names
function get_cdc($epiweeks, $locations) {
  // basic query info
  $table = '`cdc_extract` c';
  $group = "c.`epiweek`";
  $order = "c.`epiweek` ASC";
  $fields_string = array('location');
  $fields_int = array('epiweek', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7', 'num8', 'total');
  // build the epiweek filter
  $condition_epiweek = filter_integers('c.`epiweek`', $epiweeks);
  // split locations into national/regional/state
  $regions = array();
  $states = array();
  foreach($locations as $location) {
    $location = strtolower($location);
    if(in_array($location, array('nat', 'hhs1', 'hhs2', 'hhs3', 'hhs4', 'hhs5', 'hhs6', 'hhs7', 'hhs8', 'hhs9', 'hhs10', 'cen1', 'cen2', 'cen3', 'cen4', 'cen5', 'cen6', 'cen7', 'cen8', 'cen9'))) {
      array_push($regions, $location);
    } else {
      array_push($states, $location);
    }
  }
  // initialize the epidata array
  $epidata = array();
  // query each region type individually (the data is stored by state, so getting regional data requires some extra processing)
  foreach($regions as $region) {
    $region = mysql_real_escape_string($region);
    $fields = "'{$region}' `location`, c.`epiweek`, sum(c.`num1`) `num1`, sum(c.`num2`) `num2`, sum(c.`num3`) `num3`, sum(c.`num4`) `num4`, sum(c.`num5`) `num5`, sum(c.`num6`) `num6`, sum(c.`num7`) `num7`, sum(c.`num8`) `num8`, sum(c.`total`) `total`";
    if($region === 'nat') {
      // final query for U.S. National
      $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) GROUP BY {$group} ORDER BY {$order}";
    } else {
      // build the location filter
      $condition_location = "`state` IN (" . get_region_states($region) . ")";
      // final query for HHS Regions
      $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_location}) GROUP BY {$group} ORDER BY {$order}";
    }
    // append query results to the epidata array
    execute_query($query, $epidata, $fields_string, $fields_int, null);
  }
  // query all states together
  if(count($states) !== 0) {
    $fields = "c.`state` `location`, c.`epiweek`, c.`num1`, c.`num2`, c.`num3`, c.`num4`, c.`num5`, c.`num6`, c.`num7`, c.`num8`, c.`total`";
    // build the location filter
    $condition_location = filter_strings('c.`state`', $states);
    // final query for states
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_location}) ORDER BY {$order}, c.`state` ASC";
    // append query results to the epidata array
    execute_query($query, $epidata, $fields_string, $fields_int, null);
  }
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `sensors` table
//   $names (required): array of sensor names
//   $locations (required): array of location names
//   $epiweeks (required): array of epiweek values/ranges
function get_sensors($names, $locations, $epiweeks) {
  // basic query info
  $table = '`sensors` s';
  $fields = "s.`name`, s.`location`, s.`epiweek`, s.`value`";
  $order = "s.`epiweek` ASC, s.`name` ASC, s.`location` ASC";
  // data type of each field
  $fields_string = array('name', 'location');
  $fields_int = array('epiweek');
  $fields_float = array('value');
  // build the name filter
  $condition_name = filter_strings('s.`name`', $names);
  // build the location filter
  $condition_location = filter_strings('s.`location`', $locations);
  // build the epiweek filter
  $condition_epiweek = filter_integers('s.`epiweek`', $epiweeks);
  // the query
  $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_name}) AND ({$condition_location}) AND ({$condition_epiweek}) ORDER BY {$order}";
  // get the data from the database
  $epidata = array();
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `nowcasts` table
//   $locations (required): array of location names
//   $epiweeks (required): array of epiweek values/ranges
function get_nowcast($locations, $epiweeks) {
  // basic query info
  $table = '`nowcasts` n';
  $fields = "n.`location`, n.`epiweek`, n.`value`, n.`std`";
  $order = "n.`epiweek` ASC, n.`location` ASC";
  // data type of each field
  $fields_string = array('location');
  $fields_int = array('epiweek');
  $fields_float = array('value', 'std');
  // build the location filter
  $condition_location = filter_strings('n.`location`', $locations);
  // build the epiweek filter
  $condition_epiweek = filter_integers('n.`epiweek`', $epiweeks);
  // the query
  $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_location}) AND ({$condition_epiweek}) ORDER BY {$order}";
  // get the data from the database
  $epidata = array();
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries a bunch of epidata tables
function get_meta() {
  // query and return metadata
  return array(array(
    '_api' => array(
      'minute' => meta_api(60),
      'hour' => meta_api(60 * 60),
      'day' => meta_api(60 * 60 * 24),
      'week' => meta_api(60 * 60 * 24 * 7),
      'month' => meta_api(60 * 60 * 24 * 30),
    ),
    'fluview' => meta_fluview(),
    'twitter' => meta_twitter(),
    'wiki' => meta_wiki(),
    'delphi' => meta_delphi(),
  ));
}
function meta_api($seconds) {
  $epidata = array();
  $seconds = intval($seconds);
  $query = "SELECT count(1) `num_hits`, count(distinct `ip`) `unique_ips`, sum(`num_rows`) `rows_returned` FROM `api_analytics` WHERE `datetime` >= date_sub(now(), interval {$seconds} second)";
  $fields_int = array('num_hits', 'unique_ips', 'rows_returned');
  execute_query($query, $epidata, null, $fields_int, null);
  return count($epidata) === 0 ? null : $epidata;
}
function meta_fluview() {
  $epidata = array();
  $query = 'SELECT max(`release_date`) `latest_update`, max(`issue`) `latest_issue`, count(1) `table_rows` FROM `fluview`';
  $fields_string = array('latest_update');
  $fields_int = array('latest_issue', 'table_rows');
  execute_query($query, $epidata, $fields_string, $fields_int, null);
  return count($epidata) === 0 ? null : $epidata;
}
function meta_twitter() {
  $epidata = array();
  $query = 'SELECT x.`date` `latest_update`, x.`table_rows`, count(distinct t.`state`) `num_states` FROM (SELECT max(`date`) `date`, count(1) `table_rows` FROM `twitter`) x JOIN `twitter` t ON t.`date` = x.`date`';
  $fields_string = array('latest_update');
  $fields_int = array('num_states', 'table_rows');
  execute_query($query, $epidata, $fields_string, $fields_int, null);
  return count($epidata) === 0 ? null : $epidata;
}
function meta_wiki() {
  $epidata = array();
  //$query = 'SELECT date_sub(max(`datetime`), interval 5 hour) `latest_update`, count(1) `table_rows` FROM `wiki_meta`'; // GMT to EST
  $query = 'SELECT max(`datetime`) `latest_update`, count(1) `table_rows` FROM `wiki_meta`';
  $fields_string = array('latest_update');
  $fields_int = array('table_rows');
  execute_query($query, $epidata, $fields_string, $fields_int, null);
  return count($epidata) === 0 ? null : $epidata;
}
function meta_delphi() {
  $epidata = array();
  $query = 'SELECT `system`, min(`epiweek`) `first_week`, max(`epiweek`) `last_week`, count(1) `num_weeks` FROM `forecasts` GROUP BY `system` ORDER BY `system` ASC';
  $fields_string = array('system');
  $fields_int = array('first_week', 'last_week', 'num_weeks');
  execute_query($query, $epidata, $fields_string, $fields_int, null);
  return count($epidata) === 0 ? null : $epidata;
}

// all responses will have a result field
$data = array('result' => -1);
// connect to the database
if(database_connect()) {
  // select the data source
  $source = isset($_REQUEST['source']) ? strtolower($_REQUEST['source']) : null;
  if($source === 'fluview') {
    if(require_all($data, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      $sort = isset($_REQUEST['sort']) ? $_REQUEST['sort'] : null;
      // get the data
      $epidata = get_fluview($epiweeks, $regions, $issues, $lag, $sort);
      store_result($data, $epidata);
    }
  } else if($source === 'flusurv') {
    if(require_all($data, array('epiweeks', 'locations'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $locations = extract_values($_REQUEST['locations'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      $epidata = get_flusurv($epiweeks, $locations, $issues, $lag);
      store_result($data, $epidata);
    }
  } else if($source === 'ilinet') {
    if(require_all($data, array('epiweeks', 'locations'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $locations = extract_values($_REQUEST['locations'], 'str');
      $version = isset($_REQUEST['version']) ? intval($_REQUEST['version']) : null;
      $authorized = $_REQUEST['auth'] === $AUTH['ilinet'];
      // get the data
      $epidata = get_ilinet($epiweeks, $locations, $version, $authorized);
      store_result($data, $epidata);
    }
  } else if($source === 'stateili') {
    if(require_all($data, array('auth', 'epiweeks', 'states'))) {
      if($_REQUEST['auth'] === $AUTH['stateili']) {
        // parse the request
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        $states = extract_values($_REQUEST['states'], 'str');
        // get the data
        $epidata = get_stateili($epiweeks, $states);
        store_result($data, $epidata);
      } else {
        $data['message'] = 'unauthenticated';
      }
    }
  } else if($source === 'gft') {
    if(require_all($data, array('epiweeks', 'locations'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $locations = extract_values($_REQUEST['locations'], 'str');
      // get the data
      $epidata = get_gft($epiweeks, $locations);
      store_result($data, $epidata);
    }
  } else if($source === 'ght') {
    if(require_all($data, array('auth', 'epiweeks', 'locations', 'query'))) {
      if($_REQUEST['auth'] === $AUTH['ght']) {
        // parse the request
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        $locations = extract_values($_REQUEST['locations'], 'str');
        $query = $_REQUEST['query'];
        // get the data
        $epidata = get_ght($epiweeks, $locations, $query);
        store_result($data, $epidata);
      } else {
        $data['message'] = 'unauthenticated';
      }
    }
  } else if($source === 'twitter') {
    if(require_all($data, array('auth', 'locations'))) {
      if($_REQUEST['auth'] === $AUTH['twitter']) {
        // parse the request
        $locations = extract_values($_REQUEST['locations'], 'str');
        if(require_any($data, array('dates', 'epiweeks'))) {
          if(isset($_REQUEST['dates'])) {
            $resolution = 'daily';
            $dates = extract_values($_REQUEST['dates'], 'int');
          } else {
            $resolution = 'weekly';
            $dates = extract_values($_REQUEST['epiweeks'], 'int');
          }
          // get the data
          $epidata = get_twitter($locations, $dates, $resolution);
          store_result($data, $epidata);
        }
      } else {
        $data['message'] = 'unauthenticated';
      }
    }
  } else if($source === 'wiki') {
    if(require_all($data, array('articles'))) {
      // parse the request
      $articles = extract_values($_REQUEST['articles'], 'str');
      if(require_any($data, array('dates', 'epiweeks'))) {
        if(isset($_REQUEST['dates'])) {
          $resolution = 'daily';
          $dates = extract_values($_REQUEST['dates'], 'int');
        } else {
          $resolution = 'weekly';
          $dates = extract_values($_REQUEST['epiweeks'], 'int');
        }
        $hours = isset($_REQUEST['hours']) ? extract_values($_REQUEST['hours'], 'int') : null;
        // get the data
        $epidata = get_wiki($articles, $dates, $resolution, $hours);
        store_result($data, $epidata);
      }
    }
  } else if($source === 'nidss_flu') {
    if(require_all($data, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      $epidata = get_nidss_flu($epiweeks, $regions, $issues, $lag);
      store_result($data, $epidata);
    }
  } else if($source === 'nidss_dengue') {
    if(require_all($data, array('epiweeks', 'locations'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $locations = extract_values($_REQUEST['locations'], 'str');
      // get the data
      $epidata = get_nidss_dengue($epiweeks, $locations);
      store_result($data, $epidata);
    }
  } else if($source === 'delphi') {
    if(require_all($data, array('system', 'epiweek'))) {
      // parse the request
      $system = $_REQUEST['system'];
      $epiweek = intval($_REQUEST['epiweek']);
      // get the data
      $epidata = get_forecast($system, $epiweek);
      store_result($data, $epidata);
    }
  } else if($source === 'signals') {
    if(require_all($data, array('auth', 'names', 'locations', 'epiweeks'))) {
      if($_REQUEST['auth'] === $AUTH['signals']) {
        // parse the request
        $names = extract_values($_REQUEST['names'], 'str');
        $locations = extract_values($_REQUEST['locations'], 'str');
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        // get the data
        $epidata = get_signals($names, $locations, $epiweeks);
        store_result($data, $epidata);
      } else {
        $data['message'] = 'unauthenticated';
      }
    }
  } else if($source === 'cdc') {
    if(require_all($data, array('auth', 'epiweeks', 'locations'))) {
      if($_REQUEST['auth'] === $AUTH['cdc']) {
        // parse the request
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        $locations = extract_values($_REQUEST['locations'], 'str');
        // get the data
        $epidata = get_cdc($epiweeks, $locations);
        store_result($data, $epidata);
      } else {
        $data['message'] = 'unauthenticated';
      }
    }
  } else if($source === 'sensors') {
    if(require_all($data, array('auth', 'names', 'locations', 'epiweeks'))) {
      if($_REQUEST['auth'] === $AUTH['sensors']) {
        // parse the request
        $names = extract_values($_REQUEST['names'], 'str');
        $locations = extract_values($_REQUEST['locations'], 'str');
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        // get the data
        $epidata = get_sensors($names, $locations, $epiweeks);
        store_result($data, $epidata);
      } else {
        $data['message'] = 'unauthenticated';
      }
    }
  } else if($source === 'nowcast') {
    if(require_all($data, array('locations', 'epiweeks'))) {
      // parse the request
      $locations = extract_values($_REQUEST['locations'], 'str');
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      // get the data
      $epidata = get_nowcast($locations, $epiweeks);
      store_result($data, $epidata);
    }
  } else if($source === 'meta') {
    // get the data
    $epidata = get_meta();
    store_result($data, $epidata);
  } else {
    $data['message'] = 'no data source specified';
  }
  // API analytics
  $ip = mysql_real_escape_string(isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '');
  $ua = mysql_real_escape_string(isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : '');
  $source = mysql_real_escape_string(isset($source) ? $source : '');
  $result = intval($data['result']);
  $num_rows = intval(isset($data['epidata']) ? count($data['epidata']) : 0);
  mysql_query("INSERT INTO `api_analytics` (`datetime`, `ip`, `ua`, `source`, `result`, `num_rows`) VALUES (now(), '{$ip}', '{$ua}', '{$source}', {$result}, {$num_rows})");
} else {
  $data['message'] = 'database error';
}

// send the response as a json object
header('Content-Type: application/json');
echo json_encode($data);
?>
