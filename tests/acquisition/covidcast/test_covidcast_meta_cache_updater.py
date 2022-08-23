"""Unit tests for covidcast_meta_cache_updater.py."""

# standard library
import argparse

import unittest
from unittest.mock import MagicMock

# third party

from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import get_argument_parser, main
from delphi.epidata.acquisition.covidcast.database_meta import DatabaseMeta


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    def setUp(self):
        """Perform per-test setup."""

        # connect to the `epidata` database
        self.db = DatabaseMeta(base_url="http://delphi_web_epidata/epidata")
        self.db.connect(user="user", password="pass", host="delphi_database_epidata")

        # TODO: Switch when delphi_epidata client is released.
        self.db.delphi_epidata = False

        # clear all tables
        self.db._cursor.execute("truncate table signal_load")
        self.db._cursor.execute("truncate table signal_history")
        self.db._cursor.execute("truncate table signal_latest")
        self.db._cursor.execute("truncate table geo_dim")
        self.db._cursor.execute("truncate table signal_dim")
        self.db.commit()

    def tearDown(self):
        """Perform per-test teardown."""
        self.db.disconnect(None)

    def test_get_argument_parser(self):
        """Return a parser for command-line arguments."""
        self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)

    def test_main_successful(self):
        """Run the main program successfully."""

        api_response = {
            "result": 1,
            "message": "yes",
            "epidata": [{"foo": "bar"}],
        }

        args = MagicMock(log_file="log")
        mock_epidata_impl = MagicMock()
        mock_epidata_impl.covidcast_meta.return_value = api_response
        mock_database = MagicMock()
        mock_database.compute_covidcast_meta.return_value = api_response["epidata"]
        fake_database_impl = lambda: mock_database

        main(args, epidata_impl=mock_epidata_impl, database_impl=fake_database_impl)

        self.assertTrue(mock_database.connect.called)

        self.assertTrue(mock_database.update_covidcast_meta_cache.called)
        actual_args = mock_database.update_covidcast_meta_cache.call_args[0]
        expected_args = (api_response["epidata"],)
        self.assertEqual(actual_args, expected_args)

        self.assertTrue(mock_database.disconnect.called)
        self.assertTrue(mock_database.disconnect.call_args[0][0])

    def test_main_failure(self):
        """Run the main program with a query failure."""
        api_response = {
            "result": -123,
            "message": "no",
        }

        args = MagicMock(log_file="log")
        mock_database = MagicMock()
        mock_database.compute_covidcast_meta.return_value = list()
        fake_database_impl = lambda: mock_database

        main(args, epidata_impl=None, database_impl=fake_database_impl)

        self.assertTrue(mock_database.compute_covidcast_meta.called)
