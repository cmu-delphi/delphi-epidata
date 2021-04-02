from csv import DictWriter
from io import StringIO
from typing import Any, Dict, Iterable, List, Optional, Union

from flask import Response, jsonify, request, stream_with_context
from flask.json import dumps
import orjson

from ._analytics import record_analytics
from ._config import MAX_RESULTS
from ._common import app


def print_non_standard(data):
    """
    prints a non standard JSON message
    """
    record_analytics(1, len(data) if isinstance(data, list) else 0)

    format = request.values.get("format", "classic")
    if format == "json":
        return jsonify(data)
    else:
        return jsonify(dict(result=1, message="success", epidata=data))


class APrinter:
    def __init__(self, max_results = MAX_RESULTS):
        self.count: int = 0
        self.result: int = -1
        self._max_results: int = max_results

    def make_response(self, gen):
        return Response(
            gen,
            mimetype="application/json",
        )

    def __call__(self, generator: Iterable[Dict[str, Any]]) -> Response:
        def gen():
            self.result = -2  # no result, default response
            began = False
            try:
                for row in generator:
                    if not began:
                        # do it here to catch an error before we send the begin
                        r = self._begin()
                        began = True
                        if r is not None:
                            yield r
                    r = self._print_row(row)
                    if r is not None:
                        yield r
            except Exception as e:
                app.logger.error(f'error executing')
                self.result = -1
                yield self._error(e)

            record_analytics(self.result, self.count)

            if not began:
                # do it manually to catch an error before we send the begin
                r = self._begin()
                began = True
                if r is not None:
                    yield r

            r = self._end()
            if r is not None:
                yield r

        return self.make_response(stream_with_context(gen()))

    @property
    def remaining_rows(self) -> int:
        return self._max_results - self.count

    def _begin(self) -> Optional[Union[str, bytes]]:
        # hook
        return None

    def _error(self, error: Exception) -> str:
        # send an generic error
        return dumps(dict(result=self.result, message=f"unknown error occurred: {error}",error=error, epidata=[]))

    def _print_row(self, row: Dict) -> Optional[Union[str, bytes]]:
        first = self.count == 0
        if self.count >= self._max_results:
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
        sep = b"," if not first else b""
        return sep + orjson.dumps(row)

    def _end(self):
        message = "success"
        if self.count == 0:
            message = "no results"
        elif self.result == 2:
            message = "too many results, data truncated"
        return f'], "result": {self.result}, "message": {dumps(message)} }}'.encode('utf-8')


class ClassicTreePrinter(ClassicPrinter):
    """
    a printer class writing a tree by the given grouping criteria as the first element in the epidata array
    """

    group: str
    _tree: Dict[str, List[Dict]] = dict()

    def __init__(self, group: str, max_results = MAX_RESULTS):
        super(ClassicTreePrinter, self).__init__(max_results)
        self.group = group

    def _begin(self):
        self._tree = dict()
        return super(ClassicTreePrinter, self)._begin()

    def _format_row(self, first: bool, row: Dict):
        group = row.get(self.group, "")
        del row[self.group]
        if group in self._tree:
            self._tree[group].append(row)
        else:
            self._tree[group] = [row]
        return None

    def _end(self):
        tree = orjson.dumps(self._tree)
        self._tree = dict()
        r = super(ClassicTreePrinter, self)._end()
        return tree + r


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

    def _error(self, error: Exception) -> str:
        # send an generic error
        return f"unknown error occurred:\n{error}"

    def _format_row(self, first: bool, row: Dict):
        if first:
            self._writer = DictWriter(
                self._stream, list(row.keys()), lineterminator="\n"
            )
            self._writer.writeheader()
        self._writer.writerow(row)

        # remove the stream content to print just one line at a time
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
        return b"["

    def _format_row(self, first: bool, row: Dict):
        sep = b"," if not first else b""
        return sep + orjson.dumps(row)

    def _end(self):
        return b"]"


class JSONLPrinter(APrinter):
    """
    a printer class writing in JSONLines format
    """

    def make_response(self, gen):
        return Response(gen, mimetype=" text/plain; charset=utf8")

    def _format_row(self, first: bool, row: Dict):
        # each line is a JSON file with a new line to separate them
        return orjson.dumps(row, option=orjson.OPT_APPEND_NEWLINE)


def create_printer(max_results = MAX_RESULTS) -> APrinter:
    format: str = request.values.get("format", "classic")
    if format == "tree":
        return ClassicTreePrinter("signal", max_results)
    if format.startswith("tree-"):
        # support tree format by any property following the dash
        return ClassicTreePrinter(format[len("tree-") :], max_results)
    if format == "json":
        return JSONPrinter(max_results)
    if format == "csv":
        return CSVPrinter(max_results)
    if format == "jsonl":
        return JSONLPrinter(max_results)
    return ClassicPrinter(max_results)
