# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from logging import FileHandler, WARNING  # Error logging
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from blank.core.config import Config

# Handlers
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'user.signin'
login_manager.login_message_category = 'blue'

# Create an instance of the app


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Log errors to file (Only logs errors if debug mode is OFF)
    if not app.debug:
        error_file_handler = FileHandler(app.root_path + '/core/errorLog.txt')
        error_file_handler.setLevel(WARNING)
        app.logger.addHandler(error_file_handler)

    # Instantiate handlers
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import routes
    from blank.routes.errors.handlers import errors
    from blank.routes.links.routes import links
    from blank.routes.user.routes import user
    from blank.routes.routes import main
    # Register blueprints
    app.register_blueprint(errors)
    app.register_blueprint(links)
    app.register_blueprint(user)
    app.register_blueprint(main)
    return app
