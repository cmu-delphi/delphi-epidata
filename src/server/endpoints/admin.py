from datetime import timedelta
from functools import wraps

from flask import session
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.exceptions import Unauthorized

from .._common import app
from .._config import ADMIN_PASSWORD
from .._db import WriteSession
from .._security import resolve_auth_token
from ..admin.models import User, UserRole

# set optional bootswatch theme
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
# set app secret key to enable session
app.secret_key = "SOME_RANDOM_SECRET_KEY"


def require_auth(func):
    @wraps(func)
    def check_token(*args, **kwargs):
        # Check to see if it's in user's session
        if "admin_auth_token" not in session:
            raise Unauthorized()
        return func(*args, **kwargs)

    return check_token


def require_admin():
    token = resolve_auth_token()
    if token is None or token != ADMIN_PASSWORD:
        if "admin_auth_token" not in session:
            raise Unauthorized()
    session["admin_auth_token"] = token


class AuthModelView(ModelView):
    @require_auth
    def is_accessible(self):
        return True


@app.before_first_request  # runs before FIRST request (only once)
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


class AuthAdminIndexView(AdminIndexView):
    """
    Admin view main page
        require_admin() is used for authentication using one of key words("auth", "api_key", "token") with ADMIN_PASSWORD
    """

    @expose("/")
    def index(self):
        require_admin()
        return super().index()


class UserView(AuthModelView):
    """
    User model view:
        -   form_columns: list of columns that will be available in CRUD forms
        -   column_list: list of columns that are displayed on user model view page
        -   column_filters: list of available filters
        -   page_size: number of items on page
    """

    form_columns = ["api_key", "email", "roles"]
    column_list = ("api_key", "email", "created", "last_time_used", "roles")
    column_filters = ("api_key", "email")

    page_size = 10


class UserRoleView(AuthModelView):
    """
    User role view:
        -   colums_filters: list of available filters
        -   page_size: number of items on page
    """

    column_filters = ["name"]

    page_size = 10


# init admin view, default endpoint is /admin
admin = Admin(app, name="EpiData admin", template_mode="bootstrap4", index_view=AuthAdminIndexView())
# database session
admin_session = WriteSession()

# add views
admin.add_view(UserView(User, admin_session))
admin.add_view(UserRoleView(UserRole, admin_session))


@app.teardown_request
def teardown_request(*args, **kwargs):
    """
    Remove the session after each request.
    That is used to protect from dirty read.
    """
    admin_session.close()
