import unittest
from datetime import date
from epiweeks import Week

from delphi.epidata.server.utils.dates import time_value_to_date, date_to_time_value, shift_time_value, time_value_to_iso, days_in_range, weeks_in_range, week_to_time_value, week_value_to_week, time_values_to_ranges


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

    def test_time_values_to_ranges(self):
        self.assertEqual(time_values_to_ranges(None), None)
        self.assertEqual(time_values_to_ranges([]), [])
        # days
        self.assertEqual(time_values_to_ranges([20200101]), [20200101])
        self.assertEqual(time_values_to_ranges([(20200101, 20200105)]), [(20200101, 20200105)])
        self.assertEqual(time_values_to_ranges([20211231, (20211230, 20220102), 20220102]), [(20211230, 20220102)])
        self.assertEqual(time_values_to_ranges([20200101, 20200102, (20200101, 20200104), 20200106]), [(20200101, 20200104), 20200106])
        # weeks
        self.assertEqual(time_values_to_ranges([202001]), [202001])
        self.assertEqual(time_values_to_ranges([(202001, 202005)]), [(202001, 202005)])
        self.assertEqual(time_values_to_ranges([202051, (202050, 202102), 202101]), [(202050, 202102)])
        self.assertEqual(time_values_to_ranges([202050, 202051, (202050, 202101), 202103]), [(202050, 202101), 202103])
        # non-contiguous integers that represent actually contiguous time objects should join to become a range:
        self.assertEqual(time_values_to_ranges([20200228, 20200301]), [20200228, 20200301]) # this is NOT a range because 2020 was a leap year
        self.assertEqual(time_values_to_ranges([20210228, 20210301]), [(20210228, 20210301)]) # this becomes a range because these dates are indeed consecutive
        # individual weeks become a range (2020 is a rare year with 53 weeks)
        self.assertEqual(time_values_to_ranges([202051, 202052, 202053, 202101, 202102]), [(202051, 202102)])
