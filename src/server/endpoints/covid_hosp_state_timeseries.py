from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_integers, extract_strings, extract_date, require_all

# first argument is the endpoint name
bp = Blueprint("covid_hosp_state_timeseries", __name__)
alias = "covid_hosp"


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("states", "dates")
    states = extract_strings("states")
    dates = extract_integers("dates")
    issues = extract_integers("issues")
    as_of = extract_date("as_of")

    # build query
    q = QueryBuilder("covid_hosp_state_timeseries", "c")

    fields_string = [
        "state",
        "geocoded_state"
    ]
    fields_int = [
        "issue",
        "date",
        "critical_staffing_shortage_today_yes",
        "critical_staffing_shortage_today_no",
        "critical_staffing_shortage_today_not_reported",
        "critical_staffing_shortage_anticipated_within_week_yes",
        "critical_staffing_shortage_anticipated_within_week_no",
        "critical_staffing_shortage_anticipated_within_week_not_reported",
        "hospital_onset_covid",
        "hospital_onset_covid_coverage",
        "inpatient_beds",
        "inpatient_beds_coverage",
        "inpatient_beds_used",
        "inpatient_beds_used_coverage",
        "inpatient_beds_used_covid",
        "inpatient_beds_used_covid_coverage",
        "previous_day_admission_adult_covid_confirmed",
        "previous_day_admission_adult_covid_confirmed_coverage",
        "previous_day_admission_adult_covid_suspected",
        "previous_day_admission_adult_covid_suspected_coverage",
        "previous_day_admission_pediatric_covid_confirmed",
        "previous_day_admission_pediatric_covid_confirmed_coverage",
        "previous_day_admission_pediatric_covid_suspected",
        "previous_day_admission_pediatric_covid_suspected_coverage",
        "staffed_adult_icu_bed_occupancy",
        "staffed_adult_icu_bed_occupancy_coverage",
        "staffed_icu_adult_patients_confirmed_suspected_covid",
        "staffed_icu_adult_patients_confirmed_suspected_covid_coverage",
        "staffed_icu_adult_patients_confirmed_covid",
        "staffed_icu_adult_patients_confirmed_covid_coverage",
        "total_adult_patients_hosp_confirmed_suspected_covid",
        "total_adult_patients_hosp_confirmed_suspected_covid_coverage",
        "total_adult_patients_hosp_confirmed_covid",
        "total_adult_patients_hosp_confirmed_covid_coverage",
        "total_pediatric_patients_hosp_confirmed_suspected_covid",
        "total_pediatric_patients_hosp_confirmed_suspected_covid_coverage",
        "total_pediatric_patients_hosp_confirmed_covid",
        "total_pediatric_patients_hosp_confirmed_covid_coverage",
        "total_staffed_adult_icu_beds",
        "total_staffed_adult_icu_beds_coverage",
        "inpatient_beds_utilization_coverage",
        "inpatient_beds_utilization_numerator",
        "inpatient_beds_utilization_denominator",
        "percent_of_inpatients_with_covid_coverage",
        "percent_of_inpatients_with_covid_numerator",
        "percent_of_inpatients_with_covid_denominator",
        "inpatient_bed_covid_utilization_coverage",
        "inpatient_bed_covid_utilization_numerator",
        "inpatient_bed_covid_utilization_denominator",
        "adult_icu_bed_covid_utilization_coverage",
        "adult_icu_bed_covid_utilization_numerator",
        "adult_icu_bed_covid_utilization_denominator",
        "adult_icu_bed_utilization_coverage",
        "adult_icu_bed_utilization_numerator",
        "adult_icu_bed_utilization_denominator",
        "deaths_covid",
        "deaths_covid_coverage",
        "icu_patients_confirmed_influenza",
        "icu_patients_confirmed_influenza_coverage",
        "on_hand_supply_therapeutic_a_casirivimab_imdevimab_courses",
        "on_hand_supply_therapeutic_b_bamlanivimab_courses",
        "on_hand_supply_therapeutic_c_bamlanivimab_etesevimab_courses",
        "previous_day_admission_adult_covid_confirmed_18_19",
        "previous_day_admission_adult_covid_confirmed_18_19_coverage",
        "previous_day_admission_adult_covid_confirmed_20_29",
        "previous_day_admission_adult_covid_confirmed_20_29_coverage",
        "previous_day_admission_adult_covid_confirmed_30_39",
        "previous_day_admission_adult_covid_confirmed_30_39_coverage",
        "previous_day_admission_adult_covid_confirmed_40_49",
        "previous_day_admission_adult_covid_confirmed_40_49_coverage",
        "previous_day_admission_adult_covid_confirmed_50_59",
        "previous_day_admission_adult_covid_confirmed_50_59_coverage",
        "previous_day_admission_adult_covid_confirmed_60_69",
        "previous_day_admission_adult_covid_confirmed_60_69_coverage",
        "previous_day_admission_adult_covid_confirmed_70_79",
        "previous_day_admission_adult_covid_confirmed_70_79_coverage",
        "previous_day_admission_adult_covid_confirmed_80plus",
        "previous_day_admission_adult_covid_confirmed_80plus_coverage",
        "previous_day_admission_adult_covid_confirmed_unknown",
        "previous_day_admission_adult_covid_confirmed_unknown_coverage",
        "previous_day_admission_adult_covid_suspected_18_19",
        "previous_day_admission_adult_covid_suspected_18_19_coverage",
        "previous_day_admission_adult_covid_suspected_20_29",
        "previous_day_admission_adult_covid_suspected_20_29_coverage",
        "previous_day_admission_adult_covid_suspected_30_39",
        "previous_day_admission_adult_covid_suspected_30_39_coverage",
        "previous_day_admission_adult_covid_suspected_40_49",
        "previous_day_admission_adult_covid_suspected_40_49_coverage",
        "previous_day_admission_adult_covid_suspected_50_59",
        "previous_day_admission_adult_covid_suspected_50_59_coverage",
        "previous_day_admission_adult_covid_suspected_60_69",
        "previous_day_admission_adult_covid_suspected_60_69_coverage",
        "previous_day_admission_adult_covid_suspected_70_79",
        "previous_day_admission_adult_covid_suspected_70_79_coverage",
        "previous_day_admission_adult_covid_suspected_80plus",
        "previous_day_admission_adult_covid_suspected_80plus_coverage",
        "previous_day_admission_adult_covid_suspected_unknown",
        "previous_day_admission_adult_covid_suspected_unknown_coverage",
        "previous_day_admission_influenza_confirmed",
        "previous_day_admission_influenza_confirmed_coverage",
        "previous_day_deaths_covid_and_influenza",
        "previous_day_deaths_covid_and_influenza_coverage",
        "previous_day_deaths_influenza",
        "previous_day_deaths_influenza_coverage",
        "previous_week_therapeutic_a_casirivimab_imdevimab_courses_used",
        "previous_week_therapeutic_b_bamlanivimab_courses_used",
        "previous_week_therapeutic_c_bamlanivimab_etesevimab_courses_used",
        "total_patients_hospitalized_confirmed_influenza",
        "total_patients_hospitalized_confirmed_influenza_coverage",
        "total_patients_hospitalized_confirmed_influenza_covid",
        "total_patients_hospitalized_confirmed_influenza_covid_coverage"
    ]
    fields_float = [
        "inpatient_beds_utilization",
        "percent_of_inpatients_with_covid",
        "inpatient_bed_covid_utilization",
        "adult_icu_bed_covid_utilization",
        "adult_icu_bed_utilization",
    ]

    q.set_fields(fields_string, fields_int, fields_float)
    q.set_order("date", "state", "issue")

    # build the filter
    q.where_integers("date", dates)
    q.where_strings("state", states)

    if issues is not None:
        q.where_integers("issue", issues)
        # final query using specific issues
        query = f"WITH c as (SELECT {q.fields_clause}, ROW_NUMBER() OVER (PARTITION BY date, state, issue ORDER BY record_type) `row` FROM {q.table} WHERE {q.conditions_clause}) SELECT {q.fields_clause} FROM {q.alias} WHERE `row` = 1 ORDER BY {q.order_clause}"
    elif as_of is not None:
        sub_condition_asof = "(issue <= :as_of)"
        q.params["as_of"] = as_of
        query = f"WITH c as (SELECT {q.fields_clause}, ROW_NUMBER() OVER (PARTITION BY date, state ORDER BY issue DESC, record_type) `row` FROM {q.table} WHERE {q.conditions_clause} AND {sub_condition_asof}) SELECT {q.fields_clause} FROM {q.alias} WHERE `row` = 1 ORDER BY {q.order_clause}"
    else:
        # final query using most recent issues
        subquery = f"(SELECT max(`issue`) `max_issue`, `date`, `state` FROM {q.table} WHERE {q.conditions_clause} GROUP BY `date`, `state`) x"
        condition = f"x.`max_issue` = {q.alias}.`issue` AND x.`date` = {q.alias}.`date` AND x.`state` = {q.alias}.`state`"
        query = f"WITH c as (SELECT {q.fields_clause}, ROW_NUMBER() OVER (PARTITION BY date, state, issue ORDER BY record_type) `row` FROM {q.table} JOIN {subquery} ON {condition}) select {q.fields_clause} FROM {q.alias} WHERE `row` = 1 ORDER BY {q.order_clause}"

    # send query
    return execute_query(query, q.params, fields_string, fields_int, fields_float)
