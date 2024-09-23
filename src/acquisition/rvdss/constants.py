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
    "sars-cov-2":"sarscov2"
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
    "terr" :"territories"
 }

REGIONS = ['atlantic','atl','at','province of québec','québec','qc','province of ontario','ontario','on',
            'prairies', 'pr', "british columbia",'bc',"territories",'terr']
NATION = ["canada","can",'ca']

DASHBOARD_BASE_URL_2023 = "https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/{date}/"
DASHBOARD_BASE_URLS_2023 = (
    DASHBOARD_BASE_URL_2023.format(date = date) for date in
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

LAST_WEEK_OF_YEAR = 35
