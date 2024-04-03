import os
from flask import Flask, render_template, request
from . import db_conn
from .models import user_datastore
from flask_security import Security


def create_app(test_config=None):
    # Create and configure app
    app = Flask(__name__, instance_relative_config=True)
    configure_app(app, test_config)
    Security(app, user_datastore)
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

    return app

# Flask app configuration
def configure_app(app, test_config):
    app.config.from_mapping(
        SECRET_KEY= os.getenv('SECRET_KEY'),
        SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT'),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, os.getenv('LOCAL_DATABASE_URI'))}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        app.config.from_pyfile(
            "config.py", silent=True
        )  # Silent=True står för att den inte gör någon felhantering om filen inte finns
    else:
        app.config.update(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
