from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH
from .._validate import require_all, extract_strings, extract_integers
from .._query import filter_strings, execute_query, filter_integers

# first argument is the endpoint name
bp = Blueprint("covid_hosp_state_timeseries", __name__)
alias = "covid_hosp"


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("states", "dates")
    states = extract_strings("states")
    dates = extract_integers("dates")
    issues = extract_integers("issues")

    # build query
    table = "`covid_hosp_state_timeseries` c"
    fields = ", ".join(
        [
            "c.`issue`",
            "c.`state`",
            "c.`date`",
            "c.`hospital_onset_covid`",
            "c.`hospital_onset_covid_coverage`",
            "c.`inpatient_beds`",
            "c.`inpatient_beds_coverage`",
            "c.`inpatient_beds_used`",
            "c.`inpatient_beds_used_coverage`",
            "c.`inpatient_beds_used_covid`",
            "c.`inpatient_beds_used_covid_coverage`",
            "c.`previous_day_admission_adult_covid_confirmed`",
            "c.`previous_day_admission_adult_covid_confirmed_coverage`",
            "c.`previous_day_admission_adult_covid_suspected`",
            "c.`previous_day_admission_adult_covid_suspected_coverage`",
            "c.`previous_day_admission_pediatric_covid_confirmed`",
            "c.`previous_day_admission_pediatric_covid_confirmed_coverage`",
            "c.`previous_day_admission_pediatric_covid_suspected`",
            "c.`previous_day_admission_pediatric_covid_suspected_coverage`",
            "c.`staffed_adult_icu_bed_occupancy`",
            "c.`staffed_adult_icu_bed_occupancy_coverage`",
            "c.`staffed_icu_adult_patients_confirmed_suspected_covid`",
            "c.`staffed_icu_adult_patients_confirmed_suspected_covid_coverage`",
            "c.`staffed_icu_adult_patients_confirmed_covid`",
            "c.`staffed_icu_adult_patients_confirmed_covid_coverage`",
            "c.`total_adult_patients_hosp_confirmed_suspected_covid`",
            "c.`total_adult_patients_hosp_confirmed_suspected_covid_coverage`",
            "c.`total_adult_patients_hosp_confirmed_covid`",
            "c.`total_adult_patients_hosp_confirmed_covid_coverage`",
            "c.`total_pediatric_patients_hosp_confirmed_suspected_covid`",
            "c.`total_pediatric_patients_hosp_confirmed_suspected_covid_coverage`",
            "c.`total_pediatric_patients_hosp_confirmed_covid`",
            "c.`total_pediatric_patients_hosp_confirmed_covid_coverage`",
            "c.`total_staffed_adult_icu_beds`",
            "c.`total_staffed_adult_icu_beds_coverage`",
            "c.`inpatient_beds_utilization`",
            "c.`inpatient_beds_utilization_coverage`",
            "c.`inpatient_beds_utilization_numerator`",
            "c.`inpatient_beds_utilization_denominator`",
            "c.`percent_of_inpatients_with_covid`",
            "c.`percent_of_inpatients_with_covid_coverage`",
            "c.`percent_of_inpatients_with_covid_numerator`",
            "c.`percent_of_inpatients_with_covid_denominator`",
            "c.`inpatient_bed_covid_utilization`",
            "c.`inpatient_bed_covid_utilization_coverage`",
            "c.`inpatient_bed_covid_utilization_numerator`",
            "c.`inpatient_bed_covid_utilization_denominator`",
            "c.`adult_icu_bed_covid_utilization`",
            "c.`adult_icu_bed_covid_utilization_coverage`",
            "c.`adult_icu_bed_covid_utilization_numerator`",
            "c.`adult_icu_bed_covid_utilization_denominator`",
            "c.`adult_icu_bed_utilization`",
            "c.`adult_icu_bed_utilization_coverage`",
            "c.`adult_icu_bed_utilization_numerator`",
            "c.`adult_icu_bed_utilization_denominator`",
        ]
    )
    # basic query info
    order = "c.`date` ASC, c.`state` ASC, c.`issue` ASC"
    params = dict()
    # build the filter
    # build the date filter
    condition_date = filter_integers("c.`date`", dates, "date", params)
    # build the state filter
    condition_state = filter_strings("c.`state`", states, "state", params)
    if issues:
        # build the issue filter
        condition_issue = filter_integers("c.`issue`", issues, "issue", params)
        # final query using specific issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_date}) AND ({condition_state}) AND ({condition_issue}) ORDER BY {order}"
    else:
        # final query using most recent issues
        subquery = f"(SELECT max(`issue`) `max_issue`, `date`, `state` FROM {table} WHERE ({condition_date}) AND ({condition_state}) GROUP BY `date`, `state`) x"
        condition = "x.`max_issue` = c.`issue` AND x.`date` = c.`date` AND x.`state` = c.`state`"
        query = f"SELECT {fields} FROM {table} JOIN {subquery} ON {condition} ORDER BY {order}"

    # get the data from the database
    fields_string = ["state"]
    fields_int = [
        "issue",
        "date",
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
    ]
    fields_float = [
        "inpatient_beds_utilization",
        "percent_of_inpatients_with_covid",
        "inpatient_bed_covid_utilization",
        "adult_icu_bed_covid_utilization",
        "adult_icu_bed_utilization",
    ]

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
