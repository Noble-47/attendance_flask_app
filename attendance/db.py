from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, exists
import click

db_path = ""
engine = create_engine('sqlite://{db_path}')
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

class Base(DeclarativeBase):
    query = db_session.query_property()


def init_db():
    import attendance.models
    Base.metadata.create_all(bind=engine)


@click.command('init-db')
def init_db_command():
    """Clear existing data and create new tables"""
    if os.path.exists(db_file_path):
        print("This will delete all existing data at {os.path.basename(db_file_path}.")
        option = input("Are you sure you want to proceed? [Y/N]: ")
        if option.lower() in ['n', 'no']:
            return
        elif option.lower() in ['y', 'yes']:
            click.echo("Initializing database...")
            init-db()
            click.echo("Initialized database")
        else:
            raise ValueError(f"Unexpected value: {option}. Expected Y or N")

def init_app(app):
    # clean up db session after handling request
    app.teardowncontext(db_session.remove())
    app.cli.add_command(init_db_command)
