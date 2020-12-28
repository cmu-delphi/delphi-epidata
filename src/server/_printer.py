from flask import (
    request,
    jsonify,
    abort,
    make_response,
    request,
    Response,
    stream_with_context,
)
from werkzeug.exceptions import HTTPException
from flask.json import dumps
from ._analytics import record_analytics
from typing import Dict, Iterable, Any, Union, Optional, List


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

    def make_response(self, gen):
        return Response(
            gen,
            mimetype="application/json",
        )

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
        return MAX_RESULTS - self.count

    def begin(self):
        self.result = -2  # no result
        return self._begin_impl()

    def _begin_impl(self):
        # hook
        return None

    def __call__(self, row: Dict) -> Optional[Union[str, bytes]]:
        first = self.count == 0
        if self.count >= MAX_RESULTS:
            # hit the limit
            self.result = 2
            return None
        if first:
            self.result = 1  # at least one row
        self.count += 1
        return self._print_row(first, row)

    def _print_row(self, first: bool, row: Dict) -> Optional[Union[str, bytes]]:
        return None

    def end(self) -> Optional[Union[str, bytes]]:
        record_analytics(self.result, self.count)
        return self._end_impl()

    def _end_impl(self):
        # hook
        return None


class ClassicPrinter(APrinter):
    """
    a printer class writing in the classic epidata format
    """

    def _begin_impl(self):
        return '{ "epidata": ['

    def _print_row(self, first: bool, row: Dict):
        sep = "," if not first else ""
        return f"{sep}{dumps(row)}"

    def _end_impl(self):
        message = "success"
        if self.count == 0:
            message = "no results"
        elif self.result == 2:
            message = "too many results, data truncated"
        return f'], "result": {self.result}, "message": {dumps(message)} }}'


class ClassicTreePrinter(ClassicPrinter):
    """
    a printer class writing a tree by the given grouping criteria as the first element in the epidata array
    """

    group: str
    _tree: Dict[str, List[Dict]] = dict()

    def __init__(self, group: str):
        super(ClassicTreePrinter, self).__init__()
        self.group = group
        self._tree = dict()

    def _print_row(self, first: bool, row: Dict):
        group = row.get(self.group, "")
        del row[self.group]
        if group in self._tree:
            self._tree[group].append(row)
        else:
            self._tree[group] = [row]
        return None

    def _end_impl(self):
        tree = dumps(self._tree)
        self._tree = dict()
        r = super(ClassicTreePrinter, self)._end_impl()
        return f"{tree}{r}"


class CSVPrinter(APrinter):
    """
    a printer class writing in a CSV file
    """

    def make_response(self, gen):
        return Response(
            gen,
            mimetype="text/csv; charset=utf8",
            headers={"Content-Disposition": "attachment; filename=epidata.csv"},
        )

    def _begin_impl(self):
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
        return "["

    def _print_row(self, first: bool, row: Dict):
        sep = "," if not first else ""
        return f"{sep}{dumps(row)}"

    def _end_impl(self):
        return "]"


class JSONLPrinter(APrinter):
    """
    a printer class writing in JSONLines format
    """

    def make_response(self, gen):
        return Response(gen, mimetype=" text/plain; charset=utf8")

    def _print_row(self, first: bool, row: Dict):
        # each line is a JSON file with a new line to separate them
        return f"{dumps(row)}\n"


def create_printer():
    format = request.values.get("format", "classic")
    if format == "tree":
        return ClassicTreePrinter("signal")
    if format == "json":
        return JSONPrinter()
    if format == "csv":
        return CSVPrinter()
    if format == "jsonl":
        return JSONLPrinter()
    return ClassicPrinter()


def send_rows(generator: Iterable[Dict[str, Any]]):
    printer = create_printer()

    def gen():
        r = printer.begin()
        if r is not None:
            yield r
        for row in generator:
            r = printer(row)
            if r is not None:
                yield r
        r = printer.end()
        if r is not None:
            yield r

    return printer.make_response(stream_with_context(gen()))


# , execution_options={"stream_results": True}
