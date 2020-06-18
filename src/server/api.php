<?php
/*
===============
=== Purpose ===
===============

An API for DELPHI's epidemiological data.

Documentation and sample code are on GitHub:
https://github.com/cmu-delphi/delphi-epidata

See also:
  - fluview_update.py
  - gft_update.py
  - twitter_update.py
  - wiki.py
  - taiwan_update.py
  - submission_loader.py
  - ght_update.py
  - sensor_update.py
  - nowcast.py
  - cdc_extract.py
  - flusurv_update.py
  - quidel_update.py
  - norostat_update.py
  - README.md
*/

// secrets
require_once('/var/www/html/secrets.php');

// helpers
require_once(__DIR__ . '/api_helpers.php');

// passwords
$AUTH = array(
  'twitter'        => Secrets::$api['twitter'],
  'ght'            => Secrets::$api['ght'],
  'fluview'        => Secrets::$api['fluview'],
  'cdc'            => Secrets::$api['cdc'],
  'sensors'        => Secrets::$api['sensors'],
  'sensor_subsets' => Secrets::$api['sensor_subsets'],
  'quidel'         => Secrets::$api['quidel'],
  'norostat'       => Secrets::$api['norostat'],
  'afhsb'          => Secrets::$api['afhsb']
);
// begin sensor query authentication configuration
//   A multimap of sensor names to the "granular" auth tokens that can be used to access them; excludes the "global" sensor auth key that works for all sensors:
$GRANULAR_SENSOR_AUTH_TOKENS = array(
  'twtr' => array($AUTH['sensor_subsets']['twtr_sensor']),
  'gft' => array($AUTH['sensor_subsets']['gft_sensor']),
  'ght' => array($AUTH['sensor_subsets']['ght_sensors']),
  'ghtj' => array($AUTH['sensor_subsets']['ght_sensors']),
  'cdc' => array($AUTH['sensor_subsets']['cdc_sensor']),
  'quid' => array($AUTH['sensor_subsets']['quid_sensor']),
  'wiki' => array($AUTH['sensor_subsets']['wiki_sensor']),
);
//   A set of sensors that do not require an auth key to access:
$OPEN_SENSORS = array(
  'sar3',
  'epic',
  'arch',
);
//   Limits on the number of effective auth token equality checks performed per sensor query; generate auth tokens with appropriate levels of entropy according to the limits below:
$MAX_GLOBAL_AUTH_CHECKS_PER_SENSOR_QUERY = 1; // (but imagine is larger to futureproof)
$MAX_GRANULAR_AUTH_CHECKS_PER_SENSOR_QUERY = 30; // (but imagine is larger to futureproof)
//   A (currently redundant) limit on the number of auth tokens that can be provided:
$MAX_AUTH_KEYS_PROVIDED_PER_SENSOR_QUERY = 1;
// end sensor query authentication configuration

// result limit, ~10 years of daily data
$MAX_RESULTS = 3650;

// queries the `fluview` and `fluview_imputed` tables
//   $epiweeks (required): array of epiweek values/ranges
//   $regions (required): array of region names
//   $issues (optional): array of epiweek values/ranges
//     overrides $lag
//     default: most recent issue
//   $lag (optional): number of weeks between each epiweek and its issue
//     overridden by $issues
//     default: most recent issue
//   $authorized: determines whether private data (i.e. `fluview_imputed`) is
//     included in the result
function get_fluview($epiweeks, $regions, $issues, $lag, $authorized) {
  $epidata = array();
  // public data
  $table = '`fluview` fv';
  $fields = "fv.`release_date`, fv.`issue`, fv.`epiweek`, fv.`region`, fv.`lag`, fv.`num_ili`, fv.`num_patients`, fv.`num_providers`, fv.`wili`, fv.`ili`, fv.`num_age_0`, fv.`num_age_1`, fv.`num_age_2`, fv.`num_age_3`, fv.`num_age_4`, fv.`num_age_5`";
  _get_fluview_by_table($epidata, $epiweeks, $regions, $issues, $lag, $table, $fields);
  if(!$authorized) {
    // Make a special exception for New York. It is a (weighted) sum of two
    // constituent locations -- "ny_minus_jfk" and "jfk" -- both of which are
    // publicly available.
    if(in_array('ny', array_map('strtolower', $regions))) {
      $regions = array('ny');
      $authorized = true;
    }
  }
  if($authorized) {
    // private data (no release date, no age groups, and wili is equal to ili)
    $table = '`fluview_imputed` fv';
    $fields = "NULL `release_date`, fv.`issue`, fv.`epiweek`, fv.`region`, fv.`lag`, fv.`num_ili`, fv.`num_patients`, fv.`num_providers`, fv.`ili` `wili`, fv.`ili`, NULL `num_age_0`, NULL `num_age_1`, NULL `num_age_2`, NULL `num_age_3`, NULL `num_age_4`, NULL `num_age_5`";
    _get_fluview_by_table($epidata, $epiweeks, $regions, $issues, $lag, $table, $fields);
  }
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// a helper function to query `fluview` and `fluview_imputed` individually
// parameters
function _get_fluview_by_table(&$epidata, $epiweeks, $regions, $issues, $lag, $table, $fields) {
  // basic query info
  $order = "fv.`epiweek` ASC, fv.`region` ASC, fv.`issue` ASC";
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
  $fields_string = array('release_date', 'region');
  $fields_int = array('issue', 'epiweek', 'lag', 'num_ili', 'num_patients', 'num_providers', 'num_age_0', 'num_age_1', 'num_age_2', 'num_age_3', 'num_age_4', 'num_age_5');
  $fields_float = array('wili', 'ili');
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
}

// queries the `fluview_clinical` table
//   $epiweeks (required): array of epiweek values/ranges
//   $regions (required): array of region names
//   $issues (optional): array of epiweek values/ranges
//     overrides $lag
//     default: most recent issue
//   $lag (optional): number of weeks between each epiweek and its issue
//     overridden by $issues
//     default: most recent issue
function get_fluview_clinical($epiweeks, $regions, $issues, $lag) {
  // store the results in an array
  $epidata = array();
  // set up for query
  $table = "`fluview_clinical` fvc";
  // $fields = 'fvc.`release_date`, fvc.`issue`, fvc.`epiweek`, fvc.`region`, fvc.`lag`, fvc.`total_specimens`, fvc.`total_a_h1n1`, fvc.`total_a_h3`, fvc.`total_a_h3n2v`, fvc.`total_a_no_sub`, fvc.`total_b`, fvc.`total_b_vic`, fvc.`total_b_yam`';
  $fields = "fvc.`release_date`, fvc.`issue`, fvc.`epiweek`, fvc.`region`, fvc.`lag`, fvc.`total_specimens`, fvc.`total_a`, fvc.`total_b`, fvc.`percent_positive`, fvc.`percent_a`, fvc.`percent_b`";
  $order = "fvc.`epiweek` ASC, fvc.`region` ASC, fvc.`issue` ASC";
  // create conditions
  $condition_epiweek = filter_integers("fvc.`epiweek`", $epiweeks);
  $condition_region = filter_strings("fvc.`region`", $regions);
  if ($issues !== null) {
    // using specific issues
    $condition_issue = filter_integers("fvc.`issue`", $issues);
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_issue}) ORDER BY {$order}";
  } else if ($lag !== null) {
    // using lagged issues
    $condition_lag = '(fvc.`lag` = {$lag})';
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_lag}) ORDER BY {$order}";
  } else {
    // using most recent issues
    $subquery = "(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) GROUP BY `epiweek`, `region`) x";
    $condition = "x.`max_issue` = fvc.`issue` AND x.`epiweek` = fvc.`epiweek` AND x.`region` = fvc.`region`";
    $query = "SELECT {$fields} FROM {$table} JOIN {$subquery} ON {$condition} ORDER BY {$order}";
  }
  // get the data from the database
  $fields_string = array('release_date', 'region');
  $fields_float = array('percent_positive', 'percent_a', 'percent_b');
  $fields_int = array('issue', 'epiweek', 'lag', 'total_specimens', 'total_a', 'total_b');
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the result, if any
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

// queries the `paho_dengue` table
//   $epiweeks (required): array of epiweek values/ranges
//   $regions (required): array of region names
//   $issues (optional): array of epiweek values/ranges
//     overrides $lag
//     default: most recent issue
//   $lag (optional): number of weeks between each epiweek and its issue
//     overridden by $issues
//     default: most recent issue
function get_paho_dengue($epiweeks, $regions, $issues, $lag) {
  // store the results in an array
  $epidata = array();
  // set up for query
  $table = "`paho_dengue` pd";
  $fields = "pd.`release_date`, pd.`issue`, pd.`epiweek`, pd.`region`, pd.`lag`, pd.`total_pop`, pd.`serotype`, pd.`num_dengue`, pd.`incidence_rate`, pd.`num_severe`, pd.`num_deaths`";
  $order = "pd.`epiweek` ASC, pd.`region` ASC, pd.`issue` ASC";
  // create conditions
  $condition_epiweek = filter_integers("pd.`epiweek`", $epiweeks);
  $condition_region = filter_strings("pd.`region`", $regions);
  if ($issues !== null) {
    // using specific issues
    $condition_issue = filter_integers("pd.`issue`", $issues);
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_issue}) ORDER BY {$order}";
  } else if ($lag !== null) {
    // using lagged issues
    $condition_lag = '(pd.`lag` = {$lag})';
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_lag}) ORDER BY {$order}";
  } else {
    // using most recent issues
    $subquery = "(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) GROUP BY `epiweek`, `region`) x";
    $condition = "x.`max_issue` = pd.`issue` AND x.`epiweek` = pd.`epiweek` AND x.`region` = pd.`region`";
    $query = "SELECT {$fields} FROM {$table} JOIN {$subquery} ON {$condition} ORDER BY {$order}";
  }
  // get the data from the database
  $fields_string = array('release_date', 'region', 'serotype');
  $fields_float = array('incidence_rate');
  $fields_int = array('issue', 'epiweek', 'lag', 'total_pop', 'num_dengue', 'num_severe', 'num_deaths');
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the result, if any
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `ecdc_ili` table
//   $epiweeks (required): array of epiweek values/ranges
//   $regions (required): array of region names
//   $issues (optional): array of epiweek values/ranges
//     overrides $lag
//     default: most recent issue
//   $lag (optional): number of weeks between each epiweek and its issue
//     overridden by $issues
//     default: most recent issue
function get_ecdc_ili($epiweeks, $regions, $issues, $lag) {
  // store the results in an array
  $epidata = array();
  // set up for query
  $table = "`ecdc_ili` ec";
  $fields = "ec.`release_date`, ec.`issue`, ec.`epiweek`, ec.`region`, ec.`lag`, ec.`incidence_rate`";
  $order = "ec.`epiweek` ASC, ec.`region` ASC, ec.`issue` ASC";
  // create conditions
  $condition_epiweek = filter_integers("ec.`epiweek`", $epiweeks);
  $condition_region = filter_strings("ec.`region`", $regions);
  if ($issues !== null) {
    // using specific issues
    $condition_issue = filter_integers("ec.`issue`", $issues);
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_issue}) ORDER BY {$order}";
  } else if ($lag !== null) {
    // using lagged issues
    $condition_lag = '(ec.`lag` = {$lag})';
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_lag}) ORDER BY {$order}";
  } else {
    // using most recent issues
    $subquery = "(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) GROUP BY `epiweek`, `region`) x";
    $condition = "x.`max_issue` = ec.`issue` AND x.`epiweek` = ec.`epiweek` AND x.`region` = ec.`region`";
    $query = "SELECT {$fields} FROM {$table} JOIN {$subquery} ON {$condition} ORDER BY {$order}";
  }
  // get the data from the database
  $fields_string = array('release_date', 'region');
  $fields_float = array('incidence_rate');
  $fields_int = array('issue', 'epiweek', 'lag');
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the result, if any
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `kcdc_ili` table
//   $epiweeks (required): array of epiweek values/ranges
//   $regions (required): array of region names
//   $issues (optional): array of epiweek values/ranges
//     overrides $lag
//     default: most recent issue
//   $lag (optional): number of weeks between each epiweek and its issue
//     overridden by $issues
//     default: most recent issue
function get_kcdc_ili($epiweeks, $regions, $issues, $lag) {
  // store the results in an array
  $epidata = array();
  // set up for query
  $table = "`kcdc_ili` kc";
  $fields = "kc.`release_date`, kc.`issue`, kc.`epiweek`, kc.`region`, kc.`lag`, kc.`ili`";
  $order = "kc.`epiweek` ASC, kc.`region` ASC, kc.`issue` ASC";
  // create conditions
  $condition_epiweek = filter_integers("kc.`epiweek`", $epiweeks);
  $condition_region = filter_strings("kc.`region`", $regions);
  if ($issues !== null) {
    // using specific issues
    $condition_issue = filter_integers("kc.`issue`", $issues);
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_issue}) ORDER BY {$order}";
  } else if ($lag !== null) {
    // using lagged issues
    $condition_lag = '(kc.`lag` = {$lag})';
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) AND ({$condition_lag}) ORDER BY {$order}";
  } else {
    // using most recent issues
    $subquery = "(SELECT max(`issue`) `max_issue`, `epiweek`, `region` FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_region}) GROUP BY `epiweek`, `region`) x";
    $condition = "x.`max_issue` = kc.`issue` AND x.`epiweek` = kc.`epiweek` AND x.`region` = kc.`region`";
    $query = "SELECT {$fields} FROM {$table} JOIN {$subquery} ON {$condition} ORDER BY {$order}";
  }
  // get the data from the database
  $fields_string = array('release_date', 'region');
  $fields_float = array('ili');
  $fields_int = array('issue', 'epiweek', 'lag');
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the result, if any
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
  global $dbh;
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
    $region = mysqli_real_escape_string($dbh, $region);
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
//   $language (required): specify the language of articles we want to retrieve
//   $dates (required): array of date or epiweek values/ranges
//   $resolution (required): either 'daily' or 'weekly'
//   $hours (optional): array of hour values/ranges
// if present, $hours determines which counts are used within each day; otherwise all counts are used
// for example, if hours=[4], then only the 4 AM (UTC) stream is returned
function get_wiki($articles, $language, $dates, $resolution, $hours) {
  // required for `mysqli_real_escape_string`
  global $dbh;
  $language = mysqli_real_escape_string($dbh, $language);
  // basic query info
  // in a few rare instances (~6 total), `total` is unreasonably high; something glitched somewhere, just ignore it
  // $table = '`wiki` w JOIN (SELECT * FROM `wiki_meta` WHERE `total` < 100000000) m ON m.`datetime` = w.`datetime`';
  // We select rows by language and then the problem is converted to the original one, and the rest of code can be same
  $table = "( SELECT * FROM `wiki` WHERE `language` = '$language' ) w JOIN (SELECT * FROM `wiki_meta` WHERE `total` < 100000000 AND `language` = '$language' ) m ON m.`datetime` = w.`datetime`";
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

// queries the `quidel` table
//   $locations (required): array of location names
//   $epiweeks (required): array of epiweek values/ranges
function get_quidel($locations, $epiweeks) {
  // basic query info
  $table = '`quidel` q';
  $fields = "q.`location`, q.`epiweek`, q.`value`";
  $order = "q.`epiweek` ASC, q.`location` ASC";
  // data type of each field
  $fields_string = array('location');
  $fields_int = array('epiweek');
  $fields_float = array('value');
  // build the location filter
  $condition_location = filter_strings('q.`location`', $locations);
  // build the epiweek filter
  $condition_epiweek = filter_integers('q.`epiweek`', $epiweeks);
  // the query
  $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_location}) AND ({$condition_epiweek}) ORDER BY {$order}";
  // get the data from the database
  $epidata = array();
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `norostat_point` table
//   $locations (required): single location value (str listing included states)
//   $epiweeks (required): array of epiweek values/ranges
function get_norostat($location, $epiweeks) {
  // todo add release/issue args
  //
  // build the filters:
  $condition_location = filter_strings('`norostat_raw_datatable_location_pool`.`location`', [$location]);
  $condition_epiweek = filter_integers('`latest`.`epiweek`', $epiweeks);
  // get the data from the database
  $epidata = array();
  // (exclude "location" from output to reduce size & ugliness of result,
  // transfer bandwidth required; it would just be a repeated echo of the input
  // $location)
  $fields_string = array('release_date');
  $fields_int = array('epiweek', 'value');
  $query = "
    SELECT `latest`.`release_date`, `latest`.`epiweek`, `latest`.`new_value` AS `value`
    FROM `norostat_point_diffs` AS `latest`
    LEFT JOIN `norostat_raw_datatable_location_pool` USING (`location_id`)
    LEFT JOIN (
      SELECT * FROM `norostat_point_diffs`
    ) `later`
    ON `latest`.`location_id` = `later`.`location_id` AND
       `latest`.`epiweek` = `later`.`epiweek` AND
       (`latest`.`release_date`, `latest`.`parse_time`) <
         (`later`.`release_date`, `later`.`parse_time`) ANDou z z
       `later`.`new_value` IS NOT NULL
    WHERE ({$condition_location}) AND
          ({$condition_epiweek}) AND
          `later`.`parse_time` IS NULL AND
          `latest`.`new_value` IS NOT NULL
    ";
  // xxx may reorder epiweeks
  execute_query($query, $epidata, $fields_string, $fields_int, null);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `afhsb_00to13` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of location names
//   $flu_types (required): array of flu types
function get_afhsb($locations, $epiweeks, $flu_types) {
  global $dbh;
  $epidata = array();
  // split locations into national/regional/state
  $location_dict = array("hhs" => array(), "cen" => array(),
                         "state" => array(), "country" => array());
  foreach($locations as $location) {
    $location = strtolower($location);
    if(substr($location, 0, 3) === "hhs") {
      array_push($location_dict["hhs"], $location);
    } elseif (substr($location, 0, 3) === "cen") {
      array_push($location_dict["cen"], $location);
    } elseif (strlen($location) === 3) {
      array_push($location_dict["country"], $location);
    } elseif (strlen($location) === 2) {
      array_push($location_dict["state"], $location);
    }
  }
  // split flu types into disjoint/subset
  $disjoint_flus = array();
  $subset_flus = array();
  foreach($flu_types as $flu_type) {
    if(in_array($flu_type, array('flu1','flu2-flu1','flu3-flu2','ili-flu3'))) {
      array_push($disjoint_flus, $flu_type);
    } elseif(in_array($flu_type, array('flu2','flu3','ili'))) {
      array_push($subset_flus, $flu_type);
    }
  }
  foreach($location_dict as $location_type=>$locs) {
    if(!empty($locs)) {
      _get_afhsb_by_table($epidata, $location_type, $epiweeks, $locs, $disjoint_flus, $subset_flus);
    }
  }
  return count($epidata) === 0 ? null : $epidata;
}

// A helper function to query afhsb tables
function _get_afhsb_by_table(&$epidata, $location_type, $epiweeks, $locations, $disjoint_flus, $subset_flus) {
  // basic query info
  $table = (in_array($location_type, array("hhs", "cen"))) ? "afhsb_00to13_region" : "afhsb_00to13_state";
  $fields = "`epiweek`, `{$location_type}` `location`, sum(`visit_sum`) `visit_sum`";
  $group = '`epiweek`, `location`';
  $order = "`epiweek` ASC, `location` ASC";
  $fields_string = array('location', 'flu_type');
  $fields_int = array('epiweek', 'visit_sum');
  // build the epiweek filter
  $condition_epiweek = filter_integers('`epiweek`', $epiweeks);
  // build the location filter
  $condition_location = filter_strings($location_type, $locations);

  // subset flu types: flu2, flu3, ili
  $flu_mapping = array('flu2' => array('flu1','flu2-flu1'),
    'flu3' => array('flu1','flu2-flu1','flu3-flu2'),
    'ili' => array('flu1','flu2-flu1','flu3-flu2','ili-flu3'));
  foreach($subset_flus as $subset_flu) {
    $condition_flu = filter_strings('`flu_type`', $flu_mapping[$subset_flu]);
    $query = "SELECT {$fields}, '{$subset_flu}' `flu_type` FROM {$table}
      WHERE ({$condition_epiweek}) AND ({$condition_location}) AND ({$condition_flu})
      GROUP BY {$group} ORDER BY {$order}";
      execute_query($query, $epidata, $fields_string, $fields_int, null);
  }
  // disjoint flu types: flu1, flu2-flu1, flu3-flu2, ili-flu3
  if(!empty($disjoint_flus)){
    $condition_flu = filter_strings('`flu_type`', $disjoint_flus);
    $query = "SELECT {$fields}, `flu_type` FROM {$table}
    WHERE ({$condition_epiweek}) AND ({$condition_location}) AND ({$condition_flu})
    GROUP BY {$group},`flu_type` ORDER BY {$order},`flu_type`";
    execute_query($query, $epidata, $fields_string, $fields_int, null);
  }
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
  global $dbh;
  // build the epiweek filter
  $condition_epiweek = filter_integers('nd.`epiweek`', $epiweeks);
  // get the data from the database
  $epidata = array();
  $fields_string = array('location');
  $fields_int = array('epiweek', 'count');
  foreach($locations as $location) {
    $location = mysqli_real_escape_string($dbh, $location);
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
  global $dbh;
  // get the data from the database
  $system = mysqli_real_escape_string($dbh, $system);
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

// queries the `cdc_extract` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of location names
function get_cdc($epiweeks, $locations) {
  global $dbh;
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
    $region = mysqli_real_escape_string($dbh, $region);
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

// queries the `dengue_sensors` table
//   $names (required): array of sensor names
//   $locations (required): array of location names
//   $epiweeks (required): array of epiweek values/ranges
function get_dengue_sensors($names, $locations, $epiweeks) {
  // basic query info
  $table = '`dengue_sensors` s';
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

// queries the `dengue_nowcasts` table
//   $locations (required): array of location names
//   $epiweeks (required): array of epiweek values/ranges
function get_dengue_nowcast($locations, $epiweeks) {
  // basic query info
  $table = '`dengue_nowcasts` n';
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

// queries the `covidcast` table.
//   $source (required): name of upstream data souce
//   $signal (required): name of signal derived from upstream data
//   $time_type (required): temporal resolution (e.g. day, week)
//   $geo_type (required): spatial resolution (e.g. county, msa, state)
//   $time_values (required): array of time values/ranges
//   $geo_value (required): location identifier or `*` as a wildcard for all
//     locations (specific to `$geo_type`)
//   $issues (optional): array of time values/ranges
//     overrides $lag
//     default: most recent issue
//   $lag (optional): number of time units between each time value and its issue
//     overridden by $issues
//     default: most recent issue
function get_covidcast($source, $signal, $time_type, $geo_type, $time_values, $geo_value, $issues, $lag) {
  // required for `mysqli_real_escape_string`
  global $dbh;
  $source = mysqli_real_escape_string($dbh, $source);
  $signal = mysqli_real_escape_string($dbh, $signal);
  $time_type = mysqli_real_escape_string($dbh, $time_type);
  $geo_type = mysqli_real_escape_string($dbh, $geo_type);
  $geo_value = mysqli_real_escape_string($dbh, $geo_value);
  // basic query info
  $table = '`covidcast` t';
  $fields = "t.`time_value`, t.`geo_value`, t.`value`, t.`stderr`, t.`sample_size`, t.`direction`, t.`issue`, t.`lag`";
  $order = "t.`time_value` ASC, t.`geo_value` ASC, t.`issue` ASC";
  // data type of each field
  $fields_string = array('geo_value');
  $fields_int = array('time_value', 'direction', 'issue', 'lag');
  $fields_float = array('value', 'stderr', 'sample_size');
  // build the source, signal, time, and location (type and id) filters
  $condition_source = "t.`source` = '{$source}'";
  $condition_signal = "t.`signal` = '{$signal}'";
  $condition_time_type = "t.`time_type` = '{$time_type}'";
  $condition_geo_type = "t.`geo_type` = '{$geo_type}'";
  $condition_time_value = filter_integers('t.`time_value`', $time_values);
    
  if ($geo_value === '*') {
    // the wildcard query should return data for all locations in `geo_type`
    $condition_geo_value = 'TRUE';
  } else {
    // return data for a particular location
    $condition_geo_value = "t.`geo_value` = '{$geo_value}'";
  }
  $conditions = "({$condition_source}) AND ({$condition_signal}) AND ({$condition_time_type}) AND ({$condition_geo_type}) AND ({$condition_time_value}) AND ({$condition_geo_value})";

  $subquery = "";
  if ($issues !== null) {
    //build the issue filter
    $condition_issue = filter_integers('t.`issue`', $issues);
    $condition_version = $condition_issue;
  } else if($lag !== null) {
    //build the lag filter
    $condition_lag = "(t.`lag` = {$lag})";
    $condition_version = $condition_lag;
  } else {
    //fetch most recent issues
    $sub_fields = "max(`issue`) `max_issue`, `time_type`, `time_value`, `source`, `signal`, `geo_type`, `geo_value`";
    $sub_group = "`time_value`, `source`, `signal`, `geo_value`";
    $sub_condition = "x.`max_issue` = t.`issue` AND x.`time_type` = t.`time_type` AND x.`time_value` = t.`time_value` AND x.`source` = t.`source` AND x.`signal` = t.`signal` AND x.`geo_type` = t.`geo_type` AND x.`geo_value` = t.`geo_value`";
    $subquery = "JOIN (SELECT {$sub_fields} FROM {$table} WHERE ({$conditions}) GROUP BY {$sub_group}) x ON {$sub_condition}";
    $condition_version = 'TRUE';
  }
  // the query
  $query = "SELECT {$fields} FROM {$table} {$subquery} WHERE {$conditions} AND ({$condition_version}) ORDER BY {$order}";
  // get the data from the database
  $epidata = array();
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `covidcast` table for metadata only.
function get_covidcast_meta() {
  // basic query info
  $table = '`covidcast` t';
  $fields = "t.`source` AS `data_source`, t.`signal`, t.`time_type`, t.`geo_type`, MIN(t.`time_value`) AS `min_time`, MAX(t.`time_value`) AS `max_time`, COUNT(DISTINCT t.`geo_value`) AS `num_locations`, MIN(`value`) AS `min_value`, MAX(`value`) AS `max_value`, AVG(`value`) AS `mean_value`, STD(`value`) AS `stdev_value`, MAX(`timestamp1`) AS `last_update`, MAX(`issue`) as `max_issue`, MIN(`lag`) as `min_lag`, MAX(`lag`) as `max_lag`";
  $condition_wip = "t.`signal` NOT LIKE 'wip_%'";
  $group = "t.`source`, t.`signal`, t.`time_type`, t.`geo_type`";
  $order = "t.`source` ASC, t.`signal` ASC, t.`time_type` ASC, t.`geo_type` ASC";

  // only consider most recent issues
  $sub_fields = "max(`issue`) `max_issue`, `time_type`, `time_value`, `source`, `signal`, `geo_type`, `geo_value`";
  $sub_group = "`time_value`, `time_type`, `geo_type`, `source`, `signal`, `geo_value`";
  $sub_condition = "x.`max_issue` = t.`issue` AND x.`time_type` = t.`time_type` AND x.`time_value` = t.`time_value` AND x.`source` = t.`source` AND x.`signal` = t.`signal` AND x.`geo_type` = t.`geo_type` AND x.`geo_value` = t.`geo_value`";
  $subquery = "JOIN (SELECT {$sub_fields} FROM {$table} GROUP BY {$sub_group}) x ON {$sub_condition}";
  
  // data type of each field
  $fields_string = array('data_source', 'signal', 'time_type', 'geo_type');
  $fields_int = array('min_time', 'max_time', 'num_locations', 'last_update', 'max_issue', 'min_lag', 'max_lag');
  $fields_float = array('min_value', 'max_value', 'mean_value', 'stdev_value');
  // the query
  $query = "SELECT {$fields} FROM {$table} {$subquery} WHERE {$condition_wip} GROUP BY {$group} ORDER BY {$order}";
  // get the data from the database
  $epidata = array();
  execute_query($query, $epidata, $fields_string, $fields_int, $fields_float);
  // return the data
  return count($epidata) === 0 ? null : $epidata;
}

// queries the `covidcast` table for metadata only. attempts to used the cached
// version, falling back to `get_covidcast_meta` otherwise.
function get_covidcast_meta_cached() {
  // only use the cache if it's less than ~1 hour old (75 minutes max to allow
  // for some wiggle room)
  $max_age = 75 * 60;

  // basic query info
  $query = 'SELECT UNIX_TIMESTAMP(NOW()) - `timestamp` AS `age`, `epidata` FROM `covidcast_meta_cache` LIMIT 1';

  // get the data from the database
  global $dbh;
  $epidata = null;
  $result = mysqli_query($dbh, $query);
  if($row = mysqli_fetch_array($result)) {
    if (intval($row['age']) < $max_age && strlen($row['epidata']) > 0) {
      // parse and use the cached response
      $epidata = json_decode($row['epidata'], true);
    }
  }

  // fallback to the real thing if necessary
  if ($epidata === null) {
    error_log('covidcast_meta cache miss');
    $epidata = get_covidcast_meta();
  }

  // return the data
  $has_values = $epidata !== null && count($epidata) > 0;
  return $has_values ? $epidata : null;
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
function get_meta_norostat() {
  // put behind appropriate auth check
  $epidata_releases = array();
  $query = 'SELECT DISTINCT `release_date` FROM `norostat_raw_datatable_version_list`';
  execute_query($query, $epidata_releases, array('release_date'), null, null);
  $epidata_locations = array();
  $query = 'SELECT DISTINCT `location` FROM `norostat_raw_datatable_location_pool`';
  execute_query($query, $epidata_locations, array('location'), null, null);
  $epidata = array(
    "releases" => $epidata_releases,
    "locations" => $epidata_locations
  );
  return $epidata;
}
function get_meta_afhsb() {
  // put behind appropriate auth check
  $table1 = 'afhsb_00to13_state';
  $table2 = 'afhsb_13to17_state';
  $epidata = array();
  $string_keys = array('state', 'country');
  $int_keys = array('flu_severity');
  foreach($string_keys as $key) {
    $epidata_key = array();
    $query = "SELECT DISTINCT `{$key}` FROM (select `{$key}` from `{$table1}` union select `{$key}` from `{$table2}`) t";
    execute_query($query, $epidata_key, array($key), null, null);
    $epidata[$key] = $epidata_key;
  }
  foreach($int_keys as $key) {
    $epidata_key = array();
    $query = "SELECT DISTINCT `{$key}` FROM (select `{$key}` from `{$table1}` union select `{$key}` from `{$table2}`) t";

    execute_query($query, $epidata_key, null, array($key), null);
    $epidata[$key] = $epidata_key;
  }
  return $epidata;
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
      $authorized = isset($_REQUEST['auth']) && $_REQUEST['auth'] === $AUTH['fluview'];
      // get the data
      $epidata = get_fluview($epiweeks, $regions, $issues, $lag, $authorized);
      store_result($data, $epidata);
    }
  } else if($source === 'fluview_meta') {
    // get the data
    $epidata = meta_fluview();
    store_result($data, $epidata);
  } else if ($source === 'fluview_clinical') {
    if(require_all($data, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      $epidata = get_fluview_clinical($epiweeks, $regions, $issues, $lag);
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
  } else if ($source === 'paho_dengue') {
    if(require_all($data, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      $epidata = get_paho_dengue($epiweeks, $regions, $issues, $lag);
      store_result($data, $epidata);
    }
  } else if ($source === 'ecdc_ili') {
    if(require_all($data, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      $epidata = get_ecdc_ili($epiweeks, $regions, $issues, $lag);
      store_result($data, $epidata);
    }
  } else if ($source === 'kcdc_ili') {
    if(require_all($data, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      $epidata = get_kcdc_ili($epiweeks, $regions, $issues, $lag);
      store_result($data, $epidata);
    }
  } else if($source === 'ilinet' || $source === 'stateili') {
    // these two sources are now combined into fluview
    $data['message'] = 'use fluview instead';
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
    if(require_all($data, array('articles', 'language'))) {
      // parse the request
      $articles = extract_values($_REQUEST['articles'], 'str');
      $language = $_REQUEST['language'];
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
        $epidata = get_wiki($articles, $language, $dates, $resolution, $hours);
        store_result($data, $epidata);
      }
    }
  } else if($source === 'quidel') {
    if(require_all($data, array('auth', 'locations', 'epiweeks'))) {
      if($_REQUEST['auth'] === $AUTH['quidel']) {
        // parse the request
        $locations = extract_values($_REQUEST['locations'], 'str');
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        // get the data
        $epidata = get_quidel($locations, $epiweeks);
        store_result($data, $epidata);
      } else {
        $data['message'] = 'unauthenticated';
      }
    }
  } else if($source === 'norostat') {
    if(require_all($data, array('auth', 'location', 'epiweeks'))) {
      if($_REQUEST['auth'] === $AUTH['norostat']) {
        // parse the request
        $location = $_REQUEST['location'];
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        // get the data
        $epidata = get_norostat($location, $epiweeks);
        store_result($data, $epidata);
      } else {
          $data['message'] = 'unauthenticated';
      }
    }
  } else if($source === 'afhsb') {
    if(require_all($data, array('auth', 'locations', 'epiweeks', 'flu_types'))) {
      if($_REQUEST['auth'] === $AUTH['afhsb']) {
        // parse the request
        $locations = extract_values($_REQUEST['locations'], 'str');
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        $flu_types = extract_values($_REQUEST['flu_types'], 'str');
        // get the data
        $epidata = get_afhsb($locations, $epiweeks, $flu_types);
        store_result($data, $epidata);
      } else {
          $data['message'] = 'unauthenticated';
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
    // this sources is now replaced by sensors
    $data['message'] = 'use sensors instead';
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
    if(require_all($data, array('names', 'locations', 'epiweeks'))) {
      if(!array_key_exists('auth', $_REQUEST)) {
        $auth_tokens_presented = array();
      } else {
        $auth_tokens_presented = extract_values($_REQUEST['auth'], 'str');
      }
      $names = extract_values($_REQUEST['names'], 'str');
      $n_names = count($names);
      $n_auth_tokens_presented = count($auth_tokens_presented);
      $max_valid_granular_tokens_per_name = max(array_map('count', $GRANULAR_SENSOR_AUTH_TOKENS));
      // The number of valid granular tokens is related to the number of auth token checks that a single query could perform.  Use the max number of valid granular auth tokens per name in the check below as a way to prevent leakage of sensor names (but revealing the number of sensor names) via this interface.  Treat all sensors as non-open for convenience of calculation.
      if($n_names === 0) {
        // Check whether no names were provided to prevent edge-case issues in error message below, and in case surrounding behavior changes in the future:
        $data['message'] = 'no sensor names provided';
      } else if($n_auth_tokens_presented > 1) {
        $data['message'] = 'currently, only a single auth token is allowed to be presented at a time; please issue a separate query for each sensor name using only the corresponding token';
      } else if(
        // Check whether max number of presented-vs.-acceptable token comparisons that would be performed is over the set limits, avoiding calculation of numbers > PHP_INT_MAX/100:
        //   Global auth token comparison limit check:
        $n_auth_tokens_presented > $MAX_GLOBAL_AUTH_CHECKS_PER_SENSOR_QUERY ||
        //   Granular auth token comparison limit check:
        $n_names > (int)((PHP_INT_MAX/100-1)/max(1,$max_valid_granular_tokens_per_name)) ||
        $n_auth_tokens_presented > (int)(PHP_INT_MAX/100/max(1,$n_names*$max_valid_granular_tokens_per_name)) ||
        $n_auth_tokens_presented * $n_names * $max_valid_granular_tokens_per_name > $MAX_GRANULAR_AUTH_CHECKS_PER_SENSOR_QUERY
      ) {
        $data['message'] = 'too many sensors requested and/or auth tokens presented; please divide sensors into batches and/or use only the tokens needed for the sensors requested';
      } else if(count($auth_tokens_presented) > $MAX_AUTH_KEYS_PROVIDED_PER_SENSOR_QUERY) {
        // this check should be redundant with >1 check as well as global check above
        $data['message'] = 'too many auth tokens presented';
      } else {
        $unauthenticated_or_nonexistent_sensors = array();
        foreach($names as $name) {
          $sensor_is_open = in_array($name, $OPEN_SENSORS);
          // test whether they provided the "global" auth token that works for all sensors:
          $sensor_authenticated_globally = in_array($AUTH['sensors'], $auth_tokens_presented);
          // test whether they provided a "granular" auth token for one of the
          // sensor_subsets containing this sensor (if any):
          $sensor_authenticated_granularly = false;
          if(array_key_exists($name, $GRANULAR_SENSOR_AUTH_TOKENS)) {
            $acceptable_granular_tokens_for_sensor = $GRANULAR_SENSOR_AUTH_TOKENS[$name];
            // check for nonempty intersection between provided and acceptable
            // granular auth tokens:
            foreach($acceptable_granular_tokens_for_sensor as $acceptable_granular_token) {
              if(in_array($acceptable_granular_token, $auth_tokens_presented)) {
                $sensor_authenticated_granularly = true;
                break;
              }
            }
          } // (else: there are no granular tokens for this sensor; can't authenticate granularly)
          if(! $sensor_is_open &&
             ! $sensor_authenticated_globally &&
             ! $sensor_authenticated_granularly) {
            // authentication failed for this sensor; append to list:
            array_push($unauthenticated_or_nonexistent_sensors, $name);
          }
        }
        if (!empty($unauthenticated_or_nonexistent_sensors)) {
          $data['message'] = 'unauthenticated/nonexistent sensor(s): ' . implode(',', $unauthenticated_or_nonexistent_sensors);
          // // Alternative message that may enable shorter tokens:
          // $data['message'] = 'some/all sensors requested were unauthenticated/nonexistent';
        } else {
          // parse the request
          $locations = extract_values($_REQUEST['locations'], 'str');
          $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
          // get the data
          $epidata = get_sensors($names, $locations, $epiweeks);
          store_result($data, $epidata);
        }
      }
    }
  } else if($source === 'dengue_sensors') {
    if(require_all($data, array('auth', 'names', 'locations', 'epiweeks'))) {
      if($_REQUEST['auth'] === $AUTH['sensors']) {
        // parse the request
        $names = extract_values($_REQUEST['names'], 'str');
        $locations = extract_values($_REQUEST['locations'], 'str');
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        // get the data
        $epidata = get_dengue_sensors($names, $locations, $epiweeks);
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
  } else if($source === 'dengue_nowcast') {
    if(require_all($data, array('locations', 'epiweeks'))) {
      // parse the request
      $locations = extract_values($_REQUEST['locations'], 'str');
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      // get the data
      $epidata = get_dengue_nowcast($locations, $epiweeks);
      store_result($data, $epidata);
    }
  } else if($source === 'meta') {
    // get the data
    $epidata = get_meta();
    store_result($data, $epidata);
  } else if($source === 'meta_norostat') {
    if(require_all($data, array('auth'))) {
      if($_REQUEST['auth'] === $AUTH['norostat']) {
        $epidata = get_meta_norostat();
        store_result($data, $epidata);
      } else {
          $data['message'] = 'unauthenticated';
      }
    }
  } else if($source === 'meta_afhsb') {
    if(require_all($data, array('auth'))) {
      if($_REQUEST['auth'] === $AUTH['afhsb']) {
        $epidata = get_meta_afhsb();
        store_result($data, $epidata);
      } else {
          $data['message'] = 'unauthenticated';
      }
    }
  } else if($source === 'covidcast') {
    if(require_all($data, array('data_source', 'signal', 'time_type', 'geo_type', 'time_values', 'geo_value'))) {
      // parse the request
      $time_values = extract_values($_REQUEST['time_values'], 'int');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      $epidata = get_covidcast(
          $_REQUEST['data_source'],
          $_REQUEST['signal'],
          $_REQUEST['time_type'],
          $_REQUEST['geo_type'],
          $time_values,
          $_REQUEST['geo_value'],
          $issues,
          $lag);
      store_result($data, $epidata);
    }
  } else if($source === 'covidcast_meta') {
    // get the metadata
    if (isset($_REQUEST['cached']) && $_REQUEST['cached'] === 'true') {
      $epidata = get_covidcast_meta_cached();
    } else {
      $epidata = get_covidcast_meta();
    }
    store_result($data, $epidata);
  } else {
    $data['message'] = 'no data source specified';
  }
  // API analytics
  record_analytics($source, $data);
} else {
  $data['message'] = 'database error';
}

// send the response as a json object
header('Content-Type: application/json');
echo json_encode($data);
?>
