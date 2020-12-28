from flask import jsonify, request, Blueprint

from sqlalchemy import select
from .._common import app, db
from .._config import AUTH
from .._validate import require_all, extract_strings, extract_ints

bp = Blueprint("flusurv", __name__)


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("epiweeks", "locations")

    epiweeks = extract_ints("epiweeks")
    locations = extract_strings("locations")
    issues = extract_ints("isues")
    lag = int(request.values["lag"]) if "lag" in request.values else None

    # basic query info
    table = "`flusurv` fs"
    fields = "fs.`release_date`, fs.`issue`, fs.`epiweek`, fs.`location`, fs.`lag`, fs.`rate_age_0`, fs.`rate_age_1`, fs.`rate_age_2`, fs.`rate_age_3`, fs.`rate_age_4`, fs.`rate_overall`"
    order = "fs.`epiweek` ASC, fs.`location` ASC, fs.`issue` ASC"
    # build the epiweek filter
    condition_epiweek = filter_integers("fs.`epiweek`", epiweeks)
    # build the location filter
    condition_location = filter_strings("fs.`location`", locations)
    if issues is not None:
        # build the issue filter
        condition_issue = filter_integers("fs.`issue`", issues)
        # final query using specific issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_location}) AND ({condition_issue}) ORDER BY {order}"
    elif lag is not None:
        # build the lag filter
        condition_lag = f"(fs.`lag` = {lag})"
        # final query using lagged issues
        query = f"SELECT {fields} FROM {table} WHERE ({condition_epiweek}) AND ({condition_location}) AND ({condition_lag}) ORDER BY {order}"
    else:
        # final query using most recent issues
        subquery = f"(SELECT max(`issue`) `max_issue`, `epiweek`, `location` FROM {table} WHERE ({condition_epiweek}) AND ({condition_location}) GROUP BY `epiweek`, `location`) x"
        condition = f"x.`max_issue` = fs.`issue` AND x.`epiweek` = fs.`epiweek` AND x.`location` = fs.`location`"
        query = f"SELECT {fields} FROM {table} JOIN {subquery} ON {condition} ORDER BY {order}"

    # get the data from the database
    fields_string = ("release_date", "location")
    fields_int = ("issue", "epiweek", "lag")
    fields_float = (
        "rate_age_0",
        "rate_age_1",
        "rate_age_2",
        "rate_age_3",
        "rate_age_4",
        "rate_overall",
    )
    return execute_query(query, fields_string, fields_int, fields_float)
