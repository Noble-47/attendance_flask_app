from flask import Flask

import os

parent_dir = os.path.dirname(os.getcwd())

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = "dev",
        DATABASE = os.path.join(parent_dir, 'attendance.sqlite')
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
    from attendance import db
    
    db.init_app(app)


    return app

