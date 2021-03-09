"""Unit tests for signal_dash_data_generator.py."""

# standard library
import argparse
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from datetime import date

# third party
import pandas as pd

# first party
from delphi.epidata.acquisition.covidcast.signal_dash_data_generator import get_argument_parser, \
    main, Database, DashboardSignalStatus, DashboardSignalCoverage, DashboardSignal, get_latest_issue_date_from_metadata, \
    get_coverage
from delphi.epidata.client.delphi_epidata import Epidata

# py3tester coverage target
__test_target__ = (
    'delphi.epidata.acquisition.covidcast.signal_dash_data_generator'
)


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    def test_get_argument_parser(self):
        """Return a parser for command-line arguments."""

        self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)

    def test_insert_status_successful(self):
        """Test status data inserted correctly."""
        mock_connector = MagicMock()
        database = Database(connector_impl=mock_connector)
        connection = mock_connector.connect()
        cursor = connection.cursor()

        status1 = DashboardSignalStatus(
            signal_id=1, date=date(
                2020, 1, 1), latest_issue_date=date(
                2020, 1, 2), latest_data_date=date(
                2020, 1, 3))
        status2 = DashboardSignalStatus(
            signal_id=2, date=date(
                2021, 1, 1), latest_issue_date=date(
                2021, 1, 2), latest_data_date=date(
                2021, 1, 3))
        database.write_status([status1, status2])

        tuples = cursor.executemany.call_args.args[1]
        expected_tuples = [
            (1, date(2020, 1, 1), date(2020, 1, 2), date(2020, 1, 3)),
            (2, date(2021, 1, 1), date(2021, 1, 2), date(2021, 1, 3))
        ]
        self.assertListEqual(tuples, expected_tuples)

    def test_insert_coverage_successful(self):
        """Test coverage data inserted correctly."""
        mock_connector = MagicMock()
        database = Database(connector_impl=mock_connector)
        connection = mock_connector.connect()
        cursor = connection.cursor()

        coverage1 = DashboardSignalCoverage(
            signal_id=1,
            date=date(2020, 1, 1),
            geo_type="state",
            geo_value="PA"
        )
        coverage2 = DashboardSignalCoverage(
            signal_id=2,
            date=date(2021, 2, 2),
            geo_type="state",
            geo_value="NJ"
        )

        database.write_coverage([coverage1, coverage2])

        tuples = cursor.executemany.call_args.args[1]
        expected_tuples = [
            (1, date(2020, 1, 1), "state", "PA"),
            (2, date(2021, 2, 2), "state", "NJ")
        ]
        self.assertListEqual(tuples, expected_tuples)

    def test_get_enabled_signals_successful(self):
        """Test signals retrieved correctly."""
        mock_connector = MagicMock()
        database = Database(connector_impl=mock_connector)
        connection = mock_connector.connect()
        cursor = connection.cursor()

        db_rows = [
            (1, "Change", "chng"),
            (2, "Quidel", "quidel"),
        ]
        cursor.fetchall.return_value = db_rows

        signals = database.get_enabled_signals()

        expected_signals = [
            DashboardSignal(db_id=1, name="Change", source="chng"),
            DashboardSignal(db_id=2, name="Quidel", source="quidel")
        ]

        self.assertListEqual(signals, expected_signals)

    def test_get_latest_issue_date_from_metadata(self):
        signal = DashboardSignal(db_id=1, name="Change", source="chng")
        data = [['chng', 20200101], ['chng', 20210101], ['quidel', 20220101]]
        metadata = pd.DataFrame(data, columns=['data_source', 'max_issue'])

        issue_date = get_latest_issue_date_from_metadata(signal, metadata)
        self.assertEqual(issue_date, date(2021, 1, 1))

    def test_get_latest_data_date_from_metadata(self):
        signal = DashboardSignal(db_id=1, name="Change", source="chng")
        data = [
            ['chng', pd.Timestamp("2020-01-01")],
            ['chng', pd.Timestamp("2021-01-01")],
            ['quidel', pd.Timestamp("20220101")]]
        metadata = pd.DataFrame(data, columns=['data_source', 'max_time'])

        data_date = get_latest_data_date_from_metadata(signal, metadata)
        self.assertEqual(data_date, date(2021, 1, 1))

    @patch('delphi.epidata.client.delphi_epidata.Epidata.covidcast')
    def test_get_coverage(self, mock_covidcast):
        signal = DashboardSignal(db_id=1, name="Change", source="chng")
        data = [['chng', pd.Timestamp("2020-01-01"), "chng_signal"]]
        metadata = pd.DataFrame(
            data,
            columns=[
                'data_source',
                'max_time',
                'signal'])

        epidata_data = [[pd.Timestamp("2020-01-01"), "state", "PA"]]
        epidata_df = pd.DataFrame(
            epidata_data,
            columns=[
                'time_value',
                'geo_type',
                'geo_value'])

        mock_covidcast.signal.return_value = epidata_df

        coverage = get_coverage(signal, metadata)

        expected_coverage = [
            DashboardSignalCoverage(
                signal_id=1,
                date=datetime.date(
                    2020,
                    1,
                    1),
                geo_type='state',
                geo_value='PA')]

        self.assertListEqual(coverage, expected_coverage)
