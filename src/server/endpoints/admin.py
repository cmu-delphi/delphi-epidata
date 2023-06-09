from pathlib import Path
from typing import Dict, List, Set

from flask import Blueprint, make_response, render_template_string, request
from werkzeug.exceptions import NotFound, Unauthorized
from werkzeug.utils import redirect

from .._common import log_info_with_request
from .._config import ADMIN_PASSWORD, API_KEY_REGISTRATION_FORM_LINK, API_KEY_REMOVAL_REQUEST_LINK, REGISTER_WEBHOOK_TOKEN
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


def _parse_roles(roles: List[str]) -> Set[str]:
    return set(roles)


def _render(mode: str, token: str, flags: Dict, **kwargs):
    template = (templates_dir / "index.html").read_text("utf8")
    return render_template_string(
        template, mode=mode, token=token, flags=flags, roles=UserRole.list_all_roles(), **kwargs
    )


def user_exists(user_email: str = None, api_key: str = None):
    user = User.find_user(user_email=user_email, api_key=api_key)
    return True if user else False


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
    if request.method == "POST":
        # register a new user
        if not user_exists(user_email=request.values["email"], api_key=request.values["api_key"]):
            User.create_user(
                request.values["api_key"],
                request.values["email"],
                _parse_roles(request.values.getlist("roles")),
            )
            flags["banner"] = "Successfully Added"
        else:
            flags["banner"] = "User with such email and/or api key already exists."
    users = [user.as_dict for user in User.list_users()]
    return _render("overview", token, flags, users=users, user=dict())


@bp.route("/<int:user_id>", methods=["GET", "PUT", "POST", "DELETE"])
def _detail(user_id: int):
    token = _require_admin()
    user = User.find_user(user_id=user_id)
    if not user:
        raise NotFound()
    if request.method == "DELETE" or "delete" in request.values:
        User.delete_user(user.id)
        return redirect(f"./?auth={token}")
    flags = dict()
    if request.method in ["PUT", "POST"]:
        user_check = User.find_user(api_key=request.values["api_key"], user_email=request.values["email"])
        if user_check and user_check.id != user.id:
            flags["banner"] = "Could not update user; same api_key and/or email already exists."
        else:
            user = user.update_user(
                user=user,
                api_key=request.values["api_key"],
                email=request.values["email"],
                roles=_parse_roles(request.values.getlist("roles")),
            )
            flags["banner"] = "Successfully Saved"
    return _render("detail", token, flags, user=user.as_dict)


@bp.route("/register", methods=["POST"])
def _register():
    body = request.get_json()
    token = body.get("token")
    if token is None or token != REGISTER_WEBHOOK_TOKEN:
        raise Unauthorized()

    user_api_key = body["user_api_key"]
    user_email = body["user_email"]
    if user_exists(user_email=user_email, api_key=user_api_key):
        return make_response(
            "User with email and/or API Key already exists, use different parameters or contact us for help",
            409,
        )
    User.create_user(api_key=user_api_key, email=user_email)
    return make_response(f"Successfully registered API key '{user_api_key}'", 200)


@bp.route("/diagnostics", methods=["GET", "PUT", "POST", "DELETE"])
def diags():
    # allows us to get useful diagnostic information written into server logs,
    # such as a full current "X-Forwarded-For" path as inserted into headers by intermediate proxies...
    # (but only when initiated purposefully by us to keep junk out of the logs)
    _require_admin()
    log_info_with_request("diagnostics", headers=request.headers)
    response_text = f"request path: {request.headers.get('X-Forwarded-For', 'idk')}"
    return make_response(response_text, 200, {'content-type': 'text/plain'})
