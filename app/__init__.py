from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///budget.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints (will add these later)
    # from app.routes import main, auth
    # app.register_blueprint(main.bp)
    # app.register_blueprint(auth.bp)

    # Simple test route
    @app.route('/')
    def index():
        return '<h1>Budget App</h1><p>Docker container is running!</p>'

    @app.route('/health')
    def health():
        return {'status': 'healthy', 'database': 'connected'}

    return app
