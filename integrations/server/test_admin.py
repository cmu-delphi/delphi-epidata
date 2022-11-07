"""Integration tests for the `admin` endpoint."""

# standard library
import unittest
import os

# third party
import mysql.connector as db_connector
import requests

# first party
from delphi.epidata.server._security import _find_user
from delphi.epidata.server.admin import validate_email


BASE_URL = "http://delphi_web_epidata:5000/epidata/admin"
ADMIN_PASSWORD = 'abc'


class AdminEndpointTests(unittest.TestCase):
    """Tests the `admin` endpoint."""

    def setUp(self) -> None:
        cnx = db_connector.connect(
            user='user',
            password='pass',
            host='delphi_database_epidata',
            database='epidata'
        )
        cur = cnx.cursor()

        cur.execute("truncate table api_user")
        cnx.commit()
        cur.close()

        self.cnx = cnx
        self.cur = cnx.cursor()

        self.user_email: str = 'johndoe@andrew.cmu.edu'
        self.user_api_key: str = '1bca83d7-56cc-45c6-9ee8-d2b1b5af8801'

    def tearDown(self) -> None:
        self.cur.close()
        self.cnx.close()

    def test_admin_enabled(self):
        params = {'auth': ADMIN_PASSWORD}
        response = requests.get(BASE_URL, params=params)
        self.assertEqual(response.status_code, 200)

    def test_validate_email_valid(self):
        is_valid = validate_email(self.user_email)
        self.assertEqual(is_valid, True)

    def test_validate_email_invalid(self):
        email = "test@test"
        is_valid = validate_email(email)
        self.assertEqual(is_valid, False)

    def test_add_user(self):
        payload = {
            'auth': ADMIN_PASSWORD,
            'email': self.user_email,
            'api_key': self.user_api_key,

        }
        _ = requests.post(BASE_URL, params=payload)
        user = _find_user(payload['api_key'])
        self.assertEqual(user.api_key, payload['api_key'])

    # def test_update_user(self):
    #     user = _find_user(self.user_api_key)
    #     url = os.path.join(BASE_URL, str(user.id))
    #     payload = {
    #         'email': "doejohn@andrew.cmu.edu",
    #     }
    #     _ = requests.put(url, params=payload)
    #     self.assertEqual(user.email, payload['email'])


    # def test_delete_user(self):
    #     payload = {
    #         'auth': ADMIN_PASSWORD,
    #         'api_key' : self.user_api_key

    #     }

    
