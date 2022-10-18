from pathlib import Path
from os import environ
from typing import List, Set
from flask import Blueprint, render_template_string, request
from werkzeug.exceptions import Unauthorized, NotFound
from werkzeug.utils import redirect
from .._security import resolve_auth_token, DBUser, UserRole


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

def _parse_roles(roles: List[str]) -> Set[str]:
    return set(sorted(roles))

def _render(mode: str, token: str, **kwargs):
    template = (templates_dir / 'index.html').read_text('utf8')
    return render_template_string(template, mode=mode, token=token, roles=[r.value for r in UserRole], **kwargs)


@bp.route('/', methods=['GET', 'POST'])
def _index():
    token = _require_admin()
    if request.method == 'POST':
        # register a new user
        DBUser.insert(request.values['email'], request.values['api_key'], _parse_roles(request.values.getlist('roles')))

    users = DBUser.list()
    return _render('overview', token, users=users, user=dict())


@bp.route('/<int:user_id>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def _detail(user_id: int):
    token = _require_admin()
    user = DBUser.find(user_id)
    if not user:
        raise NotFound()
    if request.method == 'DELETE' or 'delete' in request.values:
        user.delete()
        return redirect(f"./?auth={token}")
    if request.method == 'PUT' or request.method == 'POST':
        user = user.update(request.values['email'], request.values['api_key'], _parse_roles(request.values.getlist('roles')))
    return _render('detail', token, user=user)
