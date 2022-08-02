import unittest
from datetime import date
from epiweeks import Week

from ....src.server.utils.dates import time_value_to_date, date_to_time_value, shift_time_value, time_value_to_iso, days_in_range, weeks_in_range, week_to_time_value, week_value_to_week, time_value_range


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

    def test_time_value_to_iso(self):
        self.assertEqual(time_value_to_iso(20201010), "2020-10-10")
        self.assertEqual(time_value_to_iso(20190201), "2019-02-01")

    def test_days_in_range(self):
        self.assertEqual(days_in_range((20201010, 20201010)), 1)
        self.assertEqual(days_in_range((20201010, 20201011)), 2)
        self.assertEqual(days_in_range((20200130, 20200203)), 5)

    def test_weeks_in_range(self):
        self.assertEqual(weeks_in_range((202110, 202110)), 1)
        self.assertEqual(weeks_in_range((202110, 202112)), 3)
        self.assertEqual(weeks_in_range((202001, 202101)), 54) # 2020 has 53 weeks
        self.assertEqual(weeks_in_range((202101, 202204)), 56)

    def test_week_value_to_week(self):
        self.assertEqual(week_value_to_week(202021), Week(2020, 21))
        self.assertEqual(week_value_to_week(202101), Week(2021, 1))

    def test_week_to_time_value(self):
        self.assertEqual(week_to_time_value(Week(2021, 1)), 202101)
        self.assertEqual(week_to_time_value(Week(2020, 42)), 202042)

    def test_time_value_range(self):
        self.assertEqual(list(time_value_range(20210801, 20210805)), [20210801, 20210802, 20210803, 20210804])
        self.assertEqual(list(time_value_range(20210801, 20210801)), [])
        self.assertEqual(list(time_value_range(20210801, 20210701)), [])
