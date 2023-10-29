from init import db
from flask_login import UserMixin


# Таблица для сообщений
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)


# Таблица для услуг
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    composition = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    cost = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String, nullable=False, default="business")


# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Роли: 'client', 'employee', 'support'
