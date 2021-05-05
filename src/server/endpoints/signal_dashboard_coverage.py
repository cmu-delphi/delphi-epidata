from typing import List, Dict, Any
from flask import Blueprint

from .._query import parse_result, filter_fields
from .._printer import print_non_standard

# first argument is the endpoint name
bp = Blueprint("signal_dashboard_coverage", __name__)
alias = None

def fetch_coverage_data() -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    fields_string = ["name", "date", "geo_type"]
    fields_int = ["count"]
    fields_float: List[str] = []

    query = """
    SELECT enabled_signal.`name`,
        coverage.`date`,
        coverage.`geo_type`,
        coverage.`count`
    FROM (SELECT `id`, `name`, `latest_coverage_update`
        FROM `dashboard_signal`
        WHERE `enabled`) AS enabled_signal
    LEFT JOIN `dashboard_signal_coverage` AS coverage
    ON enabled_signal.`id` = coverage.`signal_id`
    ORDER BY `id` ASC, `date` DESC
    """

    rows = parse_result(query, {}, fields_string, fields_int, fields_float)

    grouped: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for row in rows:
        name = row['name']
        geo_type = row['geo_type']
        timedata = {'date': row['date'], 'count': row['count'] }
        name_entry = grouped.setdefault(name, {})
        geo_type_entry = name_entry.setdefault(geo_type, [])
        geo_type_entry.append(timedata)

    return grouped


@bp.route("/", methods=("GET", "POST"))
def handle():
    return print_non_standard(fetch_coverage_data())
