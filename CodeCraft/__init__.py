import datetime
import os
import secrets
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    session,
)
from . import db_conn
from .models import user_datastore, Employee, User, db
from .employees import get_paginated_employees, get_employee_pictures
from flask_security import (
    Security,
    hash_password,
    login_required,
    logout_user,
    roles_required,
    uia_username_mapper,
)
import flask_babel


def create_app(test_config=None):
    # Create and configure app
    app = Flask(__name__, instance_relative_config=True)
    configure_app(app, test_config)
    security = Security(app, user_datastore)
    db_conn.init_app(app)

    flask_babel.Babel(app)

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/employees")
    def employees():
        search_query = request.args.get("query")
        page = request.args.get("page", 1, type=int)
        per_page = 30
        pagination, employees_data = get_paginated_employees(
            page, per_page, search_query
        )

        for page_num in pagination.iter_pages():
            print(page_num)

        return render_template(
            "employees.html", pagination=pagination, employees=employees_data
        )

    @app.route("/employees/<int:employee_id>")
    def employee_page(employee_id):
        if employee_id:
            employee = Employee.query.filter_by(id=employee_id).first()
            images = get_employee_pictures()

            if employee:
                return render_template(
                    "employee.html",
                    employee=employee,
                    employee_image=images[employee_id]["large"],
                )

            else:
                return render_template("404_page.html"), 404
        else:
            return "Employee id not provided", 400

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                flash('Username already exists')
            else:
                hashed_password = hash_password(password)
                fs_uniquifier = secrets.token_urlsafe(32)  # Generate a unique string
                new_user = user_datastore.create_user(
                    username=username,
                    password=hashed_password,
                    fs_uniquifier=fs_uniquifier,  # Provide the generated uniquifier
                    confirmed_at=datetime.datetime.now(),
                )
                db.session.commit()
                flash(f"Welcome to CodeCraft! Please login to continue.")
                return redirect(url_for("security.login"))

        return render_template("register.html")
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    @app.route("/admin")
    @roles_required("Admin")
    def admin():
        return render_template("admin.html")
    
    @app.route("/logout")
    def logout():
        logout_user()
        flash("You have been logged out successfully.", "success")
        return render_template("loading.html")

    return app


# Flask app configuration
def configure_app(app, test_config):
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SECURITY_PASSWORD_SALT=os.getenv("SECURITY_PASSWORD_SALT"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, os.getenv('LOCAL_DATABASE_URI'))}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECURITY_LOGOUT_URL="/logout",
        SECURITY_LOGIN_USER_TEMPLATE="login.html",
        SECURITY_POST_LOGIN_VIEW="/dashboard",
        SECURITY_UNAUTHORIZED_VIEW="404_page.html",
        SECURITY_USER_IDENTITY_ATTRIBUTES=[
            {
                "username": {
                    "mapper": uia_username_mapper,
                    "case_insensitive": True,
                }
            }
        ],
        SECURITY_USERNAME_ENABLE=True,
    )
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
