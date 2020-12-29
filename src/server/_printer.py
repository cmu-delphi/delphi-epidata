from flask import (
    request,
    jsonify,
    request,
    Response,
    stream_with_context,
)
from ._config import MAX_RESULTS
from flask.json import dumps
from ._analytics import record_analytics
from typing import Dict, Iterable, Any, Union, Optional, List
from csv import DictWriter
from io import StringIO


def print_non_standard(data):
    """
    prints a non standard JSON message
    """
    record_analytics(1)
    return jsonify(dict(result=1, message="success", epidata=data))


class APrinter:
    count: int = 0
    result: int = -1

    def make_response(self, gen):
        return Response(
            gen,
            mimetype="application/json",
        )

    def __call__(self, generator: Iterable[Dict[str, Any]]):
        def gen():
            self.result = -2  # no result
            r = self._begin()
            if r is not None:
                yield r
            for row in generator:
                r = self._print_row(row)
                if r is not None:
                    yield r
            record_analytics(self.result, self.count)
            r = self._end()
            if r is not None:
                yield r

        return self.make_response(stream_with_context(gen()))

    @property
    def remaining_rows(self) -> int:
        return MAX_RESULTS - self.count

    def _begin(self) -> Optional[Union[str, bytes]]:
        # hook
        return None

    def _print_row(self, row: Dict) -> Optional[Union[str, bytes]]:
        first = self.count == 0
        if self.count >= MAX_RESULTS:
            # hit the limit
            self.result = 2
            return None
        if first:
            self.result = 1  # at least one row
        self.count += 1
        return self._format_row(first, row)

    def _format_row(self, first: bool, row: Dict) -> Optional[Union[str, bytes]]:
        # hook
        return None

    def _end(self) -> Optional[Union[str, bytes]]:
        # hook
        return None


class ClassicPrinter(APrinter):
    """
    a printer class writing in the classic epidata format
    """

    def _begin(self):
        return '{ "epidata": ['

    def _format_row(self, first: bool, row: Dict):
        sep = "," if not first else ""
        return f"{sep}{dumps(row)}"

    def _end(self):
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

    def _begin(self):
        self._tree = dict()
        return None

    def _format_row(self, first: bool, row: Dict):
        group = row.get(self.group, "")
        del row[self.group]
        if group in self._tree:
            self._tree[group].append(row)
        else:
            self._tree[group] = [row]
        return None

    def _end(self):
        tree = dumps(self._tree)
        self._tree = dict()
        r = super(ClassicTreePrinter, self)._end_impl()
        return f"{tree}{r}"


class CSVPrinter(APrinter):
    """
    a printer class writing in a CSV file
    """

    _stream = StringIO()
    _writer: DictWriter

    def make_response(self, gen):
        return Response(
            gen,
            mimetype="text/csv; charset=utf8",
            # headers={"Content-Disposition": "attachment; filename=epidata.csv"},
        )

    def _begin(self):
        return None

    def _format_row(self, first: bool, row: Dict):
        if first:
            self._writer = DictWriter(self._stream, list(row.keys()))
            self._writer.writeheader()
        self._writer.writerow(row)
        self._stream.flush()
        v = self._stream.getvalue()
        self._stream.seek(0)
        self._stream.truncate(0)
        return v

    def _end(self):
        self._writer = None
        return None


class JSONPrinter(APrinter):
    """
    a printer class writing in a JSON array
    """

    def _begin(self):
        return "["

    def _format_row(self, first: bool, row: Dict):
        sep = "," if not first else ""
        return f"{sep}{dumps(row)}"

    def _end(self):
        return "]"


class JSONLPrinter(APrinter):
    """
    a printer class writing in JSONLines format
    """

    def make_response(self, gen):
        return Response(gen, mimetype=" text/plain; charset=utf8")

    def _format_row(self, first: bool, row: Dict):
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
