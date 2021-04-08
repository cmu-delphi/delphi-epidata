import unittest
from datetime import date

from delphi.epidata.server.endpoints.covidcast_utils.dates import time_value_to_date, date_to_time_value, shift_time_value


class UnitTests(unittest.TestCase):
    def test_time_value_to_date(self):
        self.assertEqual(time_value_to_date(20201010), date(2020, 10, 10))
        self.assertEqual(time_value_to_date(20190201), date(2019, 2, 1))

    def test_date_to_time_value(self):
        self.assertEqual(date_to_time_value(date(2020, 10, 10)), 20201010)
        self.assertEqual(date_to_time_value(date(2019, 2, 1)), 20190201)

    def test_shift_time_value(self):
        self.assertEqual(shift_time_value(20201010, -3), 20201007)
        self.assertEqual(shift_time_value(20201010, -12), 20200928)
