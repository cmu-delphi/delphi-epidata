# The dataset calls the same viruses, provinces, regions (province groups),
# and country by multiple names. Map each of those to a common abbreviation.
VIRUSES = {
    "parainfluenza": "hpiv",
    "piv": "hpiv",
    "para": "hpiv",
    "adenovirus": "adv",
    "adeno": "adv",
    "human metapneumovirus": "hmpv",
    "enterovirus/rhinovirus": "evrv",
    "rhinovirus": "evrv",
    "rhv": "evrv",
    "entero/rhino": "evrv",
    "rhino":"evrv",
    "ev/rv":"evrv",
    "coronavirus":"hcov",
    "coron":"hcov",
    "coro":"hcov",
    "respiratory syncytial virus":"rsv",
    "influenza":"flu",
    "sars-cov-2":"sarscov2",
}

GEOS = {
    "newfoundland": "nl",
    "newfoundland and labrador": "nl",
    "prince edward island":"pe",
    "nova scotia":"ns",
    "new brunswick":"nb",
    "québec":"qc",
    "quebec":"qc",
    "ontario":"on",
    "manitoba" : "mb",
    "saskatchewan":"sk",
    "alberta": "ab",
    "british columbia" :"bc",
    "yukon" : "yk",
    "northwest territories" : "nt",
    "nunavut" : "nu",
    "canada":"ca",
    "can":"ca" ,
    "at":"atlantic",
    "atl":"atlantic",
    "pr" :"prairies" ,
    "terr" :"territories",
 }

# Regions are groups of provinces that are geographically close together. Some single provinces are reported as their own region (e.g. Québec, Ontario).
REGIONS = ['atlantic','atl','at','province of québec','québec','qc','province of ontario','ontario','on',
            'prairies', 'pr', "british columbia",'bc',"territories",'terr',]
NATION = ["canada","can",'ca',]

# Construct dashboard and data report URLS.
DASHBOARD_BASE_URL = "https://health-infobase.canada.ca/src/data/respiratory-virus-detections/"
DASHBOARD_W_DATE_URL = DASHBOARD_BASE_URL + "archive/{date}/"
DASHBOARD_BASE_URLS_2023 = (
    DASHBOARD_W_DATE_URL.format(date = date) for date in
    (
        "2024-06-20",
        "2024-06-27",
        "2024-07-04",
        "2024-07-11",
        "2024-07-18",
        "2024-08-01",
        "2024-08-08",
        "2024-08-15",
        "2024-08-22",
        "2024-08-29",
        "2024-09-05"
    )
)

SEASON_BASE_URL = "https://www.canada.ca"
ALTERNATIVE_SEASON_BASE_URL = "www.phac-aspc.gc.ca/bid-bmi/dsd-dsm/rvdi-divr/"
HISTORIC_SEASON_REPORTS_URL + "/en/public-health/services/surveillance/respiratory-virus-detections-canada/{year_range}.html"

# Each URL created here points to a list of all data reports made during that
# season, e.g.
# https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2014-2015.html.
# The Public Health Agency of Canada site switched in 2024 to reporting
# disease data in a dashboard with a static URL. Therefore, this collection
# of URLs does _NOT_ need to be updated. It is used for fetching historical
# data (for dates on or before June 8, 2024) only.
HISTORIC_SEASON_URL = (HISTORIC_SEASON_REPORTS_URL.format(year_range = year_range) for year_range in
    (
        "2013-2014",
        "2014-2015",
        "2015-2016",
        "2016-2017",
        "2017-2018",
        "2018-2019",
        "2019-2020",
        "2020-2021",
        "2021-2022",
        "2022-2023",
        "2023-2024"
    )
)

DASHBOARD_UPDATE_DATE_FILE = "RVD_UpdateDate.csv"
DASHBOARD_DATA_FILE = "RVD_WeeklyData.csv"

RESP_COUNTS_OUTPUT_FILE = "respiratory_detections.csv"
POSITIVE_TESTS_OUTPUT_FILE = "positive_tests.csv"

LAST_WEEK_OF_YEAR = 35
