from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5433/services'
app.config['SECRET_KEY'] = 'services'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
