from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import configure_uploads,patch_request_class
from app.main.forms import photos
from app.main.models import db
from app.config import Config


login_manager = LoginManager()



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    configure_uploads(app, photos)
    patch_request_class(app)

    login_manager.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)

    from .main.views import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app