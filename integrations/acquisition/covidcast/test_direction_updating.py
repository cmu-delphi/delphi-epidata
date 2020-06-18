"""Integration tests for covidcast's direction updating."""

# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
import delphi.operations.secrets as secrets

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covidcast.direction_updater'


class DirectionUpdatingTests(unittest.TestCase):
  """Tests covidcast direction updating."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the `covidcast` table
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table covidcast')
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def test_uploading(self):
    """Update rows having a stale `direction` field and serve the results."""

    # insert some sample data
    # CA 20200301:
    #   timeline should be x=[-2, -1, 0], y=[2, 6, 5] with direction=1
    # FL 20200517:
    #   timeline should be x=[-6, -5, 0], y=[1, 1, 2] with direction=0
    # TX 20200617:
    #   secondary timestamp indicates that direction (which is intentionally
    #   wrong) is fresh
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'state', 20200228, 'ca',
          123, 2, 0, 0, 0, NULL, 20200228, 0),
        (0, 'src', 'sig', 'day', 'state', 20200229, 'ca',
          123, 6, 0, 0, 0, NULL, 20200229, 0),
        (0, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5, 0, 0, 0, NULL, 20200301, 0),
        (0, 'src', 'sig', 'day', 'state', 20200511, 'fl',
          123, 1, 0, 0, 0, NULL, 20200511, 0),
        (0, 'src', 'sig', 'day', 'state', 20200512, 'fl',
          123, 2, 0, 0, 0, NULL, 20200512, 0),
        (0, 'src', 'sig', 'day', 'state', 20200517, 'fl',
          123, 2, 0, 0, 0, NULL, 20200517, 0),
        (0, 'src', 'sig', 'day', 'state', 20200615, 'tx',
          123, 9, 0, 0, 456, NULL, 20200615, 0),
        (0, 'src', 'sig', 'day', 'state', 20200616, 'tx',
          123, 5, 0, 0, 456, NULL, 20200616, 0),
        (0, 'src', 'sig', 'day', 'state', 20200617, 'tx',
          123, 1, 0, 0, 456, 1, 20200617, 0)
    ''')
    self.cnx.commit()

    # update direction (only 20200417 has enough history)
    args = None
    main(args)

    # request data from the API
    response = Epidata.covidcast(
        'src', 'sig', 'day', 'state', '20200101-20201231', '*')

    # verify data matches the CSV
    self.assertEqual(response, {
      'result': 1,
      'epidata': [
        {
          'time_value': 20200228,
          'geo_value': 'ca',
          'value': 2,
          'stderr': 0,
          'sample_size': 0,
          'direction': None,
          'issue': 20200228,
          'lag': 0
        },
        {
          'time_value': 20200229,
          'geo_value': 'ca',
          'value': 6,
          'stderr': 0,
          'sample_size': 0,
          'direction': None,
          'issue': 20200229,
          'lag': 0
        },
        {
          'time_value': 20200301,
          'geo_value': 'ca',
          'value': 5,
          'stderr': 0,
          'sample_size': 0,
          'direction': 1,
          'issue': 20200301,
          'lag': 0
        },
        {
          'time_value': 20200511,
          'geo_value': 'fl',
          'value': 1,
          'stderr': 0,
          'sample_size': 0,
          'direction': None,
          'issue': 20200511,
          'lag': 0
        },
        {
          'time_value': 20200512,
          'geo_value': 'fl',
          'value': 2,
          'stderr': 0,
          'sample_size': 0,
          'direction': None,
          'issue': 20200512,
          'lag': 0
        },
        {
          'time_value': 20200517,
          'geo_value': 'fl',
          'value': 2,
          'stderr': 0,
          'sample_size': 0,
          'direction': 0,
          'issue': 20200517,
          'lag': 0
        },
        {
          'time_value': 20200615,
          'geo_value': 'tx',
          'value': 9,
          'stderr': 0,
          'sample_size': 0,
          'direction': None,
          'issue': 20200615,
          'lag': 0
        },
        {
          'time_value': 20200616,
          'geo_value': 'tx',
          'value': 5,
          'stderr': 0,
          'sample_size': 0,
          'direction': None,
          'issue': 20200616,
          'lag': 0
        },
        {
          'time_value': 20200617,
          'geo_value': 'tx',
          'value': 1,
          'stderr': 0,
          'sample_size': 0,
          'direction': 1,
          'issue': 20200617,
          'lag': 0
        },
       ],
      'message': 'success',
    })

    # verify secondary timestamps were updated
    self.cur.execute('select timestamp2 from covidcast order by id asc')
    timestamps = [t for (t,) in self.cur]
    for t in timestamps[:6]:
      # first 6 rows had `direction` updated
      self.assertGreater(t, 0)
    for t in timestamps[6:]:
      # last 3 rows were not updated
      self.assertEqual(t, 456)
