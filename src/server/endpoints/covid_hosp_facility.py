from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH
from .._validate import require_all, extract_strings, extract_integers
from .._query import filter_strings, execute_query, filter_integers

# first argument is the endpoint name
bp = Blueprint("covid_hosp_facility", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("hospital_pks", "collection_weeks")
    hospital_pks = extract_strings("hospital_pks")
    collection_weeks = extract_integers("collection_weeks")
    publication_dates = extract_integers("publication_dates")

    # build query
    table = "covid_hosp_facility c"
    fields = ", ".join(
        [
            "c.`publication_date`",
            "c.`hospital_pk`",
            "c.`collection_week`",
            "c.`state`",
            "c.`ccn`",
            "c.`hospital_name`",
            "c.`address`",
            "c.`city`",
            "c.`zip`",
            "c.`hospital_subtype`",
            "c.`fips_code`",
            "c.`is_metro_micro`",
            "c.`total_beds_7_day_avg`",
            "c.`all_adult_hospital_beds_7_day_avg`",
            "c.`all_adult_hospital_inpatient_beds_7_day_avg`",
            "c.`inpatient_beds_used_7_day_avg`",
            "c.`all_adult_hospital_inpatient_bed_occupied_7_day_avg`",
            "c.`total_adult_patients_hosp_confirmed_suspected_covid_7d_avg`",
            "c.`total_adult_patients_hospitalized_confirmed_covid_7_day_avg`",
            "c.`total_pediatric_patients_hosp_confirmed_suspected_covid_7d_avg`",
            "c.`total_pediatric_patients_hospitalized_confirmed_covid_7_day_avg`",
            "c.`inpatient_beds_7_day_avg`",
            "c.`total_icu_beds_7_day_avg`",
            "c.`total_staffed_adult_icu_beds_7_day_avg`",
            "c.`icu_beds_used_7_day_avg`",
            "c.`staffed_adult_icu_bed_occupancy_7_day_avg`",
            "c.`staffed_icu_adult_patients_confirmed_suspected_covid_7d_avg`",
            "c.`staffed_icu_adult_patients_confirmed_covid_7_day_avg`",
            "c.`total_patients_hospitalized_confirmed_influenza_7_day_avg`",
            "c.`icu_patients_confirmed_influenza_7_day_avg`",
            "c.`total_patients_hosp_confirmed_influenza_and_covid_7d_avg`",
            "c.`total_beds_7_day_sum`",
            "c.`all_adult_hospital_beds_7_day_sum`",
            "c.`all_adult_hospital_inpatient_beds_7_day_sum`",
            "c.`inpatient_beds_used_7_day_sum`",
            "c.`all_adult_hospital_inpatient_bed_occupied_7_day_sum`",
            "c.`total_adult_patients_hosp_confirmed_suspected_covid_7d_sum`",
            "c.`total_adult_patients_hospitalized_confirmed_covid_7_day_sum`",
            "c.`total_pediatric_patients_hosp_confirmed_suspected_covid_7d_sum`",
            "c.`total_pediatric_patients_hospitalized_confirmed_covid_7_day_sum`",
            "c.`inpatient_beds_7_day_sum`",
            "c.`total_icu_beds_7_day_sum`",
            "c.`total_staffed_adult_icu_beds_7_day_sum`",
            "c.`icu_beds_used_7_day_sum`",
            "c.`staffed_adult_icu_bed_occupancy_7_day_sum`",
            "c.`staffed_icu_adult_patients_confirmed_suspected_covid_7d_sum`",
            "c.`staffed_icu_adult_patients_confirmed_covid_7_day_sum`",
            "c.`total_patients_hospitalized_confirmed_influenza_7_day_sum`",
            "c.`icu_patients_confirmed_influenza_7_day_sum`",
            "c.`total_patients_hosp_confirmed_influenza_and_covid_7d_sum`",
            "c.`total_beds_7_day_coverage`",
            "c.`all_adult_hospital_beds_7_day_coverage`",
            "c.`all_adult_hospital_inpatient_beds_7_day_coverage`",
            "c.`inpatient_beds_used_7_day_coverage`",
            "c.`all_adult_hospital_inpatient_bed_occupied_7_day_coverage`",
            "c.`total_adult_patients_hosp_confirmed_suspected_covid_7d_cov`",
            "c.`total_adult_patients_hospitalized_confirmed_covid_7_day_coverage`",
            "c.`total_pediatric_patients_hosp_confirmed_suspected_covid_7d_cov`",
            "c.`total_pediatric_patients_hosp_confirmed_covid_7d_cov`",
            "c.`inpatient_beds_7_day_coverage`",
            "c.`total_icu_beds_7_day_coverage`",
            "c.`total_staffed_adult_icu_beds_7_day_coverage`",
            "c.`icu_beds_used_7_day_coverage`",
            "c.`staffed_adult_icu_bed_occupancy_7_day_coverage`",
            "c.`staffed_icu_adult_patients_confirmed_suspected_covid_7d_cov`",
            "c.`staffed_icu_adult_patients_confirmed_covid_7_day_coverage`",
            "c.`total_patients_hospitalized_confirmed_influenza_7_day_coverage`",
            "c.`icu_patients_confirmed_influenza_7_day_coverage`",
            "c.`total_patients_hosp_confirmed_influenza_and_covid_7d_cov`",
            "c.`previous_day_admission_adult_covid_confirmed_7_day_sum`",
            "c.`previous_day_admission_adult_covid_confirmed_18_19_7_day_sum`",
            "c.`previous_day_admission_adult_covid_confirmed_20_29_7_day_sum`",
            "c.`previous_day_admission_adult_covid_confirmed_30_39_7_day_sum`",
            "c.`previous_day_admission_adult_covid_confirmed_40_49_7_day_sum`",
            "c.`previous_day_admission_adult_covid_confirmed_50_59_7_day_sum`",
            "c.`previous_day_admission_adult_covid_confirmed_60_69_7_day_sum`",
            "c.`previous_day_admission_adult_covid_confirmed_70_79_7_day_sum`",
            "c.`previous_day_admission_adult_covid_confirmed_80plus_7_day_sum`",
            "c.`previous_day_admission_adult_covid_confirmed_unknown_7_day_sum`",
            "c.`previous_day_admission_pediatric_covid_confirmed_7_day_sum`",
            "c.`previous_day_covid_ed_visits_7_day_sum`",
            "c.`previous_day_admission_adult_covid_suspected_7_day_sum`",
            "c.`previous_day_admission_adult_covid_suspected_18_19_7_day_sum`",
            "c.`previous_day_admission_adult_covid_suspected_20_29_7_day_sum`",
            "c.`previous_day_admission_adult_covid_suspected_30_39_7_day_sum`",
            "c.`previous_day_admission_adult_covid_suspected_40_49_7_day_sum`",
            "c.`previous_day_admission_adult_covid_suspected_50_59_7_day_sum`",
            "c.`previous_day_admission_adult_covid_suspected_60_69_7_day_sum`",
            "c.`previous_day_admission_adult_covid_suspected_70_79_7_day_sum`",
            "c.`previous_day_admission_adult_covid_suspected_80plus_7_day_sum`",
            "c.`previous_day_admission_adult_covid_suspected_unknown_7_day_sum`",
            "c.`previous_day_admission_pediatric_covid_suspected_7_day_sum`",
            "c.`previous_day_total_ed_visits_7_day_sum`",
            "c.`previous_day_admission_influenza_confirmed_7_day_sum`",
        ]
    )
    # basic query info
    order = "c.`collection_week` ASC, c.`hospital_pk` ASC, c.`publication_date` ASC"
    params = dict()
    # build the filter
    # build the date filter
    condition_collection_week = filter_integers(
        "c.`collection_week`", collection_weeks, "cw", params
    )
    # build the state filter
    condition_hospital_pk = filter_strings(
        "c.`hospital_pk`", hospital_pks, "hp", params
    )
    if publication_dates:
        # build the issue filter
        condition_publication_date = filter_integers(
            "c.`publication_date`", publication_dates, "pd", params
        )
        # final query using specific issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_collection_week}) AND ({condition_hospital_pk}) AND ({condition_publication_date}) ORDER BY {order}"
    else:
        # final query using most recent issues
        subquery = f"(SELECT max(`publication_date`) `max_publication_date`, `collection_week`, `hospital_pk` FROM {table} WHERE ({condition_collection_week}) AND ({condition_hospital_pk}) GROUP BY `collection_week`, `hospital_pk`) x"
        condition = "x.`max_publication_date` = c.`publication_date` AND x.`collection_week` = c.`collection_week` AND x.`hospital_pk` = c.`hospital_pk`"
        query = f"SELECT {fields} FROM {table} JOIN {subquery} ON {condition} ORDER BY {order}"

    # get the data from the database
    fields_string = [
        "hospital_pk",
        "state",
        "ccn",
        "hospital_name",
        "address",
        "city",
        "zip",
        "hospital_subtype",
        "fips_code",
    ]
    fields_int = [
        "publication_date",
        "collection_week",
        "is_metro_micro",
        "total_beds_7_day_sum",
        "all_adult_hospital_beds_7_day_sum",
        "all_adult_hospital_inpatient_beds_7_day_sum",
        "inpatient_beds_used_7_day_sum",
        "all_adult_hospital_inpatient_bed_occupied_7_day_sum",
        "total_adult_patients_hosp_confirmed_suspected_covid_7d_sum",
        "total_adult_patients_hospitalized_confirmed_covid_7_day_sum",
        "total_pediatric_patients_hosp_confirmed_suspected_covid_7d_sum",
        "total_pediatric_patients_hospitalized_confirmed_covid_7_day_sum",
        "inpatient_beds_7_day_sum",
        "total_icu_beds_7_day_sum",
        "total_staffed_adult_icu_beds_7_day_sum",
        "icu_beds_used_7_day_sum",
        "staffed_adult_icu_bed_occupancy_7_day_sum",
        "staffed_icu_adult_patients_confirmed_suspected_covid_7d_sum",
        "staffed_icu_adult_patients_confirmed_covid_7_day_sum",
        "total_patients_hospitalized_confirmed_influenza_7_day_sum",
        "icu_patients_confirmed_influenza_7_day_sum",
        "total_patients_hosp_confirmed_influenza_and_covid_7d_sum",
        "total_beds_7_day_coverage",
        "all_adult_hospital_beds_7_day_coverage",
        "all_adult_hospital_inpatient_beds_7_day_coverage",
        "inpatient_beds_used_7_day_coverage",
        "all_adult_hospital_inpatient_bed_occupied_7_day_coverage",
        "total_adult_patients_hosp_confirmed_suspected_covid_7d_cov",
        "total_adult_patients_hospitalized_confirmed_covid_7_day_coverage",
        "total_pediatric_patients_hosp_confirmed_suspected_covid_7d_cov",
        "total_pediatric_patients_hosp_confirmed_covid_7d_cov",
        "inpatient_beds_7_day_coverage",
        "total_icu_beds_7_day_coverage",
        "total_staffed_adult_icu_beds_7_day_coverage",
        "icu_beds_used_7_day_coverage",
        "staffed_adult_icu_bed_occupancy_7_day_coverage",
        "staffed_icu_adult_patients_confirmed_suspected_covid_7d_cov",
        "staffed_icu_adult_patients_confirmed_covid_7_day_coverage",
        "total_patients_hospitalized_confirmed_influenza_7_day_coverage",
        "icu_patients_confirmed_influenza_7_day_coverage",
        "total_patients_hosp_confirmed_influenza_and_covid_7d_cov",
        "previous_day_admission_adult_covid_confirmed_7_day_sum",
        "previous_day_admission_adult_covid_confirmed_18_19_7_day_sum",
        "previous_day_admission_adult_covid_confirmed_20_29_7_day_sum",
        "previous_day_admission_adult_covid_confirmed_30_39_7_day_sum",
        "previous_day_admission_adult_covid_confirmed_40_49_7_day_sum",
        "previous_day_admission_adult_covid_confirmed_50_59_7_day_sum",
        "previous_day_admission_adult_covid_confirmed_60_69_7_day_sum",
        "previous_day_admission_adult_covid_confirmed_70_79_7_day_sum",
        "previous_day_admission_adult_covid_confirmed_80plus_7_day_sum",
        "previous_day_admission_adult_covid_confirmed_unknown_7_day_sum",
        "previous_day_admission_pediatric_covid_confirmed_7_day_sum",
        "previous_day_covid_ed_visits_7_day_sum",
        "previous_day_admission_adult_covid_suspected_7_day_sum",
        "previous_day_admission_adult_covid_suspected_18_19_7_day_sum",
        "previous_day_admission_adult_covid_suspected_20_29_7_day_sum",
        "previous_day_admission_adult_covid_suspected_30_39_7_day_sum",
        "previous_day_admission_adult_covid_suspected_40_49_7_day_sum",
        "previous_day_admission_adult_covid_suspected_50_59_7_day_sum",
        "previous_day_admission_adult_covid_suspected_60_69_7_day_sum",
        "previous_day_admission_adult_covid_suspected_70_79_7_day_sum",
        "previous_day_admission_adult_covid_suspected_80plus_7_day_sum",
        "previous_day_admission_adult_covid_suspected_unknown_7_day_sum",
        "previous_day_admission_pediatric_covid_suspected_7_day_sum",
        "previous_day_total_ed_visits_7_day_sum",
        "previous_day_admission_influenza_confirmed_7_day_sum",
    ]
    fields_float = [
        "total_beds_7_day_avg",
        "all_adult_hospital_beds_7_day_avg",
        "all_adult_hospital_inpatient_beds_7_day_avg",
        "inpatient_beds_used_7_day_avg",
        "all_adult_hospital_inpatient_bed_occupied_7_day_avg",
        "total_adult_patients_hosp_confirmed_suspected_covid_7d_avg",
        "total_adult_patients_hospitalized_confirmed_covid_7_day_avg",
        "total_pediatric_patients_hosp_confirmed_suspected_covid_7d_avg",
        "total_pediatric_patients_hospitalized_confirmed_covid_7_day_avg",
        "inpatient_beds_7_day_avg",
        "total_icu_beds_7_day_avg",
        "total_staffed_adult_icu_beds_7_day_avg",
        "icu_beds_used_7_day_avg",
        "staffed_adult_icu_bed_occupancy_7_day_avg",
        "staffed_icu_adult_patients_confirmed_suspected_covid_7d_avg",
        "staffed_icu_adult_patients_confirmed_covid_7_day_avg",
        "total_patients_hospitalized_confirmed_influenza_7_day_avg",
        "icu_patients_confirmed_influenza_7_day_avg",
        "total_patients_hosp_confirmed_influenza_and_covid_7d_avg",
    ]

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
