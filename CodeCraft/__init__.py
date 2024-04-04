import datetime
import os
import re
from flask import Flask, flash, redirect, render_template, request, url_for
from . import db_conn
from .models import user_datastore, Employee, User, db
from .employees import get_paginated_employees, get_employee_pictures
from flask_security import Security, hash_password
from flask_login import login_user, current_user, logout_user, login_required
from flask_login import LoginManager


def create_app(test_config=None):
    # Create and configure app
    app = Flask(__name__, instance_relative_config=True)
    configure_app(app, test_config)
    security = Security(app, user_datastore)
    db_conn.init_app(app)

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
        text = "Welcome to CodeCraft – Where Innovation Meets Ingenuity!"
        return render_template("index.html", text=text)

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
    def register_user():
        errors = {}
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            existing_user = User.query.filter_by(username=username).first()

            if existing_user:
                errors['username'] = "Username already exists"
    
            elif not username or not password:
                if not username:
                    errors['username'] = "Please fill in username"
                if not password:
                    errors['password'] = "Please fill in password"

            else:
                codecraft_mail = username + '@codecraft.com'
                hashed_password = hash_password(password)
                user_role = user_datastore.find_or_create_role(name='User')
                new_user = user_datastore.create_user(email=codecraft_mail, username=username, password=hashed_password, roles=[user_role], confirmed_at=datetime.datetime.now())
                if new_user:
                    flash(f"Welcome to CodeCraft! Please login to continue.")
                    return redirect(url_for("login_user"))
        return render_template("register.html", errors=errors)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        errors = {}
        return render_template("login.html", errors=errors)

    @app.route("/logout", methods=["GET", "POST"])
    def logout_user():
        return render_template("logout.html")

    return app


# Flask app configuration
def configure_app(app, test_config):
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SECURITY_PASSWORD_SALT=os.getenv("SECURITY_PASSWORD_SALT"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, os.getenv('LOCAL_DATABASE_URI'))}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config is None:
        app.config.from_pyfile(
            "config.py", silent=True
        )  
    else:
        app.config.update(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
