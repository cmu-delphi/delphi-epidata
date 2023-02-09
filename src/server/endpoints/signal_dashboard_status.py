from flask import Blueprint, request

from .signal_dashboard_coverage import fetch_coverage_data
from .._query import parse_row, run_query
from .._printer import create_printer
from .._exceptions import DatabaseErrorException

# first argument is the endpoint name
bp = Blueprint("signal_dashboard_status", __name__)
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    fields_string = ["name", "source", "covidcast_signal", "latest_issue", "latest_time_value"]
    fields_int = []
    fields_float = []

    query = """
    SELECT enabled_signal.`name`,
        enabled_signal.`source`,
        enabled_signal.`covidcast_signal`,
        status.`latest_issue`,
        status.`latest_time_value`
    FROM (SELECT `id`, `name`, `source`, `covidcast_signal`, `latest_status_update`
        FROM `dashboard_signal`
        WHERE `enabled`) AS enabled_signal
    LEFT JOIN `dashboard_signal_status` AS status
    ON enabled_signal.`latest_status_update` = status.`date`
    AND enabled_signal.`id` = status.`signal_id`
    """

    p = create_printer(request.values.get("format"))

    def gen(rows, coverage_data):
        for row in rows:
            parsed = parse_row(row, fields_string, fields_int, fields_float)
            # inject coverage data
            parsed["coverage"] = coverage_data.get(parsed["name"], {})
            yield parsed

    try:
        coverage_data = fetch_coverage_data()
        r = run_query(p, (query, {}))
    except Exception as e:
        raise DatabaseErrorException(str(e))

    # now use a generator for sending the rows and execute all the other queries
    return p(gen(r, coverage_data))
