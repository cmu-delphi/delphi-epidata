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

// result limit, ~10 years of daily data
$MAX_RESULTS = 10e6;
// specify the number of seconds the script is maximally allowed to run (default 30s)
set_time_limit(60*10); // in seconds

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
function get_fluview(IRowPrinter &$printer, $epiweeks, $regions, $issues, $lag, $authorized) {
  // public data
  $table = '`fluview` fv';
  $fields = "fv.`release_date`, fv.`issue`, fv.`epiweek`, fv.`region`, fv.`lag`, fv.`num_ili`, fv.`num_patients`, fv.`num_providers`, fv.`wili`, fv.`ili`, fv.`num_age_0`, fv.`num_age_1`, fv.`num_age_2`, fv.`num_age_3`, fv.`num_age_4`, fv.`num_age_5`";
  _get_fluview_by_table($printer, $epiweeks, $regions, $issues, $lag, $table, $fields);
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
    _get_fluview_by_table($printer, $epiweeks, $regions, $issues, $lag, $table, $fields);
  }
  $printer->end();
}

// a helper function to query `fluview` and `fluview_imputed` individually
// parameters
function _get_fluview_by_table(IRowPrinter &$printer, $epiweeks, $regions, $issues, $lag, $table, $fields) {
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
  execute_query_append($query, $printer, $fields_string, $fields_int, $fields_float);
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
function get_fluview_clinical(IRowPrinter &$printer, $epiweeks, $regions, $issues, $lag) {
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
  execute_query($query, $printer, $fields_string, $fields_int, $fields_float);
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
function get_flusurv(IRowPrinter &$printer, $epiweeks, $locations, $issues, $lag) {
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
  $fields_string = array('release_date', 'location');
  $fields_int = array('issue', 'epiweek', 'lag');
  $fields_float = array('rate_age_0', 'rate_age_1', 'rate_age_2', 'rate_age_3', 'rate_age_4', 'rate_overall');
  execute_query($query, $printer, $fields_string, $fields_int, $fields_float);
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
function get_paho_dengue(IRowPrinter &$printer, $epiweeks, $regions, $issues, $lag) {
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
  execute_query($query, $printer, $fields_string, $fields_int, $fields_float);
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
function get_ecdc_ili(IRowPrinter &$printer, $epiweeks, $regions, $issues, $lag) {
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
  execute_query($query, $printer, $fields_string, $fields_int, $fields_float);
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
function get_kcdc_ili(IRowPrinter &$printer, $epiweeks, $regions, $issues, $lag) {
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
  execute_query($query, $printer, $fields_string, $fields_int, $fields_float);
}

// queries the `gft` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of location names
function get_gft(IRowPrinter &$printer, $epiweeks, $locations) {
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
  execute_query($query, $printer, array('location'), array('epiweek', 'num'), null);
}

// queries the `ght` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of location names
//   $query (required): search query or topic ID
function get_ght(IRowPrinter &$printer, $epiweeks, $locations, $query) {
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
  execute_query($query, $printer, array('location'), array('epiweek'), array('value'));
}

// queries the `twitter` table
//   $locations (required): array of location names
//   $dates (required): array of date or epiweek values/ranges
//   $resolution (required): either 'daily' or 'weekly'
function get_twitter(IRowPrinter &$printer, $locations, $dates, $resolution) {
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
    execute_query_append($query, $printer, $fields_string, $fields_int, $fields_float);
  }
  // query all states together
  if(count($states) !== 0) {
    // build the location filter
    $condition_location = filter_strings('t.`state`', $states);
    // final query for states
    $query = "SELECT {$fields}, t.`state` `location` FROM {$table} WHERE ({$condition_filter}) AND ({$condition_date}) AND ({$condition_location}) GROUP BY {$date_field}, t.`state` ORDER BY {$date_field} ASC, t.`state` ASC";
    // append query results to the epidata array
    execute_query_append($query, $printer, $fields_string, $fields_int, $fields_float);
  }
  $printer->end();
}

// queries the `wiki` table
//   $articles (required): array of article titles
//   $language (required): specify the language of articles we want to retrieve
//   $dates (required): array of date or epiweek values/ranges
//   $resolution (required): either 'daily' or 'weekly'
//   $hours (optional): array of hour values/ranges
// if present, $hours determines which counts are used within each day; otherwise all counts are used
// for example, if hours=[4], then only the 4 AM (UTC) stream is returned
function get_wiki(IRowPrinter &$printer, $articles, $language, $dates, $resolution, $hours) {
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
  execute_query($query, $printer, $fields_string, $fields_int, $fields_float);
}

// queries the `quidel` table
//   $locations (required): array of location names
//   $epiweeks (required): array of epiweek values/ranges
function get_quidel(IRowPrinter &$printer, $locations, $epiweeks) {
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
  execute_query($query, $printer, $fields_string, $fields_int, $fields_float);
}

// queries the `norostat_point` table
//   $locations (required): single location value (str listing included states)
//   $epiweeks (required): array of epiweek values/ranges
function get_norostat(IRowPrinter &$printer, $location, $epiweeks) {
  // todo add release/issue args
  //
  // build the filters:
  $condition_location = filter_strings('`norostat_raw_datatable_location_pool`.`location`', [$location]);
  $condition_epiweek = filter_integers('`latest`.`epiweek`', $epiweeks);
  // get the data from the database
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
         (`later`.`release_date`, `later`.`parse_time`) AND
       `later`.`new_value` IS NOT NULL
    WHERE ({$condition_location}) AND
          ({$condition_epiweek}) AND
          `later`.`parse_time` IS NULL AND
          `latest`.`new_value` IS NOT NULL
    ";
  // xxx may reorder epiweeks
  execute_query($query, $printer, $fields_string, $fields_int, null);
}

// queries the `afhsb_00to13` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of location names
//   $flu_types (required): array of flu types
function get_afhsb(IRowPrinter &$printer, $locations, $epiweeks, $flu_types) {
  global $dbh;
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
      _get_afhsb_by_table($printer, $location_type, $epiweeks, $locs, $disjoint_flus, $subset_flus);
    }
  }
  $printer->end();
}

// A helper function to query afhsb tables
function _get_afhsb_by_table(IRowPrinter &$printer, $location_type, $epiweeks, $locations, $disjoint_flus, $subset_flus) {
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
      execute_query_append($query, $printer, $fields_string, $fields_int, null);
  }
  // disjoint flu types: flu1, flu2-flu1, flu3-flu2, ili-flu3
  if(!empty($disjoint_flus)){
    $condition_flu = filter_strings('`flu_type`', $disjoint_flus);
    $query = "SELECT {$fields}, `flu_type` FROM {$table}
    WHERE ({$condition_epiweek}) AND ({$condition_location}) AND ({$condition_flu})
    GROUP BY {$group},`flu_type` ORDER BY {$order},`flu_type`";
    execute_query_append($query, $printer, $fields_string, $fields_int, null);
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
function get_nidss_flu(IRowPrinter &$printer, $epiweeks, $regions, $issues, $lag) {
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
  $fields_string = array('release_date', 'region');
  $fields_int = array('issue', 'epiweek', 'lag', 'visits');
  $fields_float = array('ili');
  execute_query($query, $printer, $fields_string, $fields_int, $fields_float);
}

// queries the `nidss_dengue` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of region and/or location names
function get_nidss_dengue(IRowPrinter &$printer, $epiweeks, $locations) {
  global $dbh;
  // build the epiweek filter
  $condition_epiweek = filter_integers('nd.`epiweek`', $epiweeks);
  // get the data from the database
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
    execute_query_append($query, $printer, $fields_string, $fields_int, null);
  }
  $printer->end();
}

// queries the `forecasts` table
//   $system (required): system name
//   $epiweek (required): epiweek on which the forecast was made
function get_forecast(IRowPrinter &$printer, $system, $epiweek) {
  global $dbh;
  // get the data from the database
  $system = mysqli_real_escape_string($dbh, $system);
  $query = "SELECT `system`, `epiweek`, `json` FROM `forecasts` WHERE `system` = '{$system}' AND `epiweek` = {$epiweek}";
  $collector = new CollectRowPrinter();
  $fields_string = array('system', 'json');
  $fields_int = array('epiweek');
  execute_query($query, $collector, $fields_string, $fields_int, null);

  $data = $collector->$data;
  
  // parse forecast data
  $printer->begin();
  if(count($data) === 1 && array_key_exists('json', $data[0])) {
    $data[0]['forecast'] = json_decode($data[0]['json']);
    unset($data[0]['json']);
    $printer->printRow($data[0]);
  }
  $printer->end();
}

// queries the `cdc_extract` table
//   $epiweeks (required): array of epiweek values/ranges
//   $locations (required): array of location names
function get_cdc(IRowPrinter &$printer, $epiweeks, $locations) {
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
    execute_query_append($query, $printer, $fields_string, $fields_int, null);
  }
  // query all states together
  if(count($states) !== 0) {
    $fields = "c.`state` `location`, c.`epiweek`, c.`num1`, c.`num2`, c.`num3`, c.`num4`, c.`num5`, c.`num6`, c.`num7`, c.`num8`, c.`total`";
    // build the location filter
    $condition_location = filter_strings('c.`state`', $states);
    // final query for states
    $query = "SELECT {$fields} FROM {$table} WHERE ({$condition_epiweek}) AND ({$condition_location}) ORDER BY {$order}, c.`state` ASC";
    // append query results to the epidata array
    execute_query_append($query, $printer, $fields_string, $fields_int, null);
  }
  $printer->end();
}

/*
 * main function
 */
function main() {
  // endpoint parameter with a fallback to source parameter for compatibility reasons
  $endpoint = isset($_REQUEST['endpoint']) ? strtolower($_REQUEST['endpoint']) : (isset($_REQUEST['source']) ? strtolower($_REQUEST['source']) : '');
  $format = isset($_REQUEST['format']) ? $_REQUEST['format'] : 'classic';
  $printer = createPrinter($endpoint, $format);

  if (!$endpoint) {
    return $printer->printMissingOrWrongSource();
  }

  if (!database_connect()) {
    return $printer->send_database_error();
  }
  // connected to the database

  // switch the data source
  
  if($endpoint === 'fluview') {
    if(require_all($printer, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      $authorized = isset($_REQUEST['auth']) && $_REQUEST['auth'] === $AUTH['fluview'];
      // get the data
      get_fluview($printer, $epiweeks, $regions, $issues, $lag, $authorized);
    }
  } else if($endpoint === 'fluview_meta') {
    // get the data
    meta_fluview($printer);
  } else if ($endpoint === 'fluview_clinical') {
    if(require_all($printer, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      get_fluview_clinical($printer, $epiweeks, $regions, $issues, $lag);
    }
  } else if($endpoint === 'flusurv') {
    if(require_all($printer, array('epiweeks', 'locations'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $locations = extract_values($_REQUEST['locations'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      get_flusurv($printer, $epiweeks, $locations, $issues, $lag);
    }
  } else if ($endpoint === 'paho_dengue') {
    if(require_all($printer, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      get_paho_dengue($printer, $epiweeks, $regions, $issues, $lag);
    }
  } else if ($endpoint === 'ecdc_ili') {
    if(require_all($printer, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      get_ecdc_ili($printer, $epiweeks, $regions, $issues, $lag);
    }
  } else if ($endpoint === 'kcdc_ili') {
    if(require_all($printer, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      get_kcdc_ili($printer, $epiweeks, $regions, $issues, $lag);
    }
  } else if($endpoint === 'ilinet' || $endpoint === 'stateili') {
    // these two sources are now combined into fluview
    $printer->printError(-1, 'use fluview instead');
  } else if($endpoint === 'gft') {
    if(require_all($printer, array('epiweeks', 'locations'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $locations = extract_values($_REQUEST['locations'], 'str');
      // get the data
      get_gft($printer, $epiweeks, $locations);
    }
  } else if($endpoint === 'ght') {
    if(require_all($printer, array('auth', 'epiweeks', 'locations', 'query'))) {
      if($_REQUEST['auth'] === $AUTH['ght']) {
        // parse the request
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        $locations = extract_values($_REQUEST['locations'], 'str');
        $query = $_REQUEST['query'];
        // get the data
        get_ght($printer, $epiweeks, $locations, $query);
      } else {
        $printer->printUnAuthenticated();
      }
    }
  } else if($endpoint === 'twitter') {
    if(require_all($printer, array('auth', 'locations'))) {
      if($_REQUEST['auth'] === $AUTH['twitter']) {
        // parse the request
        $locations = extract_values($_REQUEST['locations'], 'str');
        if(require_any($printer, array('dates', 'epiweeks'))) {
          if(isset($_REQUEST['dates'])) {
            $resolution = 'daily';
            $dates = extract_values($_REQUEST['dates'], 'int');
          } else {
            $resolution = 'weekly';
            $dates = extract_values($_REQUEST['epiweeks'], 'int');
          }
          // get the data
          get_twitter($printer, $locations, $dates, $resolution);
        }
      } else {
        $printer->printUnAuthenticated();
      }
    }
  } else if($endpoint === 'wiki') {
    if(require_all($printer, array('articles', 'language'))) {
      // parse the request
      $articles = extract_values($_REQUEST['articles'], 'str');
      $language = $_REQUEST['language'];
      if(require_any($printer, array('dates', 'epiweeks'))) {
        if(isset($_REQUEST['dates'])) {
          $resolution = 'daily';
          $dates = extract_values($_REQUEST['dates'], 'int');
        } else {
          $resolution = 'weekly';
          $dates = extract_values($_REQUEST['epiweeks'], 'int');
        }
        $hours = isset($_REQUEST['hours']) ? extract_values($_REQUEST['hours'], 'int') : null;
        // get the data
        get_wiki($printer, $articles, $language, $dates, $resolution, $hours);
      }
    }
  } else if($endpoint === 'quidel') {
    if(require_all($printer, array('auth', 'locations', 'epiweeks'))) {
      if($_REQUEST['auth'] === $AUTH['quidel']) {
        // parse the request
        $locations = extract_values($_REQUEST['locations'], 'str');
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        // get the data
        get_quidel($printer, $locations, $epiweeks);
      } else {
        $printer->printUnAuthenticated();
      }
    }
  } else if($endpoint === 'norostat') {
    if(require_all($printer, array('auth', 'location', 'epiweeks'))) {
      if($_REQUEST['auth'] === $AUTH['norostat']) {
        // parse the request
        $location = $_REQUEST['location'];
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        // get the data
        get_norostat($printer, $location, $epiweeks);
      } else {
        $printer->printUnAuthenticated();
      }
    }
  } else if($endpoint === 'afhsb') {
    if(require_all($printer, array('auth', 'locations', 'epiweeks', 'flu_types'))) {
      if($_REQUEST['auth'] === $AUTH['afhsb']) {
        // parse the request
        $locations = extract_values($_REQUEST['locations'], 'str');
        $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
        $flu_types = extract_values($_REQUEST['flu_types'], 'str');
        // get the data
        get_afhsb($printer, $locations, $epiweeks, $flu_types);
      } else {
        $printer->printUnAuthenticated();
      }
    }
  } else if($endpoint === 'nidss_flu') {
    if(require_all($printer, array('epiweeks', 'regions'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $regions = extract_values($_REQUEST['regions'], 'str');
      $issues = isset($_REQUEST['issues']) ? extract_values($_REQUEST['issues'], 'int') : null;
      $lag = isset($_REQUEST['lag']) ? intval($_REQUEST['lag']) : null;
      // get the data
      get_nidss_flu($printer, $epiweeks, $regions, $issues, $lag);
    }
  } else if($endpoint === 'nidss_dengue') {
    if(require_all($printer, array('epiweeks', 'locations'))) {
      // parse the request
      $epiweeks = extract_values($_REQUEST['epiweeks'], 'int');
      $locations = extract_values($_REQUEST['locations'], 'str');
      // get the data
      get_nidss_dengue($printer, $epiweeks, $locations);
    }
  } else if($endpoint === 'delphi') {
    if(require_all($printer, array('system', 'epiweek'))) {
      // parse the request
      $system = $_REQUEST['system'];
      $epiweek = intval($_REQUEST['epiweek']);
      // get the data
      get_forecast($printer, $system, $epiweek);
    }
  }
}
main();
?>