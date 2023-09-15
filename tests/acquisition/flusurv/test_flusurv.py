"""Unit tests for flusurv.py."""

# standard library
import unittest
from unittest.mock import (MagicMock, sentinel, patch)

import delphi.epidata.acquisition.flusurv.flusurv as flusurv

# py3tester coverage target
__test_target__ = "delphi.epidata.acquisition.flusurv.flusurv"


# Example location-specific return JSON from CDC GRASP API. Contains
#  partial data for "network_all" location and season 49.
network_all_example_data = {
    'default_data': [
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'rate': 20.7, 'weeklyrate': 0.0, 'mmwrid': 2519},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 2, 'rate': 41.3, 'weeklyrate': 0.1, 'mmwrid': 2519},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 1, 'sexid': 0, 'raceid': 0, 'rate': 42, 'weeklyrate': 0.5, 'mmwrid': 2519},

        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'rate': 4.3, 'weeklyrate': 1.7, 'mmwrid': 2493},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 2, 'rate': 11.6, 'weeklyrate': 3.6, 'mmwrid': 2493},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 3, 'rate': 12.8, 'weeklyrate': 4.8, 'mmwrid': 2493},

        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'rate': 20.6, 'weeklyrate': 0.1, 'mmwrid': 2516},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 2, 'rate': 40.7, 'weeklyrate': 0.5, 'mmwrid': 2516},

        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'rate': 20.3, 'weeklyrate': 0.1, 'mmwrid': 2513},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 2, 'rate': 39.6, 'weeklyrate': 0.3, 'mmwrid': 2513},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 3, 'rate': 36.0, 'weeklyrate': 0.1, 'mmwrid': 2513},
    ]
}

# Example metadata response containing "master_lookup" element only, used
#  for mapping between valueids and strata descriptions
master_lookup_metadata = {
    'master_lookup': [
        {'Variable': 'Age', 'valueid': 1, 'parentid': 97, 'Label': '0-4 yr', 'Color_HexValue': '#d19833', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 2, 'parentid': 97, 'Label': '5-17 yr', 'Color_HexValue': '#707070', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 3, 'parentid': 98, 'Label': '18-49 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 4, 'parentid': 98, 'Label': '50-64 yr', 'Color_HexValue': '#516889', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 5, 'parentid': 98, 'Label': '65+ yr', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 7, 'parentid': 5, 'Label': '65-74 yr', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 8, 'parentid': 5, 'Label': '75-84 yr', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 9, 'parentid': 5, 'Label': '85+', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 10, 'parentid': 3, 'Label': '18-29 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 11, 'parentid': 3, 'Label': '30-39 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 12, 'parentid': 3, 'Label': '40-49 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 21, 'parentid': 2, 'Label': '5-11  yr', 'Color_HexValue': '#707070', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 22, 'parentid': 2, 'Label': '12-17 yr', 'Color_HexValue': '#707070', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 97, 'parentid': 0, 'Label': '< 18', 'Color_HexValue': '#000000', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 98, 'parentid': 0, 'Label': '>= 18', 'Color_HexValue': '#000000', 'Enabled': True},

        {'Variable': 'Race', 'valueid': 1, 'parentid': None, 'Label': 'White', 'Color_HexValue': '#516889', 'Enabled': True},
        {'Variable': 'Race', 'valueid': 2, 'parentid': None, 'Label': 'Black', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        {'Variable': 'Race', 'valueid': 3, 'parentid': None, 'Label': 'Hispanic/Latino', 'Color_HexValue': '#d19833', 'Enabled': True},
        {'Variable': 'Race', 'valueid': 4, 'parentid': None, 'Label': 'Asian/Pacific Islander', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        {'Variable': 'Race', 'valueid': 5, 'parentid': None, 'Label': 'American Indian/Alaska Native', 'Color_HexValue': '#007d8e', 'Enabled': True},

        {'Variable': 'Sex', 'valueid': 1, 'parentid': None, 'Label': 'Male', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        {'Variable': 'Sex', 'valueid': 2, 'parentid': None, 'Label': 'Female', 'Color_HexValue': '#F2775F', 'Enabled': True},

        {'Variable': None, 'valueid': 0, 'parentid': 0, 'Label': 'Overall', 'Color_HexValue': '#000000', 'Enabled': True},
    ],
}

# Map derived from "master_lookup" dictionary above mapping between valueids
#  by type and cleaned-up descriptions (no spaces or capital letters, etc)
id_label_map = {
    "Age": {
        1: "0t4",
        2: "5t17",
        3: "18t49",
        4: "50t64",
        5: "65+",
        7: "65t74",
        8: "75t84",
        9: "85+",
        10: "18t29",
        11: "30t39",
        12: "40t49",
        21: "5t11",
        22: "12t17",
        97: "<18",
        98: ">=18",
    },
    "Race": {
        1: "white",
        2: "black",
        3: "hispaniclatino",
        4: "asianpacificislander",
        5: "americanindianalaskanative",
    },
    "Sex": {
        1: "male",
        2: "female",
    },
}


class FunctionTests(unittest.TestCase):
    """Tests each function individually."""

    def test_fetch_json(self):
        """Run through a successful flow."""

        path = "path"
        payload = None

        response_object = MagicMock()
        response_object.status_code = 200
        response_object.headers = {"Content-Type": "application/json"}
        response_object.json.return_value = sentinel.expected

        requests_impl = MagicMock()
        requests_impl.get.return_value = response_object

        actual = flusurv.fetch_json(path, payload, requests_impl=requests_impl)

        self.assertEqual(actual, sentinel.expected)

    def test_mmwrid_to_epiweek(self):
        # Test epoch
        self.assertEqual(flusurv.mmwrid_to_epiweek(2179), 200340)

        metadata = flusurv.fetch_flusurv_metadata()
        for mmwr in metadata["mmwr"]:
            self.assertEqual(flusurv.mmwrid_to_epiweek(mmwr["mmwrid"]), mmwr["yearweek"])

    @patch(__test_target__ + ".fetch_flusurv_location")
    def test_get_data(self, MockFlusurvLocation):
        MockFlusurvLocation.return_value = network_all_example_data

        self.assertEqual(flusurv.get_data("network_all", [30, 49], master_lookup_metadata), {
                201014: {"rate_race_white": 0.0, "rate_race_black": 0.1, "rate_age_0": 0.5},
                200940: {"rate_race_white": 1.7, "rate_race_black": 3.6, "rate_race_hispaniclatino": 4.8},
                201011: {"rate_race_white": 0.1, "rate_race_black": 0.5},
                201008: {"rate_race_white": 0.1, "rate_race_black": 0.3, "rate_race_hispaniclatino": 0.1},
            }
        )

    def test_group_by_epiweek(self):
        input_data = network_all_example_data
        self.assertEqual(flusurv.group_by_epiweek(input_data, master_lookup_metadata), {
                201014: {"rate_race_white": 0.0, "rate_race_black": 0.1, "rate_age_0": 0.5},
                200940: {"rate_race_white": 1.7, "rate_race_black": 3.6, "rate_race_hispaniclatino": 4.8},
                201011: {"rate_race_white": 0.1, "rate_race_black": 0.5},
                201008: {"rate_race_white": 0.1, "rate_race_black": 0.3, "rate_race_hispaniclatino": 0.1},
            }
        )

        duplicate_input_data = {
            'default_data': [
                {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 1, 'sexid': 0, 'raceid': 0, 'rate': 42, 'weeklyrate': 0.5, 'mmwrid': 2519},
                {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 1, 'sexid': 0, 'raceid': 0, 'rate': 42, 'weeklyrate': 54, 'mmwrid': 2519},
            ]
        }

        with self.assertWarnsRegex(Warning, "warning: Multiple rates seen for 201014"):
            flusurv.group_by_epiweek(duplicate_input_data, master_lookup_metadata)

        with self.assertRaisesRegex(Exception, "no data found"):
            flusurv.group_by_epiweek({"default_data": []}, master_lookup_metadata)

    @patch('builtins.print')
    def test_group_by_epiweek_print_msgs(self, mock_print):
        input_data = network_all_example_data
        flusurv.group_by_epiweek(input_data, master_lookup_metadata)
        mock_print.assert_called_with("found data for 4 epiweeks")

    def test_get_current_issue(self):
        input_data = {
            'loaddatetime': 'Sep 12, 2023'
        }
        self.assertEqual(flusurv.get_current_issue(input_data), 202337)

    def test_make_id_label_map(self):
        self.assertEqual(flusurv.make_id_label_map(master_lookup_metadata), id_label_map)

    def test_groupids_to_name(self):
        ids = (
            (1, 0, 0),
            (9, 0, 0),
            (0, 2, 0),
            (0, 0, 3),
            (0, 0, 5),
            (0, 0, 0),
        )
        expected_list = [
            "rate_age_0",
            "rate_age_7",
            "rate_sex_female",
            "rate_race_hispaniclatino",
            "rate_race_americanindianalaskanative",
            "rate_overall",
        ]

        for (ageid, sexid, raceid), expected in zip(ids, expected_list):
            self.assertEqual(flusurv.groupids_to_name(ageid, sexid, raceid, id_label_map), expected)

        with self.assertRaisesRegex(ValueError, "Ageid cannot be 6"):
            flusurv.groupids_to_name(6, 0, 0, id_label_map)
        with self.assertRaisesRegex(AssertionError, "At most one groupid can be non-zero"):
            flusurv.groupids_to_name(1, 1, 0, id_label_map)
            flusurv.groupids_to_name(0, 1, 1, id_label_map)
            flusurv.groupids_to_name(1, 1, 1, id_label_map)
