import json
from pathlib import Path
import socket
from typing import Dict, List, Set

from flask import Blueprint, make_response, render_template_string, request
from werkzeug.exceptions import NotFound, Unauthorized
from werkzeug.utils import redirect

from .._common import db, log_info_with_request
from .._config import ADMIN_PASSWORD, API_KEY_REGISTRATION_FORM_LINK, API_KEY_REMOVAL_REQUEST_LINK, REGISTER_WEBHOOK_TOKEN
from .._db import WriteSession
from .._security import resolve_auth_token
from ..admin.models import User, UserRole

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


def _render(mode: str, token: str, flags: Dict, session, **kwargs):
    template = (templates_dir / "index.html").read_text("utf8")
    return render_template_string(
        template, mode=mode, token=token, flags=flags, roles=UserRole.list_all_roles(session), **kwargs
    )


# ~~~~ PUBLIC ROUTES ~~~~


@bp.route("/registration_form", methods=["GET"])
def registration_form_redirect():
    # TODO: replace this with our own hosted registration form instead of external
    return redirect(API_KEY_REGISTRATION_FORM_LINK, code=302)


@bp.route("/removal_request", methods=["GET"])
def removal_request_redirect():
    # TODO: replace this with our own hosted form instead of external
    return redirect(API_KEY_REMOVAL_REQUEST_LINK, code=302)


# ~~~~ PRIVLEGED ROUTES ~~~~


@bp.route("/", methods=["GET", "POST"])
def _index():
    token = _require_admin()
    flags = dict()
    with WriteSession() as session:
        if request.method == "POST":
            # register a new user
            if not User.find_user(
                    user_email=request.values["email"], api_key=request.values["api_key"],
                    session=session):
                User.create_user(
                    api_key=request.values["api_key"],
                    email=request.values["email"],
                    user_roles=set(request.values.getlist("roles")),
                    session=session
                )
                flags["banner"] = "Successfully Added"
            else:
                flags["banner"] = "User with such email and/or api key already exists."
        users = [user.as_dict for user in session.query(User).all()]
        return _render("overview", token, flags, session=session, users=users, user=dict())


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
            user_check = User.find_user(api_key=request.values["api_key"], user_email=request.values["email"], session=session)
            if user_check and user_check.id != user.id:
                flags["banner"] = "Could not update user; same api_key and/or email already exists."
            else:
                user = User.update_user(
                    user=user,
                    api_key=request.values["api_key"],
                    email=request.values["email"],
                    roles=set(request.values.getlist("roles")),
                    session=session
                )
                flags["banner"] = "Successfully Saved"
        return _render("detail", token, flags, session=session, user=user.as_dict)


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

    try:
        serving_host = socket.gethostbyname_ex(socket.gethostname())
    except e:
        serving_host = e

    try:
        db_host = db.execute('SELECT @@hostname AS hn').fetchone()['hn']
    except e:
        db_host = e

    log_info_with_request("diagnostics", headers=request.headers, serving_host=serving_host, database_host=db_host)

    response_data = {
        'request_path': request.headers.get('X-Forwarded-For', 'idfk'),
        'serving_host': serving_host,
        'database_host': db_host,
    }
    return make_response(json.dumps(response_data), 200, {'content-type': 'text/plain'})
