<?php

/*
The job server for wiki scraping. Any number of clients (wiki_download.py
instances) fetch jobs from, and upload results to, this server. A simple
dashboard is available from dashboard.php, visible here:
https://delphi.midas.cs.cmu.edu/~automation/public/wiki/

See wiki.py for many more details.
*/

require_once('/var/www/html/secrets.php');
$hmacSecret = Secrets::$wiki['hmac'];
$dbUser = Secrets::$db['epi'][0];
$dbPass = Secrets::$db['epi'][1];
$dbHost = 'localhost';
$dbPort = 3306;
$dbName = 'epidata';
$dbh = mysql_connect("{$dbHost}:{$dbPort}", $dbUser, $dbPass);
if(!$dbh) {
   http_response_code(500);
   echo 'db problem';
}
mysql_select_db($dbName, $dbh);
if(isset($_REQUEST['get'])) {
   $type = 0;
   if(isset($_REQUEST['type'])) {
      $type = intval($_REQUEST['type']);
   }
   mysql_query("UPDATE wiki_raw SET `status` = 0 WHERE `status` = 1 and date_add(`datetime`, interval 10 minute) < now()");
   $result = mysql_query("SELECT `id`, `name`, `hash` FROM wiki_raw WHERE `status` = {$type} ORDER BY rand() ASC LIMIT 1");
   if($row = mysql_fetch_array($result)) {
      mysql_query("UPDATE wiki_raw SET `status` = 1, `datetime` = now() WHERE `id` = {$row['id']}");
      echo "{\"id\": {$row['id']}, \"name\": \"{$row['name']}\", \"hash\": \"{$row['hash']}\"}";
   } else {
      http_response_code(201);
      echo "no jobs";
   }
} elseif(isset($_REQUEST['put']) && isset($_REQUEST['hmac'])) {
   if(hash_hmac('sha256', $_REQUEST['put'], $hmacSecret) === $_REQUEST['hmac']) {
      $obj = json_decode($_REQUEST['put']);
      mysql_query(sprintf("UPDATE wiki_raw SET `status` = 2, `datetime` = now(), `size` = %d, `worker` = '%s', `elapsed` = %.3f, `data` = '%s' WHERE `id` = %d",  intval($obj->{'size'}), mysql_real_escape_string($obj->{'worker'}), floatval($obj->{'elapsed'}), mysql_real_escape_string($obj->{'data'}),  intval($obj->{'id'})));
      echo 'ok';
   } else {
      sleep(5);
      http_response_code(400);
      echo 'wrong hmac';
   }
} else {
   http_response_code(400);
   echo 'bad request';
}
?>
