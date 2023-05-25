from sqlalchemy.ext.declarative import declaritive_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite://')
