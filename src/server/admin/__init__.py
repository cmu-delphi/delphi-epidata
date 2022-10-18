from pathlib import Path
from os import environ
from typing import Dict, List, Set
from flask import Blueprint, render_template_string, request, make_response
from werkzeug.exceptions import Unauthorized, NotFound
from werkzeug.utils import redirect
from requests import post
from .._security import resolve_auth_token, DBUser, UserRole


ADMIN_PASSWORD = environ.get('API_KEY_ADMIN_PASSWORD')
REGISTER_WEBHOOK_TOKEN = environ.get('API_KEY_REGISTER_WEBHOOK_TOKEN')

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

def _render(mode: str, token: str, flags: Dict, **kwargs):
    template = (templates_dir / 'index.html').read_text('utf8')
    return render_template_string(template, mode=mode, token=token, flags=flags, roles=[r.value for r in UserRole], **kwargs)


@bp.route('/', methods=['GET', 'POST'])
def _index():
    token = _require_admin()
    flags = dict()
    if request.method == 'POST':
        # register a new user
        DBUser.insert(request.values['api_key'], _parse_roles(request.values.getlist('roles')), request.values.get('tracking') == 'True')
        flags['banner'] = 'Successfully Added'

    users = DBUser.list()
    return _render('overview', token, flags, users=users, user=dict())


@bp.route('/<int:user_id>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def _detail(user_id: int):
    token = _require_admin()
    user = DBUser.find(user_id)
    if not user:
        raise NotFound()
    if request.method == 'DELETE' or 'delete' in request.values:
        user.delete()
        return redirect(f"./?auth={token}")
    flags = dict()
    if request.method == 'PUT' or request.method == 'POST':
        user = user.update(request.values['api_key'], _parse_roles(request.values.getlist('roles')), request.values.get('tracking') == 'True')
        flags['banner'] = 'Successfully Saved'
    return _render('detail', token, flags, user=user)


def _send_mail(sender: str, receiver: str, subject: str, body: str) -> bool:
    # send via mail gun
    auth = ('api', environ.get('MAILGUN_KEY'))
    data = {
        'from': sender,
        'to': receiver,
        'subject': subject,
        'text': body
    }
    try:
        r = post('https://api.mailgun.net/v2/epicast.net/messages', auth=auth, data=data)
        return (r.status_code == 200) and (r.json()['message'] == 'Queued. Thank you.')
    except Exception:
        return False


@bp.route('/register', methods=['POST'])
def _register():
    body = request.get_json()
    token = body.get('token')
    if token is None or token != REGISTER_WEBHOOK_TOKEN:
        raise Unauthorized()

    api_key = body['api_key']
    roles: Set[str] = set()
    tracking = False
    for k,v in body.items():
        # find the record question
        if 'record' in k.lower():
            tracking = 'yes' in v.lower()
            break
    DBUser.insert(api_key, roles, tracking)

    # email = body['email']
    # TODO handle mailing list registration handling
    # TODO send mails here or in the google script?
    return make_response('ok', 200)
