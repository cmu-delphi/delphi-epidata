from pathlib import Path
from os import environ
from typing import Set
from flask import Blueprint, render_template_string, request
from werkzeug.exceptions import Unauthorized, NotFound
from werkzeug.utils import redirect
from .._security import resolve_auth_token, DBUser


ADMIN_PASSWORD = environ.get('API_KEY_ADMIN_PASSWORD')

self_dir = Path(__file__).parent
# first argument is the endpoint name
bp = Blueprint("admin", __name__)

templates_dir = Path(__file__).parent / 'templates'

def _require_admin():
    token = resolve_auth_token()
    if token is None or token != ADMIN_PASSWORD:
        raise Unauthorized()
    return token

def _parse_roles(roles: str) -> Set[str]:
    parsed: Set[str] = set()
    for role in roles.split('\n'):
        role = role.strip()
        if role:
            parsed.add(role)
    return parsed

def _render(mode: str, token: str, **kwargs):
    template = (templates_dir / 'index.html').read_text('utf8')
    return render_template_string(template, mode=mode, token=token, **kwargs)


@bp.route('/', methods=['GET', 'POST'])
def _index():
    token = _require_admin()
    if request.method == 'POST':
        # register a new user
        DBUser.insert(request.values['email'], request.values['api_key'], _parse_roles(request.values['roles']))

    users = DBUser.list()
    return _render('overview', token, users=users)


@bp.route('/<int:user_id>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def _detail(user_id: int):
    token = _require_admin()
    user = DBUser.find(user_id)
    print(request.values.to_dict(), flush=True)
    if not user:
        raise NotFound()
    if request.method == 'DELETE' or 'delete' in request.values:
        user.delete()
        return redirect(f"./?auth={token}")
    if request.method == 'PUT' or request.method == 'POST':
        user = user.update(request.values['email'], request.values['api_key'], _parse_roles(request.values['roles']))
    return _render('detail', token, user=user)
