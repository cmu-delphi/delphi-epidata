from flask import Blueprint

from .._query import execute_query, QueryBuilder
from .._validate import extract_integer, extract_integers, extract_strings, require_all

# first argument is the endpoint name
bp = Blueprint("signal_dashboard_status", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    fields_string = ["name", "latest_issue", "latest_time_value"]
    fields_int = []
    fields_float = []

    query = """
    SELECT enabled_signal.`name`,
        status.`latest_issue`,
        status.`latest_time_value`
    FROM (SELECT `id`, `name`, `latest_status_update`
        FROM `dashboard_signal`
        WHERE `enabled`) AS enabled_signal
    LEFT JOIN `dashboard_signal_status` AS status
    ON enabled_signal.`latest_status_update` = status.`date`
    """

    # send query
    return execute_query(query, {}, fields_string, fields_int, fields_float)
