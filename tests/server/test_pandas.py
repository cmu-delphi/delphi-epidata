"""Unit tests for pandas helper."""

# standard library
import unittest
from mock import patch, sentinel, ANY

# first party
from delphi.epidata.server.main import app
from delphi.epidata.server._pandas import as_pandas
from delphi.epidata.server._config import MAX_RESULTS

# py3tester coverage target
__test_target__ = "delphi.epidata.server._pandas"


class TestPandas(unittest.TestCase):
    """Basic unit tests."""

    def setUp(self):
        """Perform per-test setup."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False

    @patch("delphi.epidata.server._pandas.text")
    @patch("pandas.read_sql_query")
    def test_as_pandas(self, mock_read_sql_query, mock_sqlalch_text):
        with app.test_request_context('/correlation'):

            mock_sqlalch_text.return_value = sentinel.default_limit
            as_pandas("", params=None, db_engine=None)
            mock_read_sql_query.assert_called()
            mock_sqlalch_text.assert_called_with(f" LIMIT {MAX_RESULTS+1}")
            mock_read_sql_query.assert_called_with(sentinel.default_limit, ANY, params=ANY, parse_dates=ANY)

            mock_sqlalch_text.return_value = sentinel.explicit_limit
            as_pandas("", params=None, db_engine=None, limit_rows=5)
            mock_sqlalch_text.assert_called_with(f" LIMIT {5}")
            mock_read_sql_query.assert_called_with(sentinel.explicit_limit, ANY, params=ANY, parse_dates=ANY)
