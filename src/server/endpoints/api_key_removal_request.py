from datetime import datetime
from flask import Blueprint, render_template, request

from .._common import send_email, send_slack_notification
from .._config import SLACK_WEBHOOK_URL
from .._db import WriteSession
from ..admin.models import RemovalRequest, User

bp = Blueprint("removal_request", __name__)
alias = None


REMOVAL_REQUEST_MESSAGE = """
Your API Key: {}, removal request will be processed soon.
To verify, we will send you an email message after processing your request.
Best,
Delphi Team
"""


def generate_api_key_removal_notification(email: str, comment: str):
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "New request", "emoji": True},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*Type:*\nAPI Key deletion."},
                    {"type": "mrkdwn", "text": "*Created by:*\n{}".format(email)},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*Comment:*\n{}".format(comment)},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*Timestamp:*\n{}".format(datetime.now())},
                ],
            },
        ]
    }
    return payload


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
            if SLACK_WEBHOOK_URL:
                slack_message = generate_api_key_removal_notification(user.email, comment)
                send_slack_notification(slack_message)
            flags["banner"] = "Your request has been successfully recorded."
            send_email(user.email, "API Key removal request", REMOVAL_REQUEST_MESSAGE.format(api_key))
    return render_template("removal_request.html", flags=flags)
