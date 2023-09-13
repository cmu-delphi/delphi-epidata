import requests

# third party
import mysql.connector

# frirst party
from delphi.epidata.acquisition.covidcast.test_utils import (
    CovidcastBase,
    CovidcastTestRow,
)


class DifferentiatedAccessTests(CovidcastBase):
    def localSetUp(self):
        """Perform per-test setup"""
        self._db._cursor.execute(
            'update covidcast_meta_cache set timestamp = 0, epidata = "[]"'
        )

    def setUp(self):
        # connect to the `epidata` database

        super().setUp()

        self.maxDiff = None

        cnx = mysql.connector.connect(
            user="user",
            password="pass",
            host="delphi_database_epidata",
            database="epidata",
        )

        cur = cnx.cursor()

        cur.execute("DELETE FROM `api_user`")
        cur.execute("TRUNCATE TABLE `user_role`")
        cur.execute("TRUNCATE TABLE `user_role_link`")

        cur.execute(
            'INSERT INTO `api_user`(`api_key`, `email`) VALUES ("api_key", "api_key@gmail.com")'
        )
        cur.execute(
            'INSERT INTO `api_user`(`api_key`, `email`) VALUES("ny_key", "ny_key@gmail.com")'
        )
        cur.execute('INSERT INTO `user_role`(`name`) VALUES("state:ny")')
        cur.execute(
            'INSERT INTO `user_role_link`(`user_id`, `role_id`) SELECT `api_user`.`id`, 1 FROM `api_user` WHERE `api_key` = "ny_key"'
        )

        cnx.commit()
        cur.close()
        cnx.close()

    def request_based_on_row(self, row: CovidcastTestRow, **kwargs):
        params = self.params_from_row(row, endpoint="differentiated_access", **kwargs)
        # use local instance of the Epidata API

        response = requests.get(
            "http://delphi_web_epidata/epidata/api.php", params=params
        )
        response.raise_for_status()
        return response.json()

    def _insert_placeholder_restricted_geo(self):
        geo_values = ["36029", "36047", "36097", "36103", "36057", "36041", "36033"]
        rows = [
            CovidcastTestRow.make_default_row(
                source="restricted-source",
                geo_type="county",
                geo_value=geo_values[i],
                time_value=2000_01_01 + i,
                value=i * 1.0,
                stderr=i * 10.0,
                sample_size=i * 100.0,
                issue=2000_01_03,
                lag=2 - i,
            )
            for i in [1, 2, 3]
        ] + [
            # time value intended to overlap with the time values above, with disjoint geo values
            CovidcastTestRow.make_default_row(
                source="restricted-source",
                geo_type="county",
                geo_value=geo_values[i],
                time_value=2000_01_01 + i - 3,
                value=i * 1.0,
                stderr=i * 10.0,
                sample_size=i * 100.0,
                issue=2000_01_03,
                lag=5 - i,
            )
            for i in [4, 5, 6]
        ]
        self._insert_rows(rows)
        return rows

    def test_restricted_geo_ny_role(self):
        # insert placeholder data
        rows = self._insert_placeholder_restricted_geo()

        # make request
        response = self.request_based_on_row(rows[0], token="ny_key")
        expected = {
            "result": 1,
            "epidata": [rows[0].as_api_compatibility_row_dict()],
            "message": "success",
        }
        self.assertEqual(response, expected)

    def test_restricted_geo_default_role(self):
        # insert placeholder data
        rows = self._insert_placeholder_restricted_geo()

        # make request
        response = self.request_based_on_row(rows[0], token="api_key")
        expected = {"result": -2, "message": "no results"}
        self.assertEqual(response, expected)
