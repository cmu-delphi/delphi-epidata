import random
import string
from datetime import datetime

from flask import Blueprint, render_template, request

from .._common import send_email, send_slack_notification, verify_recaptcha_response
from .._config import SLACK_WEBHOOK_URL
from .._db import WriteSession
from ..admin.models import RegistrationResponse, User
from .._config import RECAPTCHA_SITE_KEY

# first argument is the endpoint name
bp = Blueprint("registration_form", __name__)
alias = None

NEW_KEY_MESSAGE = """
Thank you for registering with the Delphi Epidata API.
Your API key is: {}
For usage information, see the API Keys section of the documentation: https://cmu-delphi.github.io/delphi-epidata/api/api_keys.html
Best,
Delphi Team
"""


def generate_registration_notification(email: str, organization: str, purpose: str):
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "New request", "emoji": True},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*Type:*\nNew registration."},
                    {"type": "mrkdwn", "text": "*Created by:*\n{}".format(email)},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*Organization:*\n{}".format(organization)},
                    {"type": "mrkdwn", "text": "*Purpose:*\n{}".format(purpose)},
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
            email = request.values["email"]
            organization = request.values["organization"]
            purpose = request.values["purpose"]
            verified = verify_recaptcha_response(request.values["g-recaptcha-response"])
            if verified:
                if not User.find_user(user_email=email):
                    # Use a separate table for email, purpose, organization
                    api_key = "".join(
                        random.choices(string.ascii_letters + string.digits, k=13)
                    )
                    user = User.create_user(api_key=api_key, email=email, session=session)
                    RegistrationResponse.add_response(
                        email=email,
                        organization=request.values["organization"],
                        purpose=request.values["purpose"],
                        session=session,
                    )
                    send_email(
                        to_addr=email,
                        subject="Delphi API Key Registration",
                        message=NEW_KEY_MESSAGE.format(api_key),
                    )
                    if SLACK_WEBHOOK_URL:
                        slack_message = generate_registration_notification(email, organization, purpose)
                        send_slack_notification(slack_message)
                    flags["banner"] = "Successfully sent"

                else:
                    flags[
                        "error"
                    ] = "User with such email already exists. Please try another email address or contact us."
            else:
                flags[
                        "error"
                    ] = "Captcha was not submitted. Please try again."
    return render_template(
        "registration.html", flags=flags, recaptcha_key=RECAPTCHA_SITE_KEY
    )
