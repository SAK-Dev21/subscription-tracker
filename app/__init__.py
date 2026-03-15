from flask import Flask
from config import Config
from app.extensions import db, bcrypt, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialise extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.subscriptions import subscriptions_bp
    from app.education import education_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(subscriptions_bp, url_prefix='/subscriptions')
    app.register_blueprint(education_bp, url_prefix='/education')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
