from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_integer, extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("signal_dashboard_coverage", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    fields_string = ["name", "date", "geo_type"]
    fields_int = ["count"]
    fields_float = []

    query = """
    SELECT enabled_signal.`name`,
        coverage.`date`,
        coverage.`geo_type`,
        coverage.`count`
    FROM (SELECT `id`, `name`, `latest_coverage_update`
        FROM `dashboard_signal`
        WHERE `enabled`) AS enabled_signal
    LEFT JOIN `dashboard_signal_coverage` AS coverage
    ON enabled_signal.`latest_coverage_update` = coverage.`date`
    """

    # send query
    return execute_query(query, {}, fields_string, fields_int, fields_float)
