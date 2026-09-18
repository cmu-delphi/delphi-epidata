"""Regression tests for #1801: raw database/exception details must not leak to clients.

Internal details (SQL text, driver messages, internal hostnames) are logged
server-side only. Client-facing response bodies carry generic messages.
"""

# standard library
import json
import unittest
from unittest.mock import MagicMock, patch

from delphi.epidata.server._common import app
from delphi.epidata.server._exceptions import DatabaseErrorException
from delphi.epidata.server._printer import APrinter, CSVPrinter, JSONPrinter

# py3tester coverage target
__test_target__ = "delphi.epidata.server._exceptions"

SQL_ERROR_TEXT = (
    "(sqlite3.OperationalError) no such column: nonexistent_col\n"
    "[SQL: SELECT source, signal FROM epimetric_latest_v WHERE nonexistent_col = 1]"
)

HOSTNAME_ERROR_TEXT = (
    "(pymysql.err.OperationalError) (2003, \"Can't connect to MySQL server on "
    "'db-internal.corp:3306' (super_secret_password)\")"
)

# fragments that must never appear in a client-visible response body
SENSITIVE_FRAGMENTS = [
    "sqlite3.OperationalError",
    "pymysql.err.OperationalError",
    "no such column: nonexistent_col",
    "SELECT source, signal FROM epimetric_latest_v",
    "db-internal.corp",
    "Can't connect to MySQL server",
    "super_secret_password",
]


def assert_body_is_masked(test_case, body: str):
    for fragment in SENSITIVE_FRAGMENTS:
        test_case.assertNotIn(fragment, body, f"leaked fragment: {fragment!r}")


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False

    def test_database_error_exception_body_is_generic(self):
        with app.test_request_context("/?format=json"):
            exc = DatabaseErrorException(SQL_ERROR_TEXT)
            body = exc.response.get_data(as_text=True)
            payload = json.loads(body)
            self.assertEqual(payload["result"], -1)
            self.assertEqual(payload["message"], "database error")
            self.assertEqual(payload["epidata"], [])
            assert_body_is_masked(self, body)

    def test_database_error_details_logged_server_side(self):
        with app.test_request_context("/?format=json"):
            with patch(
                "delphi.epidata.server._exceptions.get_structured_logger"
            ) as get_logger:
                logger = MagicMock()
                get_logger.return_value = logger
                DatabaseErrorException(SQL_ERROR_TEXT)
                get_logger.assert_called_with("server_error")
                logged = str(logger.error.call_args)
                self.assertIn("no such column", logged)

    def test_execute_queries_masks_driver_error(self):
        with app.test_request_context("/?format=json"):
            with patch(
                "delphi.epidata.server._query.run_query",
                side_effect=Exception(SQL_ERROR_TEXT),
            ), patch(
                "delphi.epidata.server._query.get_structured_logger"
            ) as get_logger:
                logger = MagicMock()
                get_logger.return_value = logger
                from delphi.epidata.server._query import execute_queries

                with self.assertRaises(DatabaseErrorException) as ctx:
                    execute_queries([("SELECT 1", {})], [], [], [])
                body = ctx.exception.response.get_data(as_text=True)
                assert_body_is_masked(self, body)
                # the driver error was logged server-side only
                get_logger.assert_called_with("server_error")
                logged = str(logger.error.call_args)
                self.assertIn("no such column", logged)

    def test_json_printer_error_is_generic(self):
        with app.test_request_context("/?format=json"):
            printer = JSONPrinter()
            self.assertIsInstance(printer, APrinter)
            out = printer._error(Exception(HOSTNAME_ERROR_TEXT))
            payload = json.loads(out)
            self.assertEqual(payload["result"], -1)
            self.assertEqual(payload["message"], "unknown error occurred")
            self.assertEqual(payload["error"], "unknown error occurred")
            self.assertEqual(payload["epidata"], [])
            assert_body_is_masked(self, out)

    def test_csv_printer_error_is_generic(self):
        with app.test_request_context("/?format=csv"):
            out = CSVPrinter()._error(Exception(HOSTNAME_ERROR_TEXT))
            self.assertEqual(out, "unknown error occurred")
            assert_body_is_masked(self, out)

    def test_http_status_contract_unchanged(self):
        # classic/tree formats still mask the failure as HTTP 200 with result -1;
        # changing that contract is an open question for the maintainers (#1801).
        with app.test_request_context("/"):
            exc = DatabaseErrorException(SQL_ERROR_TEXT)
            self.assertEqual(exc.code, 200)
            self.assertEqual(exc.response.status_code, 200)
            self.assertEqual(json.loads(exc.response.get_data(as_text=True))["result"], -1)
        with app.test_request_context("/?format=json"):
            exc = DatabaseErrorException(SQL_ERROR_TEXT)
            self.assertEqual(exc.code, 500)
            self.assertEqual(exc.response.status_code, 500)
