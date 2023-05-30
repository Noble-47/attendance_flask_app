from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, exists
from flask import current_app
import click

import os

from . import settings

db_path = settings.DATABASE
engine = create_engine(f"sqlite:///{db_path}")
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

class Base(DeclarativeBase):
    query = db_session.query_property()

def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)


@click.command('init-db')
def init_db_command():
    """Clear existing data and create new tables"""
    if os.path.exists(db_path):
        print("This will delete all existing data at {os.path.basename(db_path}.")
        option = input("Are you sure you want to proceed? [Y/N]: ")
        if option.lower() in ['n', 'no']:
            return
        elif option.lower() in ['y', 'yes']:
            click.echo("Initializing database...")
            init_db()
            click.echo("Initialized database")
        else:
            raise ValueError(f"Unexpected value: {option}. Expected Y or N")
    else:
        click.echo("Initializing database")
        init_db()
        click.echo("Initialzed database")


def shutdown_session(exception=None):
    db_session.remove()

def init_app(app):
    # clean up db session after handling request
    app.teardown_appcontext(shutdown_session)
    app.cli.add_command(init_db_command)
