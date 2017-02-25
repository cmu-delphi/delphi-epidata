<?php

/*
A simple, realtime, and readonly dashboard for wiki scraping jobs.

See wiki.py for many more details.
*/

require_once('/var/www/html/secrets.php');
$dbUser = Secrets::$db['epi'][0];
$dbPass = Secrets::$db['epi'][1];
$dbHost = 'localhost';
$dbPort = 3306;
$dbName = 'epidata';
$dbh = mysql_connect("{$dbHost}:{$dbPort}", $dbUser, $dbPass);
if(!$dbh) {
   http_response_code(500);
}
mysql_select_db($dbName, $dbh);
?><!doctype html>
<html>
   <head>
      <meta http-equiv="refresh" content="60">
      <title>
         Wiki Status
      </title>
      <style>
         body {
            font-size: 75%;
         }
         h1 {
            text-align: center;
            margin: 0;
            margin-top: 10px;
            /*display: none;*/
         }
         table {
            border-collapse: collapse;
         }
         th {
            background-color: #eee;
         }
         th,td {
            padding: 0px;
            padding-left: 10px;
            padding-right: 10px;
            text-align: left;
         }
         .block {
            display: inline-block;
            width: 3px;
            height: 256px;
            margin: 0;
            padding: 0;
            border-left: 1px solid #eee;
            /*border: 1px solid #ccc;*/
         }
         .curr {
            /*border: 1px solid #444;*/
         }
         .inner {
            width: 100%;
         }
         .st_1 {
            background-color: #f00;
         }
         .st0 {
            background-color: #eee;
         }
         .st1 {
            background-color: #444;
         }
         .st2 {
            background-color: #ccc;
         }
         .st3 {
            /* background-color: #ca8; */
            background-color: #8ca;
         }
         .finished {
            background-color: #8ca;
         }
         #p0 {
            width: calc(100% - 22px);
            border: 1px solid #444;
            margin: 10px;
            padding: 0;
         }
         #p1 {
            height: 100%;
            margin: 0;
            padding: 3px;
            background-color: #ccc;
         }
      </style>
   </head>
   <body>
      <!--
      <h1>Status</h1>
      <div id="p0"><?php
         $result = mysql_query("select sum(case when status in (2,3) then 1 else 0 end) / count(1) progress from wiki_raw");
         $progress = 0;
         if($row = mysql_fetch_array($result)) {
            $progress = floatval($row["progress"]) * 100;
         }
         $rem = 0;
         $result = mysql_query("select (sum(case when status = 0 then 1 else 0 end) / sum(case when status = 2 and datetime >= date_sub(now(), interval 30 minute) then 1 else 0 end)) / (60 / 30) rem from wiki_raw");
         if($row = mysql_fetch_array($result)) {
            $rem = floatval($row["rem"]);
         }
      ?><div id="p1" style="width: <?php printf("%.2f%%", $progress); ?>;"><?php printf("<b>%.1f%%</b> (%.1f hr)", $progress, $rem); ?></div></div>
      -->
      <h1>Workers</h1>
      <table>
         <tr><th>Worker</th><th>Download (GB)</th><th>Num Jobs</th><th>Last Job Finished (sec)</th></tr>
         <?php
         $result = mysql_query("select substr(worker, locate('@', worker) + 1) worker, sum(size) / 1000000000 dl, count(1) jobs, unix_timestamp(now()) - unix_timestamp(max(datetime)) seen from wiki_raw where status in (2,3) group by worker having max(datetime) >= date_sub(now(), interval 1 hour) order by max(datetime)");
         $num = 0;
         while($row = mysql_fetch_array($result)) {
            printf("<tr><td>{$row['worker']}</td><td>%.1f</td><td>{$row['jobs']}</td><td>{$row['seen']}</td></tr>", floatval($row['dl']));
            $num++;
         }
         ?>
      </table>
      <p><?php printf("Total workers active in the past hour: %d", $num); ?></p>
      <h1>Jobs</h1>
      <table>
         <tr><th>Status</th><th>Num Jobs</th><th>Description</th></tr>
         <?php
         $result = mysql_query("select status, count(1) num from wiki_raw group by status order by status");
         while($row = mysql_fetch_array($result)) {
            $desc = 'unknown';
            if($row['status'] == '-1') {
               $desc = 'failed for unknown reason';
            } elseif($row['status'] == '-2') {
               $desc = 'bad hash';
            } elseif($row['status'] == '-3') {
               $desc = 'file missing';
            } elseif($row['status'] == '-4') {
               $desc = 'gunzip failed';
            } elseif($row['status'] == '0') {
               $desc = 'queued for download';
            } elseif($row['status'] == '1') {
               $desc = 'downloading';
            } elseif($row['status'] == '2') {
               $desc = 'queued for extraction';
            } elseif($row['status'] == '3') {
               $desc = 'finished';
            }
            printf("<tr><td>{$row['status']}</td><td>{$row['num']}</td><td>{$desc}</td></tr>");
         }
         ?>
      </table>
      <br />
      <?php
      $result = mysql_query("select x.block, sum(case when x.status = -1 then 1 else 0 end) st_1, sum(case when x.status = 1 then 1 else 0 end) st1, sum(case when x.status = 0 then 1 else 0 end) st0, sum(case when x.status = 2 then 1 else 0 end) st2, sum(case when x.status = 3 then 1 else 0 end) st3 from (select floor(id/256) block, status from wiki_raw) x group by x.block order by x.block asc limit 1024");
      while($row = mysql_fetch_array($result)) {
         print("<div class=\"block");
         if(intval($row['st1']) > 0) {
            print(" curr");
         }
         print("\">");
         $st_1 = intval($row['st_1']);
         $st0 = intval($row['st0']);
         $st1 = intval($row['st1']);
         $st2 = intval($row['st2']);
         $st3 = intval($row['st3']);
         $total = $st_1 + $st0 + $st1 + $st2 + $st3;
         if($st3 == $total) {
            print("<div class=\"inner finished\" style=\"height: 100%;\"></div>");
         } else {
            printf("<div class=\"inner st_1\" style=\"height: %.3f%%;\"></div>", (100 * $st_1 / $total));
            printf("<div class=\"inner st0\" style=\"height: %.3f%%;\"></div>", (100 * $st0 / $total));
            printf("<div class=\"inner st1\" style=\"height: %.3f%%;\"></div>", (100 * $st1 / $total));
            printf("<div class=\"inner st2\" style=\"height: %.3f%%;\"></div>", (100 * $st2 / $total));
            printf("<div class=\"inner st3\" style=\"height: %.3f%%;\"></div>", (100 * $st3 / $total));
         }
         print("</div>");
      }
      ?>
   </body>
</html>
