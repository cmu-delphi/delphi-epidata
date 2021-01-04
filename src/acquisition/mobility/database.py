import sys
import pymysql
import delphi.operations.secrets as secrets


class Database:
    """Database connection class."""

    def __init__(self):

        user, password = secrets.db.epi
        self.host = secrets.db.host,
        self.username = user,
        self.password = password,
        self.port = '3306',
        self.dbname = 'epidata',
        self.conn = None

    def open_connection(self):
        """Connect to MySQL Database."""
        try:
            if self.conn is None:
                self.conn = pymysql.connect(
                    self.host,
                    user=self.username,
                    passwd=self.password,
                    db=self.dbname,
                    connect_timeout=10
                )
        except pymysql.MySQLError as e:
            print(e)
            sys.exit()

    def insert_apple_data(self, data):
        """Execute SQL query."""
        try:
            self.open_connection()
            with self.conn.cursor() as cur:
                cols = "`, `".join([str(i) for i in data.columns.tolist()])
                # Insert DataFrame records.
                for i, row in data.iterrows():
                    sql = "INSERT INTO `Apple_Mobility_US` (`" + cols + "`) VALUES (" + "%s," * (
                            len(row) - 1) + "%s) ON " \
                                            "DUPLICATE KEY UPDATE " \
                                            "`state` = %s," \
                                            "`county_and_city` = %s," \
                                            "`geo_type` = %s, `date` = " \
                                            "%s, " \
                                            "`driving` = %s, `transit` = " \
                                            "%s, " \
                                            "`walking` = %s "
                    sql_data = (
                    row['state'].lower(), row['county_and_city'].lower(), row['geo_type'].lower(), row['date'],
                    row['driving'],
                    row['transit'], row['walking'], row['state'].lower(), row['county_and_city'].lower(),
                    row['geo_type'].lower(),
                    row['date'], row['driving'], row['transit'], row['walking'])
                    # print(sql_data)
                    cur.execute(sql, sql_data)
            self.conn.commit()
            cur.close()
        except pymysql.MySQLError as e:
            print(e)
            sys.exit()
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None

    def insert_google_data(self, data):
        """Execute SQL query."""
        try:
            self.open_connection()
            with self.conn.cursor() as cur:
                cols = "`, `".join([str(i) for i in data.columns.tolist()])

                # Insert DataFrame records one by one.
                for i, row in data.iterrows():
                    sql = "INSERT INTO `Google_Mobility_US` (`" + cols + "`) VALUES (" + "%s," * (
                            len(row) - 1) + "%s) ON " \
                                            "DUPLICATE KEY UPDATE " \
                                            "`state` = %s," \
                                            " `county` = %s," \
                                            " `date` = %s"
                    sql_data = (
                        row['state'].lower(), row['county'].lower(), row['date'], row['retail and recreation'],
                        row['grocery and pharmacy'],
                        row['parks'], row['transit stations'], row['workplaces'], row['residential'],
                        row['state'].lower(),
                        row['county'].lower(), row['date'])
                    # print(sql_data)
                    cur.execute(sql, sql_data)
                self.conn.commit()
                cur.close()
        except pymysql.MySQLError as e:
            print(e)
            sys.exit()
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None
