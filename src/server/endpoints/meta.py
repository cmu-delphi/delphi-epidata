from flask import Blueprint, request

from .._printer import print_non_standard
from .._query import parse_result
from .fluview_meta import meta_fluview

# first argument is the endpoint name
bp = Blueprint("meta", __name__)
alias = None


def meta_twitter():
    query = "SELECT x.`date` `latest_update`, x.`table_rows`, count(distinct t.`state`) `num_states` FROM (SELECT max(`date`) `date`, count(1) `table_rows` FROM `twitter`) x JOIN `twitter` t ON t.`date` = x.`date` GROUP BY x.`date`, x.`table_rows`"
    fields_string = ["latest_update"]
    fields_int = ["num_states", "table_rows"]
    return parse_result(query, {}, fields_string, fields_int, None)


def meta_wiki():
    # $query = 'SELECT date_sub(max(`datetime`), interval 5 hour) `latest_update`, count(1) `table_rows` FROM `wiki_meta`' // GMT to EST
    query = "SELECT max(`datetime`) `latest_update`, count(1) `table_rows` FROM `wiki_meta`"
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
        "fluview": fluview,
        "twitter": twitter,
        "wiki": wiki,
        "delphi": delphi,
    }
    return print_non_standard(request.values.get("format"), [row])
