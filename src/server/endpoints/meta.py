from flask import request, Blueprint

from sqlalchemy import text
from .._common import app, db
from .._config import AUTH
from .._exceptions import UnAuthenticatedException
from .._validate import require_all, extract_strings, extract_integers
from .._query import filter_strings, execute_query, parse_result
from .._printer import print_non_standard
from .fluview_meta import meta_fluview

# first argument is the endpoint name
bp = Blueprint("meta", __name__)
alias = None


def meta_api(seconds: int):
    query = "SELECT count(1) `num_hits`, count(distinct `ip`) `unique_ips`, sum(`num_rows`) `rows_returned` FROM `api_analytics` WHERE `datetime` >= date_sub(now(), interval {$seconds} second)"
    fields_int = ["num_hits", "unique_ips", "rows_returned"]

    return parse_result(query, {}, None, fields_int, None)


def meta_twitter():
    query = "SELECT x.`date` `latest_update`, x.`table_rows`, count(distinct t.`state`) `num_states` FROM (SELECT max(`date`) `date`, count(1) `table_rows` FROM `twitter`) x JOIN `twitter` t ON t.`date` = x.`date`"
    fields_string = ["latest_update"]
    fields_int = ["num_states", "table_rows"]
    return parse_result(query, {}, fields_string, fields_int, None)


def meta_wiki():
    # $query = 'SELECT date_sub(max(`datetime`), interval 5 hour) `latest_update`, count(1) `table_rows` FROM `wiki_meta`' // GMT to EST
    query = (
        "SELECT max(`datetime`) `latest_update`, count(1) `table_rows` FROM `wiki_meta`"
    )
    fields_string = ["latest_update"]
    fields_int = ["table_rows"]
    return parse_result(query, {}, fields_string, fields_int, None)


def meta_delphi():
    query = "SELECT `system`, min(`epiweek`) `first_week`, max(`epiweek`) `last_week`, count(1) `num_weeks` FROM `forecasts` GROUP BY `system` ORDER BY `system` ASC"
    fields_string = ["system"]
    fields_int = ["first_week", "last_week", "num_weeks"]
    return parse_result(query, {}, fields_string, fields_int, None)


@bp.route("/", methods=("GET", "POST"))
def handle():
    # query and return metadata
    # collect individual meta data results using collectors
    fluview = meta_fluview()
    twitter = meta_twitter()
    wiki = meta_wiki()
    delphi = meta_delphi()

    row = {
        "_api": {
            "minute": meta_api(60),
            "hour": meta_api(60 * 60),
            "day": meta_api(60 * 60 * 24),
            "week": meta_api(60 * 60 * 24 * 7),
            "month": meta_api(60 * 60 * 24 * 30),
        },
        "fluview": fluview,
        "twitter": twitter,
        "wiki": wiki,
        "delphi": delphi,
    }
    return print_non_standard([row])
