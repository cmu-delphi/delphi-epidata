from unittest import TestCase, mock
import pymysql
import delphi.operations.secrets as secrets


def query(sql, sql_data):

    user, password = secrets.db.epi
    connection = pymysql.connect(host=secrets.db.host, user=user, password=password,
                                 db='epidata', charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_data)
            results = cursor.fetchall()

    finally:
        connection.close()

    return results


class TestMobilityData(TestCase):

    @mock.patch('TestMobilityData.pymysql', autospec=True)
    def test_apple_mobility_data(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        test_data = [{'state': 'dummy', 'county_and_city': 'boone county', 'geo_type': 'county', 'date': '2020-11-03',
                      'driving': 57.129999999999995,
                      'transit': 0.0, 'walking': 0.0}]

        mock_cursor.fetchall.return_value = test_data
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        sql_del = "DELETE FROM `Apple_Mobility_US` (`state`, `county_and_city`, `geo_type`, `date`, `driving`, " \
                  "`transit`, `walking`) VALUES (%s,%s,%s,%s,%s,%s,%s) WHERE `state` = %s,`county_and_city` = %s," \
                  "`geo_type` = %s, `date` = %s, `driving` = %s, `transit` = %s, `walking` = %s "
        sql_del_data = "('dummy', 'boone county', 'county', '2020-11-03', 57.129999999999995, 0.0, 0.0, 'dummy', " \
                       "'boone county', 'county', '2020-11-03', 57.129999999999995, 0.0, 0.0) "

        query(sql_del, sql_del_data)

        sql = "INSERT INTO `Apple_Mobility_US` (`state`, `county_and_city`, `geo_type`, `date`, `driving`, `transit`, " \
              "`walking`) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `state` = %s,`county_and_city` = %s," \
              "`geo_type` = %s, `date` = %s, `driving` = %s, `transit` = %s, `walking` = %s "
        sql_data = "('dummy', 'boone county', 'county', '2020-11-03', 57.129999999999995, 0.0, 0.0, 'dummy', " \
                   "'boone county', 'county', '2020-11-03', 57.129999999999995, 0.0, 0.0) "

        self.assertEqual(test_data, query(sql, sql_data))

    @mock.patch('TestMobilityData.pymysql', autospec=True)
    def test_google_mobility_data(self, mock_pymysql):
        mock_cursor = mock.MagicMock()
        test_data = [{'state': 'dummy', 'county': 'san diego county', 'date': '2020-05-03',
                      'retail and recreation': -53.0, 'grocery and pharmacy': -16.0, 'parks': -36.0,
                      'transit stations': -59.0, 'workplaces': -35.0, 'residential': 13.0}]

        mock_cursor.fetchall.return_value = test_data
        mock_pymysql.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        sql_del = " DELETE FROM `Google_Mobility_US`(`state`, `county`, `date`, `retail and recreation`, " \
                  "`grocery and pharmacy`, `parks`, `transit stations`, `workplaces`, `residential`) " \
                  "VALUES( % s, % s, % s, % s, % s, % s, % s, % s, % s) WHERE `state` = % s," \
                  " `county` = % s, `date` = % s "
        sql_del_data = "('dummy', 'san diego county', '2020-05-03', -53.0, -16.0, -36.0, -59.0, -35.0, 13.0," \
                       " 'dummy', 'san diego county', '2020-05-03')"

        query(sql_del, sql_del_data)

        sql = " INSERT INTO `Google_Mobility_US`(`state`, `county`, `date`, `retail and recreation`, " \
              "`grocery and pharmacy`, `parks`, `transit stations`, `workplaces`, `residential`) " \
              "VALUES( % s, % s, % s, % s, % s, % s, % s, % s, % s) ON DUPLICATE KEY UPDATE `state` = % s," \
              " `county` = % s, `date` = % s "
        sql_data = "('dummy', 'san diego county', '2020-05-03', -53.0, -16.0, -36.0, -59.0, -35.0, 13.0," \
                   " 'dummy', 'san diego county', '2020-05-03')"

        self.assertEqual(test_data, query(sql, sql_data))
