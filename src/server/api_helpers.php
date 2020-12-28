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


// executes a query, casts the results, and returns an array of the data
// the number of results is limited to $MAX_RESULTS
//   $query (required): a SQL query string
//   $printer (required): the row printer to use
//   $fields_string (optional): an array of names of string fields
//   $fields_int (optional): an array of names of integer fields
//   $fields_float (optional): an array of names of float fields
function execute_query(string $query, IRowPrinter &$printer, ?array $fields_string = null, ?array $fields_int = null, ?array $fields_float = null, bool $single_query = TRUE) {
  global $dbh;
  if ($printer->remainingRows() >= 0) {
    $limit = $printer->remainingRows() + 1;
    $fullQuery = $query . " LIMIT {$limit}"; // +1 to know if there is more
  } else {
    $fullQuery = $query; // no limit
  }
  error_log($fullQuery);
  $result = mysqli_real_query($dbh, $fullQuery);
  if (!$result) {
    error_log("Bad query: ".$query);
    error_log(mysqli_error($dbh));
    return;
  }
  $result = mysqli_use_result($dbh);

  if (isset($_REQUEST['fields'])) {
    $fields = extract_values($_REQUEST['fields'], 'str');
    // limit fields to the selection
    if($fields_string !== null) {
      $fields_string = array_intersect($fields_string, $fields);
    }
    if($fields_int !== null) {
      $fields_int = array_intersect($fields_int, $fields);
    }
    if($fields_float !== null) {
      $fields_float = array_intersect($fields_float, $fields);
    }
  }

  $printer->begin();

  while ($row = mysqli_fetch_array($result)) {
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
    $printer->printRow($values);
  }
  mysqli_free_result($result);

  if ($single_query) {
    // unless we are going to append more, we end the printing
    $printer->end();
  }
}

function execute_query_append(string $query, IRowPrinter &$printer, ?array $fields_string, ?array $fields_int, ?array $fields_float) {
  return execute_query($query, $printer, $fields_string, $fields_int, $fields_float, FALSE);
}

interface IRowPrinter {
  /**
   * returns the number of possible remaining rows to fetch, if < 0 it means no limit
   */
  public function remainingRows(): int;
  /**
   * starts printing rows, can be called multiple times without harm
   */
  public function begin();
  /**
   * print a specific row
   */
  public function printRow(array &$row);
  /**
   * finish writing rows needs to be called once
   */
  public function end();
}

class CollectRowPrinter implements IRowPrinter {
  public array $data = [];

  public function remainingRows(): int {
    global $MAX_RESULTS;
    return $MAX_RESULTS - count($this->data);
  }

  public function begin() {
    // dummy
  }
  public function printRow(array &$row) {
    array_push($this->data, $row);
  }
  public function end() {
    // dummy
  }
}

abstract class APrinter implements IRowPrinter {
  /**
   * number of rows that were printed
   */
  public int $count = 0;
  /**
   * message result status
   */
  public int $result = -1;
  /**
   * flag whether begin was called
   */
  protected bool $began = FALSE;
  /**
   * flag for using status codes for handling errors
   */
  protected bool $useStatusCodes = TRUE;
  /**
   * the endpoint selected by the user
   */
  public string $endpoint;

  function __construct(string $endpoint, bool $useStatusCodes = TRUE) {
    $this->endpoint = $endpoint;
    $this->useStatusCodes = $useStatusCodes;
  }

  /**
   * prints a generic error
   * @param {int} $result the message result
   * @param {string} $message the message itself
   * @param {int} $statusCode http status code if status codes are enabled in this printer
   */
  public function printError(int $result, string $message, int $statusCode = 500) {
    $this->result = $result;
    if ($this->useStatusCodes) {
      http_response_code($statusCode);
    }
    header('Content-Type: application/json');
    echo json_encode(array('result' => $result, 'message' => $message));
    record_analytics($this->endpoint, $this->result);
  }

  public function printDatabaseError() {
    $this->printError(-1, 'database error', 500);
  }

  public function printUnAuthenticated() {
    $this->printError(-1, 'unauthenticated', 401);
  }

  public function printValidationFailed(string $message) {
    $this->printError(-1, $message, 400);
  }

  public function printMissingOrWrongSource() {
    $this->printError(-1, 'no data source specified', 400);    
  }

  /**
   * prints a non standard JSON message
   */
  public function printNonStandard(mixed &$data) {
    $this->result = 1;
    header('Content-Type: application/json');
    echo json_encode(array('result' => $this->result, 'message' => 'success', 'epidata' => $data));
    record_analytics($this->endpoint, $this->result);
  }

  public function remainingRows(): int {
    global $MAX_RESULTS;
    return $MAX_RESULTS - $this->count;
  }

  public function begin() {
    if ($this->began) {
      return;
    }
    $this->began = TRUE;
    $this->result = -2; // no result
    $this->beginImpl();
  }

  protected function beginImpl() {
    // hook
  }

  public function printRow(array &$row) {
    global $MAX_RESULTS;
    if (!$this->began) {
      $this->begin();
    }
    $first = $this->count == 0;
    if ($this->count >= $MAX_RESULTS) {
      // hit the limit
      $this->result = 2;
      return;
    }
    if ($first) {
      $this->result = 1; // at least one row
    }
    $this->printRowImpl($first, $row);
    $this->count++;
  }

  protected abstract function printRowImpl(bool $first, array &$row);

  public function end() {
    if (!$this->began) {
      return;
    }
    $this->endImpl();
    record_analytics($this->endpoint, $this->result, $this->count);
  }

  protected function endImpl() {
    // hook
  }
}

/**
 * a printer class writing in the classic epidata format
 */
class ClassicPrinter extends APrinter {

  function __construct(string $endpoint) {
    parent::__construct($endpoint, FALSE);
  }

  protected function beginImpl() {
    header('Content-Type: application/json');
    echo '{ "epidata": [';
  }

  protected function printRowImpl(bool $first, array &$row) {
    if (!$first) {
      echo ',';
    }
    echo json_encode($row);
  }

  protected function endImpl() {
    $message = $this->count == 0 ? 'no results' : ($this->result == 2 ? 'too many results, data truncated' : 'success');
    $messageEncoded = json_encode($message);
    echo "], \"result\": {$this->result}, \"message\": {$messageEncoded} }";
  }
}

/**
 * a printer class writing a tree by the given grouping criteria as the first element in the epidata array
 */
class ClassicTreePrinter extends ClassicPrinter {
  private array $tree = [];
  private string $group;

  function __construct(string $endpoint, string $group) {
    parent::__construct($endpoint);
    $this->group = $group;
  }

  protected function printRowImpl(bool $first, array &$row) {
    $group = isset($row[$this->group]) ? $row[$this->group] : '';
    unset($row[$this->group]);      
    if (isset($this->tree[$group])) {
      array_push($this->tree[$group], $row);
    } else {
      $this->tree[$group] = [$row];
    }
  }

  private function printTree() {
    if (count($this->tree) == 0) {
      echo '{}'; // force object style
    } else {
      echo json_encode($this->tree);
    }
    // clean up
    $this->tree = [];
  }

  protected function endImpl() {
    $this->printTree();
    parent::endImpl();
  }
}

/**
 * a printer class writing in a CSV file
 */
class CSVPrinter extends APrinter {
  private $out = null;

  protected function beginImpl() {
    $this->out = fopen('php://output', 'w');
    header('Content-Type: text/csv; charset=utf8');
    header('Content-Disposition: attachment; filename=epidata.csv');
  }

  protected function printRowImpl(bool $first, array &$row) {
    if ($first) {
      // print headers
      $headers = array_keys($row);
      fputcsv($this->out, $headers);  
    }
    fputcsv($this->out, $row);
  }

  protected function endImpl() {
    fclose($this->out);
  }
}

/**
 * a printer class writing in a JSON array
 */
class JSONPrinter extends APrinter {
  protected function beginImpl() {
    header('Content-Type: application/json');
    echo '[';
  }

  protected function printRowImpl(bool $first, array &$row) {
    if (!$first) {
      echo ',';
    }
    echo json_encode($row);
  }

  protected function endImpl() {
    echo ']';
  }
}

/**
 * a printer class writing in JSONLines format
 */
class JSONLPrinter extends APrinter {
  protected function beginImpl() {
    // there is no official mime type for json lines
    header('Content-Type: text/plain; charset=utf8');
  }

  protected function printRowImpl(bool $first, array &$row) {
    // each line is a JSON file with a new line to separate them
    echo json_encode($row);
    echo "\n";
  }
}

function createPrinter(string $endpoint, string $format = 'classic') {
  switch($format) {
  case 'tree':
    return new ClassicTreePrinter($endpoint, 'signal');
  case 'json': 
    return new JSONPrinter($endpoint);
  case 'csv': 
    return new CSVPrinter($endpoint);
  case 'jsonl':
    return new JSONLPrinter($endpoint);
  default:
    return new ClassicPrinter($endpoint);
  }
}

?>
