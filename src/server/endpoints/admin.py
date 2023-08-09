from pathlib import Path
from typing import Dict

from flask import Blueprint, make_response, render_template_string, request
from werkzeug.exceptions import NotFound, Unauthorized
from werkzeug.utils import redirect
import random
import string

from .._common import log_info_with_request, send_email
from .._config import (
    ADMIN_PASSWORD,
    REGISTER_WEBHOOK_TOKEN,
)
from .._db import WriteSession
from .._security import resolve_auth_token
from ..admin.models import User, UserRole, RegistrationResponse, RemovalRequest

NEW_KEY_MESSAGE = """
Thank you for registering with the Delphi Epidata API.

Your API key is: {}

For usage information, see the API Keys section of the documentation: https://cmu-delphi.github.io/delphi-epidata/api/api_keys.html

Best,
Delphi Team
"""

REMOVAL_REQUEST_MESSAGE = """
Your API Key: {} removal request will be processed soon.
To verify, we will send you an email message after processing your request.

Best,
Delphi Team
"""

self_dir = Path(__file__).parent
# first argument is the endpoint name
bp = Blueprint("admin", __name__)

templates_dir = Path(__file__).parent.parent / "admin" / "templates"


def enable_admin() -> bool:
    # only enable admin endpoint if we have a password for it, so it is not exposed to the world
    return bool(ADMIN_PASSWORD)


def _require_admin():
    token = resolve_auth_token()
    if token is None or token != ADMIN_PASSWORD:
        raise Unauthorized()
    return token


def _render(template_name: str, mode: str, token: str, flags: Dict, **kwargs):
    template = (templates_dir / template_name).read_text("utf8")
    return render_template_string(template, mode=mode, token=token, flags=flags, **kwargs)


# ~~~~ PUBLIC ROUTES ~~~~


@bp.route("/registration_form", methods=["GET", "POST"])
def registration_form():
    flags = dict()
    with WriteSession() as session:
        if request.method == "POST":
            email = request.values["email"]
            if not User.find_user(user_email=email):
                # Use a separate table for email, purpose and organization
                api_key = "".join(random.choices(string.ascii_letters + string.digits, k=13))
                User.create_user(
                    api_key=api_key,
                    email=email,
                    session=session,
                )
                RegistrationResponse.add_response(
                    email, request.values["organization"], request.values["purpose"], session
                )
                send_email(email, "Delphi Epidata API Registration", NEW_KEY_MESSAGE.format(api_key))
                flags["banner"] = "Successfully Added"
            else:
                flags[
                    "error"
                ] = "User with email and/or API Key already exists, use different parameters or contact us for help"
    return _render("registration.html", "registration", None, flags=flags)


@bp.route("/removal_request", methods=["GET", "POST"])
def removal_request():
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
    return _render("removal_request.html", "removal_request", None, flags=flags)


# ~~~~ PRIVLEGED ROUTES ~~~~


@bp.route("/", methods=["GET", "POST"])
def _index():
    token = _require_admin()
    flags = dict()
    with WriteSession() as session:
        if request.method == "POST":
            # register a new user
            if not User.find_user(
                user_email=request.values["email"], api_key=request.values["api_key"], session=session
            ):
                User.create_user(
                    api_key=request.values["api_key"],
                    email=request.values["email"],
                    user_roles=set(request.values.getlist("roles")),
                    session=session,
                )
                flags["banner"] = "Successfully Added"
            else:
                flags["banner"] = "User with such email and/or api key already exists."
        users = [user.as_dict for user in session.query(User).all()]
        return _render(
            "index.html", "overview", token, flags, users=users, user=dict(), roles=UserRole.list_all_roles(session)
        )


@bp.route("/<int:user_id>", methods=["GET", "PUT", "POST", "DELETE"])
def _detail(user_id: int):
    token = _require_admin()
    with WriteSession() as session:
        user = User.find_user(user_id=user_id, session=session)
        if not user:
            raise NotFound()
        if request.method == "DELETE" or "delete" in request.values:
            User.delete_user(user.id, session=session)
            return redirect(f"./?auth={token}")
        flags = dict()
        if request.method in ["PUT", "POST"]:
            user_check = User.find_user(
                api_key=request.values["api_key"], user_email=request.values["email"], session=session
            )
            if user_check and user_check.id != user.id:
                flags["banner"] = "Could not update user; same api_key and/or email already exists."
            else:
                user = User.update_user(
                    user=user,
                    api_key=request.values["api_key"],
                    email=request.values["email"],
                    roles=set(request.values.getlist("roles")),
                    session=session,
                )
                flags["banner"] = "Successfully Saved"
        return _render("index.html", "detail", token, flags, user=user.as_dict, roles=UserRole.list_all_roles(session))


@bp.route("/register", methods=["POST"])
def _register():
    body = request.get_json()
    token = body.get("token")
    if token is None or token != REGISTER_WEBHOOK_TOKEN:
        raise Unauthorized()

    user_api_key = body["user_api_key"]
    user_email = body["user_email"]
    with WriteSession() as session:
        if User.find_user(user_email=user_email, api_key=user_api_key, session=session):
            return make_response(
                "User with email and/or API Key already exists, use different parameters or contact us for help",
                409,
            )
        User.create_user(api_key=user_api_key, email=user_email, session=session)
    return make_response(f"Successfully registered API key '{user_api_key}'", 200)


@bp.route("/diagnostics", methods=["GET", "PUT", "POST", "DELETE"])
def diags():
    # allows us to get useful diagnostic information written into server logs,
    # such as a full current "X-Forwarded-For" path as inserted into headers by intermediate proxies...
    # (but only when initiated purposefully by us to keep junk out of the logs)
    _require_admin()
    log_info_with_request("diagnostics", headers=request.headers)
    response_text = f"request path: {request.headers.get('X-Forwarded-For', 'idk')}"
    return make_response(response_text, 200, {"content-type": "text/plain"})
