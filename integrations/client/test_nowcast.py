"""Integration tests for delphi_epidata.py."""

# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
import delphi.operations.secrets as secrets

# py3tester coverage target
__test_target__ = "delphi.epidata.client.delphi_epidata"


class DelphiEpidataPythonClientNowcastTests(unittest.TestCase):
    """Tests the Python client."""

    def setUp(self):
        """Perform per-test setup."""

        # connect to the `epidata` database and clear relevant tables
        cnx = mysql.connector.connect(user="user", password="pass", host="delphi_database_epidata", database="epidata")
        cur = cnx.cursor()

        cur.execute("truncate table covidcast_nowcast")
        cur.execute("delete from api_user")
        cur.execute('insert into api_user(api_key, tracking, registered) values ("key", 1, 1)')

        cnx.commit()
        cur.close()

        # make connection and cursor available to test cases
        self.cnx = cnx
        self.cur = cnx.cursor()

        # use the local instance of the Epidata API
        # Default value for BASE_URL is "https://delphi.cmu.edu/epidata/api.php" and None for auth
        Epidata.BASE_URL = "http://delphi_web_epidata/epidata/api.php"
        Epidata.auth = ("epidata", "key")

        # use the local instance of the epidata database
        secrets.db.host = "delphi_database_epidata"
        secrets.db.epi = ("user", "pass")

    def tearDown(self):
        """Perform per-test teardown."""
        self.cur.close()
        self.cnx.close()

    def test_covidcast_nowcast(self):
        """Test that the covidcast_nowcast endpoint returns expected data."""

        # insert dummy data
        self.cur.execute(
            """insert into covidcast_nowcast values
      (0, 'src', 'sig1', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 3.5, 20200101, 2),
      (0, 'src', 'sig2', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 2.5, 20200101, 2),
      (0, 'src', 'sig1', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 1.5, 20200102, 2)"""
        )
        self.cnx.commit()

        # fetch data
        response = Epidata.covidcast_nowcast("src", ["sig1", "sig2"], "sensor", "day", "county", 20200101, "01001")

        # request two signals
        self.assertEqual(
            response,
            {
                "result": 1,
                "epidata": [
                    {
                        "time_value": 20200101,
                        "geo_value": "01001",
                        "value": 1.5,
                        "issue": 20200102,
                        "lag": 2,
                        "signal": "sig1",
                    },
                    {
                        "time_value": 20200101,
                        "geo_value": "01001",
                        "value": 2.5,
                        "issue": 20200101,
                        "lag": 2,
                        "signal": "sig2",
                    },
                ],
                "message": "success",
            },
        )

        # request range of issues
        response = Epidata.covidcast_nowcast(
            "src", "sig1", "sensor", "day", "county", 20200101, "01001", issues=Epidata.range(20200101, 20200102)
        )

        self.assertEqual(
            response,
            {
                "result": 1,
                "epidata": [
                    {
                        "time_value": 20200101,
                        "geo_value": "01001",
                        "value": 3.5,
                        "issue": 20200101,
                        "lag": 2,
                        "signal": "sig1",
                    },
                    {
                        "time_value": 20200101,
                        "geo_value": "01001",
                        "value": 1.5,
                        "issue": 20200102,
                        "lag": 2,
                        "signal": "sig1",
                    },
                ],
                "message": "success",
            },
        )

        # request as_of
        response = Epidata.covidcast_nowcast(
            "src", "sig1", "sensor", "day", "county", 20200101, "01001", as_of=20200101
        )

        self.assertEqual(
            response,
            {
                "result": 1,
                "epidata": [
                    {
                        "time_value": 20200101,
                        "geo_value": "01001",
                        "value": 3.5,
                        "issue": 20200101,
                        "lag": 2,
                        "signal": "sig1",
                    }
                ],
                "message": "success",
            },
        )

        # request unavailable data
        response = Epidata.covidcast_nowcast("src", "sig1", "sensor", "day", "county", 22222222, "01001")

        self.assertEqual(response, {"result": -2, "message": "no results"})
