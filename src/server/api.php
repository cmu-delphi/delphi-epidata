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

/*
 * main function
 */
function main() {


  if (!database_connect()) {
    return $printer->send_database_error();
  }
  // connected to the database
}
main();
?>