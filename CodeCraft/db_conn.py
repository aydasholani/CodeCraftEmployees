import click
from flask import g
from .models import db, seed_data

def get_db():
    if not hasattr(g, "db"):
        g.db = db.engine.connect()
    return g.db

# Stänger databasconnection efter varje request
def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()
        
# Initierar databasen
@click.command("init-db")
def init_db():
    db.drop_all()
    db.create_all()
    seed_data() 
    db.session.commit()
    print("Database initialization successful.")

def init_app(app):
    db.init_app(app)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)