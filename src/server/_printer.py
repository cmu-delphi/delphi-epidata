from flask import request, jsonify, abort, make_response, request
from werkzeug.exceptions import HTTPException
from flask.json import dumps
from ._analytics import record_analytics
from typing import Dict

MAX_RESULTS = 1000


def _is_using_status_codes() -> bool:
    return request.values.get("format", "classic") not in ["classic", "tree"]


class EpiDataException(HTTPException):
    def __init__(self, message: str, status_code: int = 500):
        super(EpiDataException, self).__init__(message)
        self.code = status_code if _is_using_status_codes() else 200
        self.response = make_response(
            dumps(dict(result=-1, message=message)),
            self.code,
        )
        self.response.mimetype = "application/json"
        record_analytics(-1)


class MissingOrWrongSourceException(EpiDataException):
    def __init__(self):
        super(MissingOrWrongSourceException, self).__init__(
            "no data source specified", 400
        )


class UnAuthenticatedException(EpiDataException):
    def __init__(self):
        super(UnAuthenticatedException, self).__init__("unauthenticated", 401)


class ValidationFailedException(EpiDataException):
    def __init__(self, message: str):
        super(ValidationFailedException, self).__init__(message, 400)


class DatabaseErrorException(EpiDataException):
    def __init__(self):
        super(DatabaseErrorException, self).__init__("database error", 500)


class APrinter:
    count: int = 0
    result: int = -1
    _began = False
    _use_status_codes = True
    endpoint: str

    def __init__(self, endpoint: str, use_status_codes=True):
        self.endpoint = endpoint
        self._use_status_codes = use_status_codes

    def print_non_standard(self, data):
        """
        prints a non standard JSON message
        """
        self._result = 1
        record_analytics(1)
        # TODO
        return jsonify(dict(result=self._result, message="success", epidata=data))

    @property
    def remaining_rows(self) -> int:
        return MAX_RESULTS - self._count

    def __enter__(self):
        self._begin()
        return self

    def _begin(self):
        if self._began:
            return
        self._began = True
        self.result = -2  # no result
        self._begin_impl()

    def _begin_impl(self):
        # hook
        pass

    def __call__(self, row: Dict):
        if not self._began:
            self._begin()
        first = self.count == 0
        if self.count >= MAX_RESULTS:
            # hit the limit
            self.result = 2
            return
        if first:
            self.result = 1  # at least one row
        self._print_row(first, row)
        self.count += 1

    def _print_row_impl(self, first: bool, row: Dict):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._began:
            return
        # record_analytics($this->endpoint, $this->result, $this->count)
        self._end_impl()

    def _end_impl(self):
        # hook
        pass


# interface IRowPrinter {
#   /**
#    * returns the number of possible remaining rows to fetch, if < 0 it means no limit
#    */
#   public function remainingRows(): int;
#   /**
#    * starts printing rows, can be called multiple times without harm
#    */
#   public function begin();
#   /**
#    * print a specific row
#    */
#   public function printRow(array &$row);
#   /**
#    * finish writing rows needs to be called once
#    */
#   public function end();
# }

# class CollectRowPrinter implements IRowPrinter {
#   public array $data = [];

#   public function remainingRows(): int {
#     global $MAX_RESULTS;
#     return $MAX_RESULTS - count($this->data);
#   }

#   public function begin() {
#     // dummy
#   }
#   public function printRow(array &$row) {
#     array_push($this->data, $row);
#   }
#   public function end() {
#     // dummy
#   }
# }

# /**
#  * a printer class writing in the classic epidata format
#  */
# class ClassicPrinter extends APrinter {

#   function __construct(string $endpoint) {
#     parent::__construct($endpoint, FALSE);
#   }

#   protected function beginImpl() {
#     header('Content-Type: application/json');
#     echo '{ "epidata": [';
#   }

#   protected function printRowImpl(bool $first, array &$row) {
#     if (!$first) {
#       echo ',';
#     }
#     echo json_encode($row);
#   }

#   protected function endImpl() {
#     $message = $this->count == 0 ? 'no results' : ($this->result == 2 ? 'too many results, data truncated' : 'success');
#     $messageEncoded = json_encode($message);
#     echo "], \"result\": {$this->result}, \"message\": {$messageEncoded} }";
#   }
# }

# /**
#  * a printer class writing a tree by the given grouping criteria as the first element in the epidata array
#  */
# class ClassicTreePrinter extends ClassicPrinter {
#   private array $tree = [];
#   private string $group;

#   function __construct(string $endpoint, string $group) {
#     parent::__construct($endpoint);
#     $this->group = $group;
#   }

#   protected function printRowImpl(bool $first, array &$row) {
#     $group = isset($row[$this->group]) ? $row[$this->group] : '';
#     unset($row[$this->group]);
#     if (isset($this->tree[$group])) {
#       array_push($this->tree[$group], $row);
#     } else {
#       $this->tree[$group] = [$row];
#     }
#   }

#   private function printTree() {
#     if (count($this->tree) == 0) {
#       echo '{}'; // force object style
#     } else {
#       echo json_encode($this->tree);
#     }
#     // clean up
#     $this->tree = [];
#   }

#   protected function endImpl() {
#     $this->printTree();
#     parent::endImpl();
#   }
# }


class CSVPrinter(APrinter):
    """
    a printer class writing in a CSV file
    """

    def _begin_impl(self):
        # header('Content-Type: text/csv; charset=utf8');
        # header('Content-Disposition: attachment; filename=epidata.csv');
        pass

    def _print_row_impl(self, first: bool, row: Dict):
        #     if ($first) {
        #   // print headers
        #   $headers = array_keys($row);
        #   fputcsv($this->out, $headers);
        # }
        # fputcsv($this->out, $row);
        pass

    def _end_impl(self):
        # echo ']'
        pass


class JSONPrinter(APrinter):
    """
    a printer class writing in a JSON array
    """

    def _begin_impl(self):
        # TODO header('Content-Type: application/json')
        # echo '['
        pass

    def _print_row_impl(self, first: bool, row: Dict):
        sep = "," if not first else ""
        return f"{sep}{dumps(row)}"

    def _end_impl(self):
        # echo ']'
        pass


class JSONLPrinter(APrinter):
    """
    a printer class writing in JSONLines format
    """

    def _begin_impl(self):
        # TODO
        # there is no official mime type for json lines
        # header('Content-Type: text/plain; charset=utf8');
        pass

    def _print_row_impl(self, first: bool, row: Dict):
        # each line is a JSON file with a new line to separate them
        return f"{dumps(row)}\n"


def create_printer(endpoint: str):
    format = request.values.get("format", "classic")
    # if format == "tree":
    #     return ClassicTreePrinter(endpoint, "signal")
    # if format == "json":
    return JSONPrinter(endpoint)
    # if format == "csv":
    #     return CSVPrinter(endpoint)
    # if format == "jsonl":
    #     return JSONLPrinter(endpoint)
    # return ClassicPrinter(endpoint)
