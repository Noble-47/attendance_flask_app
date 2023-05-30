from flask import Flask

import os

from . import settings 

def create_app(test_config=None):
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = "dev",
        DATABASE = settings.DATABASE
    )

    # Get configurations
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure instance path exists if not, create it
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return "Hello, World!"
    
    from . import register
    from . import admin
    from . import auth
    from . import db
   
    db.init_app(app)
    app.register_blueprint(register.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)

    return app


