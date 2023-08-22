from datetime import timedelta

from flask import session, request, redirect, url_for, render_template
import flask_login
from flask_admin import Admin, AdminIndexView, expose, BaseView
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

login_manager = flask_login.LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


def _require_admin():
    token = resolve_auth_token()
    if token is None or token != ADMIN_PASSWORD:
        raise Unauthorized()
    return token


class AdminUser(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(admin_token):
    if admin_token != ADMIN_PASSWORD:
        return

    user = AdminUser()
    user.id = admin_token
    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return "Unauthorized", 401


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        admin_token = request.form["admin_token"]
        if admin_token == ADMIN_PASSWORD:
            user = AdminUser()
            user.id = admin_token
            flask_login.login_user(user)
            return redirect(url_for("admin.index"))
    return render_template("login.html")


class AuthModelView(ModelView):
    @flask_login.login_required
    def is_accessible(self):
        return True


@app.before_first_request  # runs before FIRST request (only once)
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


class AuthAdminIndexView(AdminIndexView):
    """
    Admin view main page
    """

    @expose("/")
    @flask_login.login_required
    def index(self):
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


class LogoutView(BaseView):
    @expose("/")
    @flask_login.login_required
    def logout(self):
        flask_login.logout_user()
        return redirect(url_for("login"))


# init admin view, default endpoint is /admin
admin = Admin(app, name="EpiData admin", template_mode="bootstrap4", index_view=AuthAdminIndexView())
# database session
admin_session = WriteSession()

# add views
admin.add_view(UserView(User, admin_session))
admin.add_view(UserRoleView(UserRole, admin_session))
admin.add_view(LogoutView(name="Logout", endpoint="logout"))


@app.teardown_request
def teardown_request(*args, **kwargs):
    """
    Remove the session after each request.
    That is used to protect from dirty read.
    """
    admin_session.close()
