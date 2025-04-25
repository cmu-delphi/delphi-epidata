"""Unit tests for flusurv.py."""

# standard library
import unittest
from collections import defaultdict
from unittest.mock import (MagicMock, sentinel, patch)

import delphi.epidata.acquisition.flusurv.api as flusurv

# py3tester coverage target
__test_target__ = "delphi.epidata.acquisition.flusurv.api"


network_all_example_data = [
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'flutype': 0, 'rate': 20.7, 'weeklyrate': 0.0, 'mmwrid': 2519},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 2, 'flutype': 0, 'rate': 41.3, 'weeklyrate': 0.1, 'mmwrid': 2519},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 1, 'sexid': 0, 'raceid': 0, 'flutype': 0, 'rate': 42, 'weeklyrate': 0.5, 'mmwrid': 2519},

        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 2, 'raceid': 0, 'flutype': 0, 'rate': 1, 'weeklyrate': 0.1, 'mmwrid': 2519},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 14, 'sexid': 0, 'raceid': 0, 'flutype': 0, 'rate': 2, 'weeklyrate': 0.2, 'mmwrid': 2519},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 8, 'sexid': 0, 'raceid': 0, 'flutype': 0, 'rate': 3, 'weeklyrate': 0.3, 'mmwrid': 2519},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 22, 'sexid': 0, 'raceid': 0, 'flutype': 0, 'rate': 4, 'weeklyrate': 0.4, 'mmwrid': 2519},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 0, 'flutype': 1, 'rate': 5, 'weeklyrate': 0.5, 'mmwrid': 2519},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 0, 'flutype': 2, 'rate': 6, 'weeklyrate': 0.6, 'mmwrid': 2519},

        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'flutype': 0, 'rate': 4.3, 'weeklyrate': 1.7, 'mmwrid': 2493},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 2, 'flutype': 0, 'rate': 11.6, 'weeklyrate': 3.6, 'mmwrid': 2493},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 3, 'flutype': 0, 'rate': 12.8, 'weeklyrate': 4.8, 'mmwrid': 2493},

        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'flutype': 0, 'rate': 20.6, 'weeklyrate': 0.1, 'mmwrid': 2516},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 2, 'flutype': 0, 'rate': 40.7, 'weeklyrate': 0.5, 'mmwrid': 2516},

        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'flutype': 0, 'rate': 20.3, 'weeklyrate': 0.1, 'mmwrid': 2513},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 2, 'flutype': 0, 'rate': 39.6, 'weeklyrate': 0.3, 'mmwrid': 2513},
        {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 3, 'flutype': 0, 'rate': 36.0, 'weeklyrate': 0.1, 'mmwrid': 2513},
    ]

by_epiweek_example_data = {
    201014: {"rate_race_white": 0.0, "rate_race_black": 0.1, "rate_age_0": 0.5, "rate_sex_female": 0.1,
        "rate_age_1t4": 0.2, "rate_age_6": 0.3, "rate_age_12t17": 0.4, "rate_flu_a": 0.5, "rate_flu_b": 0.6,
        "season": "2009-10"},
    200940: {"rate_race_white": 1.7, "rate_race_black": 3.6, "rate_race_hisp": 4.8, "season": "2009-10"},
    201011: {"rate_race_white": 0.1, "rate_race_black": 0.5, "season": "2009-10"},
    201008: {"rate_race_white": 0.1, "rate_race_black": 0.3, "rate_race_hisp": 0.1, "season": "2009-10"},
}

metadata_result = {
    # Last data update date
    'loaddatetime': 'Sep 12, 2023',
    # IDs (network ID + catchment ID) specifying geos and data sources available
    'catchments': [
        {'networkid': 1, 'name': 'FluSurv-NET', 'area': 'Entire Network', 'catchmentid': '22', 'beginseasonid': 49, 'endseasonid': 51},

        {'networkid': 2, 'name': 'EIP', 'area': 'California', 'catchmentid': '1', 'beginseasonid': 43, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'Colorado', 'catchmentid': '2', 'beginseasonid': 43, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'Connecticut', 'catchmentid': '3', 'beginseasonid': 43, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'Entire Network', 'catchmentid': '22', 'beginseasonid': 49, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'Georgia', 'catchmentid': '4', 'beginseasonid': 43, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'Maryland', 'catchmentid': '7', 'beginseasonid': 43, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'Minnesota', 'catchmentid': '9', 'beginseasonid': 43, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'New Mexico', 'catchmentid': '11', 'beginseasonid': 43, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'New York - Albany', 'catchmentid': '13', 'beginseasonid': 43, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'New York - Rochester', 'catchmentid': '14', 'beginseasonid': 43, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'Oregon', 'catchmentid': '17', 'beginseasonid': 43, 'endseasonid': 51},
        {'networkid': 2, 'name': 'EIP', 'area': 'Tennessee', 'catchmentid': '20', 'beginseasonid': 43, 'endseasonid': 51},

        {'networkid': 3, 'name': 'IHSP', 'area': 'Entire Network', 'catchmentid': '22', 'beginseasonid': 49, 'endseasonid': 51},
        {'networkid': 3, 'name': 'IHSP', 'area': 'Idaho', 'catchmentid': '6', 'beginseasonid': 49, 'endseasonid': 51},
        {'networkid': 3, 'name': 'IHSP', 'area': 'Iowa', 'catchmentid': '5', 'beginseasonid': 49, 'endseasonid': 51},
        {'networkid': 3, 'name': 'IHSP', 'area': 'Michigan', 'catchmentid': '8', 'beginseasonid': 49, 'endseasonid': 51},
        {'networkid': 3, 'name': 'IHSP', 'area': 'Ohio', 'catchmentid': '15', 'beginseasonid': 50, 'endseasonid': 51},
        {'networkid': 3, 'name': 'IHSP', 'area': 'Oklahoma', 'catchmentid': '16', 'beginseasonid': 49, 'endseasonid': 50},
        {'networkid': 3, 'name': 'IHSP', 'area': 'Rhode Island', 'catchmentid': '18', 'beginseasonid': 50, 'endseasonid': 51},
        {'networkid': 3, 'name': 'IHSP', 'area': 'South Dakota', 'catchmentid': '19', 'beginseasonid': 49, 'endseasonid': 49},
        {'networkid': 3, 'name': 'IHSP', 'area': 'Utah', 'catchmentid': '21', 'beginseasonid': 50, 'endseasonid': 51}
    ],
    # "seasons" element, used for mapping between seasonids and season year spans.
    'seasons': [
        {'description': 'Season 2003-04', 'enabled': True, 'endweek': 2231, 'label': '2003-04', 'seasonid': 43, 'startweek': 2179, 'IncludeWeeklyRatesAndStrata': True},
        {'description': 'Season 2006-07', 'enabled': True, 'endweek': 2387, 'label': '2006-07', 'seasonid': 46, 'startweek': 2336, 'IncludeWeeklyRatesAndStrata': True},
        {'description': 'Season 2009-10', 'enabled': True, 'endweek': 2544, 'label': '2009-10', 'seasonid': 49, 'startweek': 2488, 'IncludeWeeklyRatesAndStrata': True},
        {'description': 'Season 2021-22', 'enabled': True, 'endweek': 3170, 'label': '2021-22', 'seasonid': 61, 'startweek': 3119, 'IncludeWeeklyRatesAndStrata': False},
        {'description': 'Season 2022-23', 'enabled': True, 'endweek': 3222, 'label': '2022-23', 'seasonid': 62, 'startweek': 3171, 'IncludeWeeklyRatesAndStrata': False},
        # sic
        {'description': 'Season 2023-24 ', 'enabled': True, 'endweek': 3274, 'label': '2023-24', 'seasonid': 63, 'startweek': 3223, 'IncludeWeeklyRatesAndStrata': False},
    ],
    # "master_lookup" element, used for mapping between valueids and strata descriptions
    'master_lookup': [
        {'Variable': 'Age', 'valueid': 1, 'parentid': 97, 'Label': '0-4 yr', 'Color_HexValue': '#d19833', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 2, 'parentid': 97, 'Label': '5-17 yr', 'Color_HexValue': '#707070', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 3, 'parentid': 98, 'Label': '18-49 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 4, 'parentid': 98, 'Label': '50-64 yr', 'Color_HexValue': '#516889', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 5, 'parentid': 98, 'Label': '>= 65 yr', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 7, 'parentid': 5, 'Label': '65-74 yr', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 8, 'parentid': 15, 'Label': '75-84 yr', 'Color_HexValue': '#b2df8a', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 9, 'parentid': 15, 'Label': '>= 85', 'Color_HexValue': '#b2df8a', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 10, 'parentid': 3, 'Label': '18-29 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 11, 'parentid': 3, 'Label': '30-39 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 12, 'parentid': 3, 'Label': '40-49 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 13, 'parentid': 1, 'Label': '0-< 1 yr', 'Color_HexValue': '#d19833', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 14, 'parentid': 1, 'Label': '1-4 yr', 'Color_HexValue': '#d19833', 'Enabled': True},
        {'Variable': 'Age', 'valueid': 15, 'parentid': 5, 'Label': '>= 75', 'Color_HexValue': '#b2df8a', 'Enabled': True},
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

        {'Variable': 'Flutype', 'valueid': 1, 'parentid': None, 'Label': 'Influenza A', 'Color_HexValue': '#FF0000', 'Enabled': True},
        {'Variable': 'Flutype', 'valueid': 2, 'parentid': None, 'Label': 'Influenza B', 'Color_HexValue': '#0000FF', 'Enabled': True},

        {'Variable': None, 'valueid': 0, 'parentid': 0, 'Label': 'Overall', 'Color_HexValue': '#000000', 'Enabled': True},
    ],
    'default_data': network_all_example_data,
    # Mapping each mmwrid to a week number, season, and date. Could use this instead of our current epoch-based function.
    'mmwr': [
        {'mmwrid': 2828, 'weekend': '2016-03-12', 'weeknumber': 10, 'weekstart': '2016-03-06', 'year': 2016, 'yearweek': 201610, 'seasonid': 55, 'label': 'Mar-12-2016', 'weekendlabel': 'Mar 12, 2016', 'weekendlabel2': 'Mar-12-2016'},
        {'mmwrid': 2885, 'weekend': '2017-04-15', 'weeknumber': 15, 'weekstart': '2017-04-09', 'year': 2017, 'yearweek': 201715, 'seasonid': 56, 'label': 'Apr-15-2017', 'weekendlabel': 'Apr 15, 2017', 'weekendlabel2': 'Apr-15-2017'},
        {'mmwrid': 2911, 'weekend': '2017-10-14', 'weeknumber': 41, 'weekstart': '2017-10-08', 'year': 2017, 'yearweek': 201741, 'seasonid': 57, 'label': 'Oct-14-2017', 'weekendlabel': 'Oct 14, 2017', 'weekendlabel2': 'Oct-14-2017'},
        {'mmwrid': 2928, 'weekend': '2018-02-10', 'weeknumber': 6, 'weekstart': '2018-02-04', 'year': 2018, 'yearweek': 201806, 'seasonid': 57, 'label': 'Feb-10-2018', 'weekendlabel': 'Feb 10, 2018', 'weekendlabel2': 'Feb-10-2018'},
        {'mmwrid': 2974, 'weekend': '2018-12-29', 'weeknumber': 52, 'weekstart': '2018-12-23', 'year': 2018, 'yearweek': 201852, 'seasonid': 58, 'label': 'Dec-29-2018', 'weekendlabel': 'Dec 29, 2018', 'weekendlabel2': 'Dec-29-2018'},
        {'mmwrid': 3031, 'weekend': '2020-02-01', 'weeknumber': 5, 'weekstart': '2020-01-26', 'year': 2020, 'yearweek': 202005, 'seasonid': 59, 'label': 'Feb-01-2020', 'weekendlabel': 'Feb 01, 2020', 'weekendlabel2': 'Feb-01-2020'},
        {'mmwrid': 3037, 'weekend': '2020-03-14', 'weeknumber': 11, 'weekstart': '2020-03-08', 'year': 2020, 'yearweek': 202011, 'seasonid': 59, 'label': 'Mar-14-2020', 'weekendlabel': 'Mar 14, 2020', 'weekendlabel2': 'Mar-14-2020'},
        {'mmwrid': 3077, 'weekend': '2020-12-19', 'weeknumber': 51, 'weekstart': '2020-12-13', 'year': 2020, 'yearweek': 202051, 'seasonid': 60, 'label': 'Dec-19-2020', 'weekendlabel': 'Dec 19, 2020', 'weekendlabel2': 'Dec-19-2020'},
        {'mmwrid': 3140, 'weekend': '2022-03-05', 'weeknumber': 9, 'weekstart': '2022-02-27', 'year': 2022, 'yearweek': 202209, 'seasonid': 61, 'label': 'Mar-05-2022', 'weekendlabel': 'Mar 05, 2022', 'weekendlabel2': 'Mar-05-2022'},
        {'mmwrid': 3183, 'weekend': '2022-12-31', 'weeknumber': 52, 'weekstart': '2022-12-25', 'year': 2022, 'yearweek': 202252, 'seasonid': 62, 'label': 'Dec-31-2022', 'weekendlabel': 'Dec 31, 2022', 'weekendlabel2': 'Dec-31-2022'},
    ]
}

# Example location-specific return JSON from CDC GRASP API. Contains
#  partial data for "network_all" location and season 49.
location_api_result = {'default_data': network_all_example_data}


# Map derived from "master_lookup" dictionary above, mapping between valueids
#  by type and cleaned-up descriptions (no spaces or capital letters, etc)
id_group_map = {
    "Age": {
        1: "0",
        2: "1",
        3: "2",
        4: "3",
        5: "4",
        7: "5",
        8: "6",
        9: "7",
        10: "18t29",
        11: "30t39",
        12: "40t49",
        13: "0tlt1",
        14: "1t4",
        15: "gte75",
        21: "5t11",
        22: "12t17",
        97: "lt18",
        98: "gte18",
    },
    "Race": {
        1: "white",
        2: "black",
        3: "hisp",
        4: "asian",
        5: "natamer",
    },
    "Sex": {
        1: "male",
        2: "female",
    },
    "Flutype": {
        1: "a",
        2: "b",
    },
    # Unused. Leaving here for documentation's sake.
    "Overall": {
        0: "overall",
    },
}

catchment_name_map = {
    "CA": (2, 1),
    "CO": (2, 2),
    "CT": (2, 3),
    "GA": (2, 4),
    "IA": (3, 5),
    "ID": (3, 6),
    "MD": (2, 7),
    "MI": (3, 8),
    "MN": (2, 9),
    "NM": (2, 11),
    "NY_albany": (2, 13),
    "NY_rochester": (2, 14),
    "OH": (3, 15),
    "OK": (3, 16),
    "OR": (2, 17),
    "RI": (3, 18),
    "SD": (3, 19),
    "TN": (2, 20),
    "UT": (3, 21),
    "network_all": (1, 22),
    "network_eip": (2, 22),
    "network_ihsp": (3, 22),
}

with patch(__test_target__ + ".fetch_json",
    return_value = metadata_result) as MockFlusurvMetadata:
    metadata_fetcher = flusurv.FlusurvMetadata(52)
    api_fetcher = flusurv.FlusurvLocationFetcher(52)


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

        for mmwr in metadata_result["mmwr"]:
            self.assertEqual(flusurv.mmwrid_to_epiweek(mmwr["mmwrid"]), mmwr["yearweek"])

    def test_metadata_attributes(self):
        self.assertEqual(metadata_fetcher.metadata, metadata_result)
        self.assertEqual(metadata_fetcher.issue, 202337)
        self.assertEqual(metadata_fetcher.max_age_weeks, 52)
        self.assertEqual(metadata_fetcher.seasonids, {61, 62, 63})

        self.assertEqual(metadata_fetcher.location_to_code, catchment_name_map)
        self.assertEqual(metadata_fetcher.locations, catchment_name_map.keys())

        self.assertEqual(metadata_fetcher.id_to_group, id_group_map)
        self.assertEqual(metadata_fetcher.id_to_season, {
            43: '2003-04',
            46: '2006-07',
            49: '2009-10',
            61: '2021-22',
            62: '2022-23',
            63: '2023-24',
        })

    def test_geo_name_conversion(self):
        geos = (
            "California",
            "Utah",
            "Entire Network",
            "Entire Network",
            "Entire Network",
            "New York - Albany",
            "New York - Rochester",
        )
        networks = (
            "FluSurv-NET",
            "FluSurv-NET",
            "FluSurv-NET",
            "IHSP",
            "EIP",
            "FluSurv-NET",
        )
        expected_list = [
            "CA",
            "UT",
            "network_all",
            "network_ihsp",
            "network_eip",
            "NY_albany",
            "NY_rochester",
        ]

        for (geo, network), expected in zip(zip(geos, networks), expected_list):
            self.assertEqual(metadata_fetcher._location_name_to_abbr(geo, network), expected)

    @patch(__test_target__ + ".fetch_json")
    def test_get_data(self, MockFlusurvLocation):
        MockFlusurvLocation.return_value = location_api_result

        season_api_fetcher = api_fetcher
        season_api_fetcher.metadata.seasonids = [30, 49]

        self.assertEqual(season_api_fetcher.get_data("network_all"), by_epiweek_example_data)

    @patch(__test_target__ + ".fetch_json")
    def test_fetch_flusurv_location(self, MockFlusurvLocation):
        # API returns normal result
        MockFlusurvLocation.return_value = location_api_result
        self.assertEqual(api_fetcher._fetch_flusurv_location("network_all"), location_api_result)

        # API returns empty result formatted normally
        empty_expected_result = {"default_data": []}
        MockFlusurvLocation.return_value = empty_expected_result
        with self.assertWarnsRegex(Warning, "No data was returned from the API for network_all"):
            empty_data_result = api_fetcher._fetch_flusurv_location("network_all")
        self.assertEqual(empty_data_result, empty_expected_result)

        # API returns "no data" result
        MockFlusurvLocation.return_value = {"default_data": {"response": "No Data"}}
        with self.assertWarnsRegex(Warning, "No data was returned from the API for network_all"):
            no_data_result = api_fetcher._fetch_flusurv_location("network_all")
        self.assertEqual(no_data_result, empty_expected_result)

    def test_group_by_epiweek(self):
        self.assertEqual(api_fetcher._group_by_epiweek(metadata_result), by_epiweek_example_data)

        duplicate_input_data = {
            'default_data': [
                {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 1, 'sexid': 0, 'raceid': 0, 'flutype': 0, 'rate': 42, 'weeklyrate': 0.5, 'mmwrid': 2519},
                {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 1, 'sexid': 0, 'raceid': 0, 'flutype': 0, 'rate': 42, 'weeklyrate': 54, 'mmwrid': 2519},
            ]
        }

        with self.assertWarnsRegex(Warning, "warning: Multiple rates seen for 201014"):
            api_fetcher._group_by_epiweek(duplicate_input_data)

        self.assertEqual(
            api_fetcher._group_by_epiweek({"default_data": []}),
            defaultdict(lambda: defaultdict(lambda: None))
        )

    @patch('builtins.print')
    def test_group_by_epiweek_print_msgs(self, mock_print):
        api_fetcher._group_by_epiweek(metadata_result)
        mock_print.assert_called_with("found data for 4 epiweeks")

    def test_groupids_to_name(self):
        ids = (
            (1, 0, 0, 0),
            (9, 0, 0, 0),
            (0, 2, 0, 0),
            (0, 0, 3, 0),
            (0, 0, 5, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 2),
            (0, 0, 0, 1),
            (13, 0, 0, 0),
            (97, 0, 0, 0),
            (999, 0, 0, 0),
            (0, 0, 111, 0),
        )
        expected_list = [
            "rate_age_0",
            "rate_age_7",
            "rate_sex_female",
            "rate_race_hisp",
            "rate_race_natamer",
            "rate_overall",
            "rate_flu_b",
            "rate_flu_a",
            "rate_age_0tlt1",
            "rate_age_lt18",
            "rate_age_999",
            "rate_race_111",
        ]

        for (ageid, sexid, raceid, fluid), expected in zip(ids, expected_list):
            self.assertEqual(api_fetcher._groupid_to_name(ageid, sexid, raceid, fluid), expected)

        with self.assertRaisesRegex(ValueError, "Ageid cannot be 6"):
            api_fetcher._groupid_to_name(6, 0, 0, 0)
        with self.assertRaisesRegex(ValueError, "Expect at least three of four group ids to be 0"):
            api_fetcher._groupid_to_name(1, 1, 0, 0)
            api_fetcher._groupid_to_name(0, 1, 1, 0)
            api_fetcher._groupid_to_name(1, 1, 1, 1)
