from sqlalchemy import extract
from flask import Flask, g
from redis import Redis

from datetime import datetime
import os

from . import settings 

def create_app(test_config=None):
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = "dev",
        DATABASE = settings.DATABASE,
    )

    # Get configurations
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # setup redis client
    app.config["REDIS_HOST"] = settings.REDIS_HOST
    app.config["REDIS_PORT"] = settings.REDIS_PORT
    app.config["REDIS_DB"] = settings.REDIS_DB
      
    # attach redis_client to app
    app.redis = Redis(
            host = settings.REDIS_HOST,
            port = settings.REDIS_PORT,
            db = settings.REDIS_DB
    )
    app.redis.set('app-init', 'hello world')
    @app.route('/hello')
    def hello():
        return "Hello, World!"
    
    # app initializers 
    from . import commands
    from . import db
   
    db.init_app(app)
    commands.init_app(app)
    
    from . import register
    from . import admin    
    from . import auth

    app.register_blueprint(register.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    
    from .models import Event
    from .db import db_session

    # setup current event if any
    @app.before_request
    def setup_event():
        # check if event exists
        # check if event is today
        t = datetime.now()
        if g.get('event') is not None:
            # if current event is of previous day
            # close current event
            if g.event.date.month < t.month or g.event.day != t.day:
                g.event.close()
                db_session.add(g.event)
                db_session.commit()

        # if no event
        # or event is closed
        # check if any event for today exists that is not closed
        if g.get('event') is None or g.event.closed == True:    
            event = Event.query.filter(
                    extract('day', Event.date) == t.day,
                    extract('month', Event.date) == t.month,
                    extract('year', Event.date) == t.year,
                    Event.closed == False
                ).first()
            g.event = event  # returns None or Event object


    return app

