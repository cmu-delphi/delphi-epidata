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
reporting has changed from 6 to 0. Age ids 1-5 and 7-9 retain the same the
same meanings; age id 6 is not reported.
"""
EXPECTED_GROUPS = (
    "rate_overall",

    "rate_age_0",
    "rate_age_1",
    "rate_age_2",
    "rate_age_3",
    "rate_age_4",
    "rate_age_5",
    "rate_age_6",
    "rate_age_7",

    "rate_age_18t29",
    "rate_age_30t39",
    "rate_age_40t49",
    "rate_age_5t11",
    "rate_age_12t17",
    "rate_age_lt18",
    "rate_age_gte18",

    "rate_race_white",
    "rate_race_black",
    "rate_race_hisp",
    "rate_race_asian",
    "rate_race_natamer",

    "rate_sex_male",
    "rate_sex_female"
)


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
