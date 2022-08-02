import unittest
from unittest.mock import MagicMock

from ....src.acquisition.covidcast.database_meta import DatabaseMeta

class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    def test_update_covidcast_meta_cache_query(self):
        """Query to update the metadata cache looks sensible.

        NOTE: Actual behavior is tested by integration test.
        """

        args = ('epidata_json_str',)
        mock_connector = MagicMock()
        database = DatabaseMeta()
        database.connect(connector_impl=mock_connector)

        database.update_covidcast_meta_cache(*args)

        connection = mock_connector.connect()
        cursor = connection.cursor()
        self.assertTrue(cursor.execute.called)

        sql, args = cursor.execute.call_args[0]
        expected_args = ('"epidata_json_str"',)
        self.assertEqual(args, expected_args)

        sql = sql.lower()
        self.assertIn('update', sql)
        self.assertIn('`covidcast_meta_cache`', sql)
        self.assertIn('timestamp', sql)
        self.assertIn('epidata', sql)
