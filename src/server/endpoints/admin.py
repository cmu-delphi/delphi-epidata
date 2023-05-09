from pathlib import Path
from typing import Dict, List, Set

from flask import Blueprint, make_response, render_template_string, request
from werkzeug.exceptions import NotFound, Unauthorized
from werkzeug.utils import redirect

from .._config import ADMIN_PASSWORD, REGISTER_WEBHOOK_TOKEN
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
            flags["banner"] = "User with such email/api key already exists."
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
    if request.method == "PUT" or request.method == "POST":
        user_check = User.find_user(api_key=request.values["api_key"], user_email=request.values["email"])
        if user_check and user_check.id != user.id:
            flags[
                "banner"
            ] = "Could not update the user because of api_key/email conflict. User with the same api_key/email already exists."
        else:
            user = user.update_user(
                user=user,
                api_key=request.values["api_key"],
                email=request.values["email"],
                roles=_parse_roles(request.values.getlist("roles")),
            )
            flags["banner"] = "Successfully Saved"
    return _render("detail", token, flags, user=user.as_dict)


def register_new_key(api_key: str, email: str) -> str:
    User.create_user(api_key=api_key, email=email)
    return api_key


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
            "User with such email or API Key already exists, try to use different email or contact us to resolve this issue",
            409,
        )
    api_key = register_new_key(user_api_key, user_email)
    return make_response(f"Successfully registered the API key '{api_key}' and removed rate limit", 200)
