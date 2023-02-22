import unittest
from datetime import date
from epiweeks import Week

from delphi.epidata.server.utils.dates import time_value_to_day, day_to_time_value, shift_day_value, time_value_to_iso, days_in_range, weeks_in_range, week_to_time_value, time_value_to_week, time_values_to_ranges, iterate_over_range, iterate_over_ints_and_ranges


class UnitTests(unittest.TestCase):
    def test_time_value_to_day(self):
        self.assertEqual(time_value_to_day(20201010), date(2020, 10, 10))
        self.assertEqual(time_value_to_day(20190201), date(2019, 2, 1))

    def test_day_to_time_value(self):
        self.assertEqual(day_to_time_value(date(2020, 10, 10)), 20201010)
        self.assertEqual(day_to_time_value(date(2019, 2, 1)), 20190201)

    def test_shift_day_value(self):
        self.assertEqual(shift_day_value(20201010, -3), 20201007)
        self.assertEqual(shift_day_value(20201010, -12), 20200928)

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

    def test_time_value_to_week(self):
        self.assertEqual(time_value_to_week(202021), Week(2020, 21))
        self.assertEqual(time_value_to_week(202101), Week(2021, 1))

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

    def test_iterate_over_range(self):
        self.assertEqual(list(iterate_over_range(20210801, 20210805)), [20210801, 20210802, 20210803, 20210804])
        self.assertEqual(list(iterate_over_range(20210801, 20210801)), [])
        self.assertEqual(list(iterate_over_range(20210801, 20210701)), [])

    def test_iterate_over_ints_and_ranges(self):
        assert list(iterate_over_ints_and_ranges([0, (5, 8)], use_dates=False)) == [0, 5, 6, 7, 8]
        assert list(iterate_over_ints_and_ranges([(5, 8), (4, 6), (3, 5)], use_dates=False)) == [3, 4, 5, 6, 7, 8]
        assert list(iterate_over_ints_and_ranges([(7, 8), (5, 7), (3, 8), 8], use_dates=False)) == [3, 4, 5, 6, 7, 8]
        assert list(iterate_over_ints_and_ranges([2, (2, 3)], use_dates=False)) == [2, 3]
        assert list(iterate_over_ints_and_ranges([20, 50, 25, (21, 25), 23, 30, 31, (24, 26)], use_dates=False)) == [20, 21, 22, 23, 24, 25, 26, 30, 31, 50]

        assert list(iterate_over_ints_and_ranges([20210817])) == [20210817]
        assert list(iterate_over_ints_and_ranges([20210817, (20210810, 20210815)])) == [20210810, 20210811, 20210812, 20210813, 20210814, 20210815, 20210817]
        assert list(iterate_over_ints_and_ranges([(20210801, 20210905), (20210815, 20210915)])) == list(iterate_over_range(20210801, 20210916)) # right-exclusive
