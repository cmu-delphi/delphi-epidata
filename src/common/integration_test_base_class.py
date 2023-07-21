# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class BasicIntegrationTest(unittest.TestCase):
    """Basic integration test class"""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.delete_from_tables_list = []
        self.truncate_tables_list = []
        self.create_tables_list = []
        self.role_name = None
        self.epidata = Epidata
        self.epidata.BASE_URL = "http://delphi_web_epidata/epidata/api.php"
        self.epidata.auth = ("epidata", "key")

    def delete_from_table(self, cur, table_name: str) -> None:
        cur.execute(f"DELETE FROM `{table_name}`")

    def truncate_table(self, cur, table_name: str) -> None:
        cur.execute(f"TRUNCATE TABLE `{table_name}`")

    def create_table(self, cur, create_table_stmt: str):
        cur.execute(create_table_stmt)

    def create_key_with_role(self, cur, role_name: str):
        cur.execute("TRUNCATE TABLE `user_role`")
        cur.execute("TRUNCATE TABLE `user_role_link`")
        cur.execute(f'INSERT INTO `api_user`(`api_key`, `email`) VALUES("{role_name}_key", "{role_name}_email")')
        cur.execute(f'INSERT INTO `user_role`(`name`) VALUES("{role_name}")')
        cur.execute(
            f'INSERT INTO `user_role_link`(`user_id`, `role_id`) SELECT `api_user`.`id`, 1 FROM `api_user` WHERE `api_key`="{role_name}_key"'
        )

    def setUp(self) -> None:
        """Perform per-test setup."""

        # connect to the `epidata` database
        cnx = mysql.connector.connect(user="user", password="pass", host="delphi_database_epidata", database="epidata")
        cur = cnx.cursor()

        cur.execute("DELETE FROM `api_user`")
        cur.execute('INSERT INTO `api_user`(`api_key`, `email`) VALUES ("key", "email")')

        for stmt in self.create_tables_list:
            self.create_table(cur, stmt)

        for table_name in self.delete_from_tables_list:
            self.delete_from_table(cur, table_name)

        for table_name in self.truncate_tables_list:
            self.truncate_table(cur, table_name)

        if self.role_name:
            self.create_key_with_role(cur, self.role_name)

        cnx.commit()
        cur.close()

        self.cnx = cnx
        self.cur = cnx.cursor()

    @staticmethod
    def _clear_limits() -> None:
        limiter.storage.reset()

    def tearDown(self) -> None:
        """Perform per-test teardown."""
        self.cur.close()
        self.cnx.close()
        self._clear_limits()
