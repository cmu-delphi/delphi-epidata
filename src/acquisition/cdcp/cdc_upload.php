<?php

/*
A website for DELPHI members to upload CDC page visit statistics. Uploaded
files will eventually be extracted, inserted into the database, and made
available though the Epidata API.

See cdc_upload.py for many more details.
*/

require_once('/var/www/html/secrets.php');
$hmacSecret = Secrets::$cdcp['hmac'];
$dbUser = Secrets::$db['epi'][0];
$dbPass = Secrets::$db['epi'][1];
$dbHost = 'localhost';
$dbPort = 3306;
$dbName = 'epidata';
$dbh = mysql_connect("{$dbHost}:{$dbPort}", $dbUser, $dbPass);
if($dbh) {
   mysql_select_db($dbName, $dbh);
}
?><!doctype html>
<html>
  <head>
    <title>CDC Page Stats</title>
    <meta charset="utf-8">
    <style>
      * { margin: 0; box-sizing: border-box; }
      html, body { width: 100%; height: 100%; }
      body { background: radial-gradient(#fff,#ccc); }
      body { font-family: Calibri, Candara, Segoe, "Segoe UI", Optima, Arial, sans-serif; text-align: center; }
      input { margin: 16px; }
      form { border: 1px solid #888; border-radius: 8px; }
      .full { width: 100%; height: 100%; }
      .centered { display: flex; justify-content: center; align-items: center; flex-direction: column; }
    </style>
  </head>
  <body>
    <div class="full centered">
      <div>
        <?php
        if(!$dbh) {
          printf('Error: No connection to database.', $fileType);
        } elseif(isset($_POST['submit'])) {
          ?>
          <h1>Upload Result</h1>
          <?php
          $fileName = basename($_FILES['zip_file']['name']);
          $fileType = pathinfo($fileName, PATHINFO_EXTENSION);
          if($_FILES['zip_file']['error'] > 0) {
            printf('Error: upload failed (%d)', intval($_FILES['zip_file']['error']));
          } else if($fileType != 'zip') {
            printf('Error: expected *.zip, got *.%s', $fileType);
          } else {
            $template = 'openssl dgst -sha256 -hmac "%s" "%s" | cut -d " " -f 2';
            $command = sprintf($template, $hmacSecret, $_FILES['zip_file']['tmp_name']);
            $hmac = trim(shell_exec($command));
            // todo - constant time comparison
            if($hmac === $_REQUEST['hmac']) {
              $target_dir = '/common/cdc_stage/';
              $target_file = $target_dir . time() . '_' . $fileName;
              if (move_uploaded_file($_FILES['zip_file']['tmp_name'], $target_file)) {
                mysql_query('CALL automation.RunStep(46)'); // Process CDCP Data
                printf('Success, thanks!');
              } else {
                printf('Error: something is wrong with file permissions.');
              }
            } else {
              $expected = substr($hmac, 0, 8) . '...';
              printf("Error: HMAC mismatch, expected [{$expected}].");
              sleep(5);
            }
          }
        } else {
          ?>
          <h1>Upload zip file</h1>
          <p>
            <?php
            $d = '????-??-??';
            $result = mysql_query('SELECT max(`date`) `date` FROM `cdc`');
            if($row = mysql_fetch_array($result)) {
              $d = $row['date'];
            }
            ?>
            (We have data through <?= $d ?>.)
          </p>
          <form method="post" enctype="multipart/form-data">
            <label>file: <input type="file" name="zip_file"></label><br>
            <label>hmac: <input type="text" name="hmac"></label><br>
            <input type="submit" name="submit" value="Upload" />
          </form>
          <?php
        }
        ?>
      </div>
      <div>
        To compute the hmac of your file, run [ <span style="font-family: monospace;">openssl dgst -sha256 -hmac "<span style="color: #888; font-style: italic;">&lt;secret&gt;</span>" "<span style="color: #888; font-style: italic;">&lt;filename&gt;</span>"</span> ]. The hmac should be a 64 character string of hex digits (32 bytes, 256 bits).
      </div>
    </div>
  </body>
</html>
