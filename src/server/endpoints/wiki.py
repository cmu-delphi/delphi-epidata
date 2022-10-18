from flask import Blueprint, request

from .._query import execute_query, filter_dates, filter_integers, filter_strings
from .._validate import extract_integers, extract_strings, require_all, require_any

# first argument is the endpoint name
bp = Blueprint("wiki", __name__)
required_role = None
alias = None


@bp.route("/", methods=("GET", "POST"))
def handle():
    require_all("articles")
    require_any("dates", "epiweeks")

    articles = extract_strings("articles")
    language = request.values.get("language", "en")
    if "dates" in request.values:
        resolution = "daily"
        dates = extract_integers("dates")
    else:
        resolution = "weekly"
        dates = extract_integers("epiweeks")
    hours = extract_integers("hours")

    # build query
    params = dict()
    # in a few rare instances (~6 total), `total` is unreasonably high; something glitched somewhere, just ignore it
    table = "`wiki` w JOIN (SELECT * FROM `wiki_meta` WHERE `total` < 100000000) m ON m.`datetime` = w.`datetime`"
    # We select rows by language and then the problem is converted to the original one, and the rest of code can be same
    table = "( SELECT * FROM `wiki` WHERE `language` = :language ) w JOIN (SELECT * FROM `wiki_meta` WHERE `total` < 100000000 AND `language` = :language ) m ON m.`datetime` = w.`datetime`"
    params["language"] = language

    fields_string = ["article"]
    fields_int = ["count", "total", "hour"]
    fields_float = ["value"]

    if resolution == "daily":
        date_field = "m.`date`"
        date_name = "date"
        condition_date = filter_dates(date_field, dates, "date", params)
        fields_string.append(date_name)
    else:
        date_field = "m.`epiweek`"
        date_name = "epiweek"
        condition_date = filter_integers(date_field, dates, "date", params)
        fields_int.append(date_name)

    fields = f"{date_field} `{date_name}`, w.`article`, sum(w.`count`) `count`, sum(m.`total`) `total`, round(sum(w.`count`) / (sum(m.`total`) * 1e-6), 8) `value`"
    # build the article filter
    condition_article = filter_strings("w.`article`", articles, "article", params)
    if hours:
        # filter by specific hours
        condition_hour = filter_integers("hour(m.`datetime`)", hours, "hour", params)
        # final query, only taking counts from specific hours of the day
        query = f"SELECT {fields}, hour(m.`datetime`) `hour` FROM {table} WHERE ({condition_date}) AND ({condition_article}) AND ({condition_hour}) GROUP BY {date_field}, w.`article`, hour(m.`datetime`) ORDER BY {date_field} ASC, w.`article` ASC, hour(m.`datetime`) ASC"
    else:
        # final query, summing over all hours of the day
        query = f"SELECT {fields}, -1 `hour` FROM {table} WHERE ({condition_date}) AND ({condition_article}) GROUP BY {date_field}, w.`article` ORDER BY {date_field} ASC, w.`article` ASC"

    # send query
    return execute_query(query, params, fields_string, fields_int, fields_float)
