from pathlib import Path
from os import environ
from flask import Blueprint, render_template_string
from werkzeug.exceptions import Unauthorized
from .._security import resolve_auth_token, list_users


ADMIN_PASSWORD = environ.get('API_KEY_ADMIN_PASSWORD')

self_dir = Path(__file__).parent
# first argument is the endpoint name
bp = Blueprint("admin", __name__)

templates_dir = Path(__file__).parent / 'templates'

def _require_admin():
    token = resolve_auth_token()
    if token is None or token != ADMIN_PASSWORD:
        raise Unauthorized

@bp.route('/')
def _index():
    _require_admin()
    users = list_users()
    return render_template_string((templates_dir / 'index.html').read_text('utf8'), users=users)
