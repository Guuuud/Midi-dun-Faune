from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask import Flask, redirect, render_template, request, session, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "Database.db"
FLASK_APP = '__init__.py'

FLASKY_ADMIN = 'sc19hcs@leeds'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'SD'
    app.config['ADMIN'] = 'sc19hcs@leeds'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .view import view
    from .auth import auth
    app.register_blueprint(view, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .database import User
    create_db(app)
    login_manager = LoginManager()

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app


def create_db(app):
    if not path.exists("CW2/" + DB_NAME):
        db.create_all(app=app)
