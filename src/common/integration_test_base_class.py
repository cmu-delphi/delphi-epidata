# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class DelphiTestBase(unittest.TestCase):
    """Basic integration test class"""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.delete_from_tables_list = []
        self.truncate_tables_list = []
        self.create_tables_list = []
        self.role_name = None
        self.epidata_client = Epidata
        self.epidata_client.BASE_URL = "http://delphi_web_epidata/epidata"
        self.epidata_client.auth = ("epidata", "key")

    def create_key_with_role(self, cur, role_name: str):
        cur.execute(f'INSERT INTO `api_user`(`api_key`, `email`) VALUES("{role_name}_key", "{role_name}_email")')
        cur.execute(f'INSERT INTO `user_role`(`name`) VALUES("{role_name}")')
        cur.execute(
            f'INSERT INTO `user_role_link`(`user_id`, `role_id`) SELECT `api_user`.`id`, `user_role`.`id` FROM `api_user` JOIN `user_role` WHERE `api_user`.`api_key`="{role_name}_key" AND `user_role`.`name`="{role_name}"'
        )

    def setUp(self) -> None:
        """Perform per-test setup."""

        # connect to the `epidata` database
        cnx = mysql.connector.connect(user="user", password="pass", host="delphi_database_epidata", database="epidata")
        cur = cnx.cursor()

        cur.execute("DELETE FROM `api_user`")
        cur.execute("TRUNCATE TABLE `user_role`")
        cur.execute("TRUNCATE TABLE `user_role_link`")
        cur.execute('INSERT INTO `api_user`(`api_key`, `email`) VALUES ("key", "email")')

        self.localSetUp()

        for stmt in self.create_tables_list:
            cur.execute(stmt)

        for table_name in self.delete_from_tables_list:
            cur.execute(f"DELETE FROM `{table_name}`")

        for table_name in self.truncate_tables_list:
            cur.execute(f"TRUNCATE TABLE `{table_name}`")

        if self.role_name:
            self.create_key_with_role(cur, self.role_name)

        cnx.commit()
        cur.close()

        self.cnx = cnx
        self.cur = cnx.cursor()

    def localSetUp(self):
        # stub; override in subclasses to perform custom setup.
        # runs after user/api_key tables have been truncated, but before test-specific tables are created/deleted/truncated and before database changes have been committed
        pass

    @staticmethod
    def _clear_limits() -> None:
        limiter.storage.reset()

    def tearDown(self) -> None:
        """Perform per-test teardown."""
        self.cur.close()
        self.cnx.close()
        self._clear_limits()
