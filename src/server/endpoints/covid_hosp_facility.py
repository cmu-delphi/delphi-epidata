from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("covid_hosp_facility", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("hospital_pks", "collection_weeks")
    hospital_pks = extract_strings("hospital_pks")
    collection_weeks = extract_integers("collection_weeks")
    publication_dates = extract_integers("publication_dates")

    # build query
    q = QueryBuilder("covid_hosp_facility", "c")

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
    q.set_fields(fields_string, fields_int, fields_float)

    # basic query info
    q.set_order("collection_week", "hospital_pk", "publication_date")

    # build the filter
    q.where_integers("collection_week", collection_weeks)
    q.where_strings("hospital_pk", hospital_pks)

    if publication_dates:
        # build the issue filter
        q.where_integers("publication_date", publication_dates)
    else:
        # final query using most recent issues
        condition = "x.max_publication_date = c.publication_date AND x.collection_week = c.collection_week AND x.hospital_pk = c.hospital_pk"
        q.subquery = f"JOIN (SELECT max(publication_date) max_publication_date, collection_week, hospital_pk FROM {q.table} WHERE {q.conditions_clause} GROUP BY collection_week, hospital_pk) x ON {condition}"
        q.condition = []  # since used for join

    # send query
    return execute_query(str(q), q.params, fields_string, fields_int, fields_float)
