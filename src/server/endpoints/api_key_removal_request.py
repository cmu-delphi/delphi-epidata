from flask import Blueprint, render_template, request

from .._common import send_email
from .._db import WriteSession
from ..admin.models import RemovalRequest, User

bp = Blueprint("removal_request", __name__, template_folder="/app/delphi/epidata/server/templates", static_url_path="")
alias = None


REMOVAL_REQUEST_MESSAGE = """
Your API Key: {}, removal request will be processed soon.
To verify, we will send you an email message after processing your request.
Best,
Delphi Team
"""


@bp.route("/", methods=["GET", "POST"])
def handle():
    flags = dict()
    with WriteSession() as session:
        if request.method == "POST":
            api_key = request.values["api_key"]
            comment = request.values.get("comment")
            user = User.find_user(api_key=api_key)
            # User.delete_user(user.id, session)
            RemovalRequest.add_request(api_key, comment, session)
            flags["banner"] = "Your request has been successfully recorded."
            send_email(user.email, "API Key removal request", REMOVAL_REQUEST_MESSAGE.format(api_key))
    return render_template("removal_request.html", flags=flags)
