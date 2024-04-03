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
    @app.route("/about")
    def about():
        text = "At CodeCraft, we are dedicated to crafting cutting-edge solutions that push the boundaries of technology. Founded with a passion for innovation, our team of dynamic developers, designers, and visionaries are committed to transforming ideas into reality. Our mission is simple: to empower businesses and individuals alike with transformative digital experiences. Whether it's developing sleek and intuitive websites, building robust mobile applications, or harnessing the power of AI to drive efficiency, we strive for excellence in every project we undertake. Driven by creativity and fueled by curiosity, we believe in the power of collaboration and continuous learning. By staying at the forefront of emerging technologies and industry trends, we ensure that our clients always receive solutions that are not just ahead of the curve, but also tailored to their unique needs and aspirations. At CodeCraft, innovation isn't just a buzzword – it's our ethos. Join us on our journey as we pave the way for a brighter digital future, one line of code at a time."
        return render_template("about.html", text=text)
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
    
