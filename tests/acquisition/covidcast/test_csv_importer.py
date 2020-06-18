"""Unit tests for csv_importer.py."""

# standard library
import unittest
from unittest.mock import MagicMock

# third party
import pandas

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covidcast.csv_importer'


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def test_is_sane_day(self):
    """Sanity check some dates."""

    self.assertTrue(CsvImporter.is_sane_day(20200418))

    self.assertFalse(CsvImporter.is_sane_day(22222222))
    self.assertFalse(CsvImporter.is_sane_day(20200001))
    self.assertFalse(CsvImporter.is_sane_day(20200199))
    self.assertFalse(CsvImporter.is_sane_day(202015))

  def test_is_sane_week(self):
    """Sanity check some weeks."""

    self.assertTrue(CsvImporter.is_sane_week(202015))

    self.assertFalse(CsvImporter.is_sane_week(222222))
    self.assertFalse(CsvImporter.is_sane_week(202000))
    self.assertFalse(CsvImporter.is_sane_week(202054))
    self.assertFalse(CsvImporter.is_sane_week(20200418))

  def test_find_csv_files(self):
    """Recursively explore and find CSV files."""

    path_prefix = 'prefix/to/the/data/'
    glob_paths = [
      # valid weekly
      path_prefix + 'fb_survey/weekly_202015_county_cli.csv',
      # valid daily
      path_prefix + 'ght/20200408_state_rawsearch.csv',
      # invalid
      path_prefix + 'invalid/hello_world.csv',
      # invalid day
      path_prefix + 'invalid/22222222_b_c.csv',
      # invalid week
      path_prefix + 'invalid/weekly_222222_b_c.csv',
      # invalid geography
      path_prefix + 'invalid/20200418_country_c.csv',
      # ignored
      path_prefix + 'ignored/README.md',
    ]
    mock_glob = MagicMock()
    mock_glob.glob.return_value = glob_paths

    found = list(CsvImporter.find_csv_files(path_prefix, glob=mock_glob))

    expected_issue_day=int(date.today().strftime("%Y%m%d"))
    expected_issue_week=int(str(epi.Week.fromdate(date.today())))
    time_value_day = 20200408
    expected = [
      (glob_paths[0], ('fb_survey', 'cli', 'week', 'county', 202015, expected_issue_week, delta_epiweeks(202015, expected_issue_week))),
      (glob_paths[1], ('ght', 'rawsearch', 'day', 'state', time_value_day, expected_issue_day, (date.today() - date(year=time_value_day // 10000, month=(time_value_day // 100) % 100, day=time_value_day % 100)).days)),
      (glob_paths[2], None),
      (glob_paths[3], None),
      (glob_paths[4], None),
      (glob_paths[5], None),
    ]
    self.assertEqual(found, expected)

  def test_is_header_valid_allows_extra_columns(self):
    """Allow and ignore extra columns in the header."""

    columns = CsvImporter.REQUIRED_COLUMNS

    self.assertTrue(CsvImporter.is_header_valid(columns))
    self.assertTrue(CsvImporter.is_header_valid(columns | {'foo', 'bar'}))

  def test_is_header_valid_does_not_depend_on_column_order(self):
    """Allow columns to appear in any order."""

    # sorting changes the order of the columns
    columns = sorted(CsvImporter.REQUIRED_COLUMNS)

    self.assertTrue(CsvImporter.is_header_valid(columns))

  def test_floaty_int(self):
    """Parse ints that may look like floats."""

    self.assertEqual(CsvImporter.floaty_int('-1'), -1)
    self.assertEqual(CsvImporter.floaty_int('-1.0'), -1)

    with self.assertRaises(ValueError):
      CsvImporter.floaty_int('-1.1')

  def test_maybe_apply(self):
    """Apply a function to a value as long as it's not null-like."""

    self.assertEqual(CsvImporter.maybe_apply(float, '3.14'), 3.14)
    self.assertEqual(CsvImporter.maybe_apply(int, '1'), 1)
    self.assertIsNone(CsvImporter.maybe_apply(int, 'NA'))
    self.assertIsNone(CsvImporter.maybe_apply(int, 'NaN'))
    self.assertIsNone(CsvImporter.maybe_apply(float, ''))
    self.assertIsNone(CsvImporter.maybe_apply(float, None))

  def test_extract_and_check_row(self):
    """Apply various sanity checks to a row of data."""

    def make_row(
        geo_type='state',
        geo_id='vi',
        val='1.23',
        se='4.56',
        sample_size='100.5'):
      row = MagicMock(
          geo_id=geo_id,
          val=val,
          se=se,
          sample_size=sample_size)
      return geo_type, row

    # cases to test each failure mode
    failure_cases = [
      (make_row(geo_type='county', geo_id='1234'), 'geo_id'),
      (make_row(geo_type='county', geo_id='00000'), 'geo_id'),
      (make_row(geo_type='hrr', geo_id='600'), 'geo_id'),
      (make_row(geo_type='msa', geo_id='1234'), 'geo_id'),
      (make_row(geo_type='msa', geo_id='01234'), 'geo_id'),
      (make_row(geo_type='dma', geo_id='400'), 'geo_id'),
      (make_row(geo_type='state', geo_id='48'), 'geo_id'),
      (make_row(geo_type='state', geo_id='iowa'), 'geo_id'),
      (make_row(geo_type='country', geo_id='usa'), 'geo_type'),
      (make_row(se='-1'), 'se'),
      (make_row(sample_size='3'), 'sample_size'),
      (make_row(geo_type=None), 'geo_type'),
      (make_row(geo_id=None), 'geo_id'),
      (make_row(val=None), 'val'),
      (make_row(val='nan'), 'val'),
      (make_row(val='NaN'), 'val'),
      (make_row(geo_type='hrr', geo_id='hrr001'), 'geo_id'),
      (make_row(val='val'), 'val'),
      (make_row(se='se'), 'se'),
      (make_row(sample_size='sample_size'), 'sample_size'),
    ]

    for ((geo_type, row), field) in failure_cases:
      values, error = CsvImporter.extract_and_check_row(row, geo_type)
      self.assertIsNone(values)
      self.assertEqual(error, field)

    # a nominal case without missing values
    geo_type, row = make_row()
    values, error = CsvImporter.extract_and_check_row(row, geo_type)

    self.assertIsInstance(values, CsvImporter.RowValues)
    self.assertEqual(str(values.geo_value), row.geo_id)
    self.assertEqual(str(values.value), row.val)
    self.assertEqual(str(values.stderr), row.se)
    self.assertEqual(str(values.sample_size), row.sample_size)
    self.assertIsNone(error)

    # a nominal case with missing values
    geo_type, row = make_row(se='', sample_size='NA')
    values, error = CsvImporter.extract_and_check_row(row, geo_type)

    self.assertIsInstance(values, CsvImporter.RowValues)
    self.assertEqual(str(values.geo_value), row.geo_id)
    self.assertEqual(str(values.value), row.val)
    self.assertIsNone(values.stderr)
    self.assertIsNone(values.sample_size)
    self.assertIsNone(error)

  def test_load_csv_with_invalid_header(self):
    """Bail loading a CSV when the header is invalid."""

    data = {'foo': [1, 2, 3]}
    mock_pandas = MagicMock()
    mock_pandas.read_csv.return_value = pandas.DataFrame(data=data)
    filepath = 'path/name.csv'
    geo_type = 'state'

    rows = list(CsvImporter.load_csv(filepath, geo_type, pandas=mock_pandas))

    self.assertTrue(mock_pandas.read_csv.called)
    self.assertTrue(mock_pandas.read_csv.call_args[0][0], filepath)
    self.assertEqual(rows, [None])

  def test_load_csv_with_valid_header(self):
    """Yield sanity checked `RowValues` from a valid CSV file."""

    # one invalid geo_id, but otherwise valid
    data = {
      'geo_id': ['ca', 'tx', 'fl', '123'],
      'val': ['1.1', '1.2', '1.3', '1.4'],
      'se': ['2.1', '2.2', '2.3', '2.4'],
      'sample_size': ['301', '302', '303', '304'],
    }
    mock_pandas = MagicMock()
    mock_pandas.read_csv.return_value = pandas.DataFrame(data=data)
    filepath = 'path/name.csv'
    geo_type = 'state'

    rows = list(CsvImporter.load_csv(filepath, geo_type, pandas=mock_pandas))

    self.assertTrue(mock_pandas.read_csv.called)
    self.assertTrue(mock_pandas.read_csv.call_args[0][0], filepath)
    self.assertEqual(len(rows), 4)

    self.assertEqual(rows[0].geo_value, 'ca')
    self.assertEqual(rows[0].value, 1.1)
    self.assertEqual(rows[0].stderr, 2.1)
    self.assertEqual(rows[0].sample_size, 301)

    self.assertEqual(rows[1].geo_value, 'tx')
    self.assertEqual(rows[1].value, 1.2)
    self.assertEqual(rows[1].stderr, 2.2)
    self.assertEqual(rows[1].sample_size, 302)

    self.assertEqual(rows[2].geo_value, 'fl')
    self.assertEqual(rows[2].value, 1.3)
    self.assertEqual(rows[2].stderr, 2.3)
    self.assertEqual(rows[2].sample_size, 303)

    self.assertIsNone(rows[3])
