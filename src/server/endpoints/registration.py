import random
import string

from flask import Blueprint, render_template, request

from .._common import send_email
from .._db import WriteSession
from ..admin.models import RegistrationResponse, User

# first argument is the endpoint name
bp = Blueprint("registration_form", __name__, template_folder="/app/delphi/epidata/server/templates", static_url_path="")
alias = None

NEW_KEY_MESSAGE = """
Thank you for registering with the Delphi Epidata API.
Your API key is: {}
For usage information, see the API Keys section of the documentation: https://cmu-delphi.github.io/delphi-epidata/api/api_keys.html
Best,
Delphi Team
"""


@bp.route("/", methods=["GET", "POST"])
def handle():
    flags = dict()
    with WriteSession() as session:
        if request.method == "POST":
            email = request.values["email"]
            if not User.find_user(user_email=email):
                # Use a separate table for email, purpose, organization
                api_key = "".join(random.choices(string.ascii_letters + string.digits, k=13))
                user = User.create_user(api_key=api_key, email=email, session=session)
                RegistrationResponse.add_response(
                    email=email,
                    organization=request.values["organization"],
                    purpose=request.values["purpose"],
                    session=session,
                )
                send_email(
                    to_addr=email, subject="Delphi API Key Registration", message=NEW_KEY_MESSAGE.format(api_key)
                )
                flags["banner"] = "Successfully sent"
            else:
                flags["error"] = "User with such email already exists. Please try another email address or contact us."
    return render_template("registration.html", flags=flags)
