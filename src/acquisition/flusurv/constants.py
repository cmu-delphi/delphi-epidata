from delphi_utils import GeoMapper

"""
As of Sept 2023, for new data we expect to see these 23 groups, as described
in the top-level "master_lookup" element, below, of the new GRASP API
(https://gis.cdc.gov/GRASP/Flu3/PostPhase03DataTool) response object.
See `./reference/new_grasp_result.json` for a full example response.
    'master_lookup' = [
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
        {'Variable': 'Age', 'valueid': 22, 'parentid': 2, 'Label': '12-17 yr', 'Color_HexValue': '#707070', 'Enabled': True}
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
    ]

All 23 strata are available starting epiweek 200935, inclusive.

The previous version of the GRASP API
(https://gis.cdc.gov/GRASP/Flu3/GetPhase03InitApp) used the following age-id
mapping, as described in the top-level "ages" element, below. See
`./reference/old_grasp_result.json` for a full example response.
    'ages' = [
        {'label': '0-4 yr', 'ageid': 1, 'color_hexvalue': '#1B9E77'},
        {'label': '5-17 yr', 'ageid': 2, 'color_hexvalue': '#D95F02'},
        {'label': '18-49 yr', 'ageid': 3, 'color_hexvalue': '#4A298B'},
        {'label': '50-64 yr', 'ageid': 4, 'color_hexvalue': '#E7298A'},
        {'label': '65+ yr', 'ageid': 5, 'color_hexvalue': '#6AA61E'},
        {'label': 'Overall', 'ageid': 6, 'color_hexvalue': '#000000'},
        {'label': '65-74 yr', 'ageid': 7, 'color_hexvalue': '#A6CEE3'},
        {'label': '75-84 yr', 'ageid': 8, 'color_hexvalue': '#CAB2D6'},
        {'label': '85+', 'ageid': 9, 'color_hexvalue': '#1f78b4'}
    ]

In addition to the new age, race, and sex breakdowns, the group id for overall
reporting has changed from 6 to 0. Age ids 1-5 and 7-9 retain the
same meanings; age id 6 is not reported.
"""
HISTORICAL_GROUPS = (
    "rate_overall",

    "rate_age_0",
    "rate_age_1",
    "rate_age_2",
    "rate_age_3",
    "rate_age_4",
    "rate_age_5",
    "rate_age_6",
    "rate_age_7",
)
NEW_AGE_GROUPS = (
    "rate_age_18t29",
    "rate_age_30t39",
    "rate_age_40t49",
    "rate_age_5t11",
    "rate_age_12t17",
    "rate_age_lt18",
    "rate_age_gte18",
    "rate_age_1t4",
    "rate_age_gte75",
    "rate_age_0tlt1",
)
RACE_GROUPS = (
    "rate_race_white",
    "rate_race_black",
    "rate_race_hisp",
    "rate_race_asian",
    "rate_race_natamer",
)
SEX_GROUPS = (
    "rate_sex_male",
    "rate_sex_female",
)
FLU_GROUPS = (
    "rate_flu_a",
    "rate_flu_b",
)
EXPECTED_GROUPS = HISTORICAL_GROUPS + NEW_AGE_GROUPS + RACE_GROUPS + SEX_GROUPS + FLU_GROUPS


# dict(Variable: dict(valueid: output_col_suffix))
ID_TO_LABEL_MAP = {
    "Age": {
        # The column names used in the DB for the original age groups
        # are ordinal, such that:
        #    "rate_age_0" corresponds to age group 1, 0-4 yr
        #    "rate_age_1" corresponds to age group 2, 5-17 yr
        #    "rate_age_2" corresponds to age group 3, 18-49 yr
        #    "rate_age_3" corresponds to age group 4, 50-64 yr
        #    "rate_age_4" corresponds to age group 5, 65+ yr
        #    "rate_age_5" corresponds to age group 7, 65-74 yr
        #    "rate_age_6" corresponds to age group 8, 75-84 yr
        #    "rate_age_7" corresponds to age group 9, 85+ yr
        #
        # Group 6 was the "overall" category and not included in the
        # ordinal naming scheme. Because of that, groups 1-5 have column
        # ids equal to the ageid - 1; groups 7-9 have column ids equal
        # to ageid - 2.
        #
        # Ageid of 6 used to be used for the "overall" category.
        # Now "overall" is represented by a valueid of 0, and ageid of 6
        # is not used for any group. If we see an ageid of 6, something
        # has gone wrong.
        1: "0", # 'Label': '0-4 yr'
        2: "1", # 'Label': '5-17 yr'
        3: "2", # 'Label': '18-49 yr'
        4: "3", # 'Label': '50-64 yr'
        5: "4", # 'Label': '65+ yr'
        7: "5", # 'Label': '65-74 yr'
        8: "6", # 'Label': '75-84 yr'
        9: "7", # 'Label': '85+'
        10: "18t29", # 'Label': '18-29 yr'
        11: "30t39", # 'Label': '30-39 yr'
        12: "40t49", # 'Label': '40-49 yr'
        13: "0tlt1", # 'Label': '0-< 1 yr'
        14: "1t4", # 'Label': '1-4 yr',
        15: "gte75", # 'Label': '>= 75',
        21: "5t11", # 'Label': '5-11  yr'
        22: "12t17", # 'Label': '12-17 yr'
        97: "lt18", # 'Label': '< 18'
        98: "gte18", # 'Label': '>= 18'
    },
    "Race": {
        1: "white", # 'Label': 'White'
        2: "black", # 'Label': 'Black'
        3: "hisp", # 'Label': 'Hispanic/Latino'
        4: "asian", # 'Label': 'Asian/Pacific Islander'
        5: "natamer", # 'Label': 'American Indian/Alaska Native'
    },
    "Sex": {
        1: "male", # 'Label': 'Male'
        2: "female", # 'Label': 'Female'
    },
    "Flutype": {
        1: "a", # 'Label': 'Influenza A'
        2: "b", # 'Label': 'Influenza B'
    },
    # Unused. Leaving here for documentation's sake.
    "Overall": {
        0: "overall", # 'Label': 'Overall'
    },
}



MAX_AGE_TO_CONSIDER_WEEKS = 52


gmpr = GeoMapper()
map_state_names = gmpr.get_crosswalk("state", "state")
map_state_names = map_state_names.to_dict(orient = "records")
map_state_names = {elem["state_name"]: elem["state_id"].upper() for elem in map_state_names}

map_nonstandard_names = {"New York - Albany": "NY_albany", "New York - Rochester": "NY_rochester"}

MAP_REGION_NAMES_TO_ABBR = {**map_state_names, **map_nonstandard_names}

MAP_ENTIRE_NETWORK_NAMES = {
	"FluSurv-NET": "network_all",
	"EIP": "network_eip",
	"IHSP": "network_ihsp"
}


FLUSURV_BASE_URL = "https://gis.cdc.gov/GRASP/Flu3/"
