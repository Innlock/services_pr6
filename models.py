from init import db
from flask_login import UserMixin

# Связь диалогов и сообщений
dialog_participants = db.Table('dialog_participants',
                               db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                               db.Column('dialog_id', db.Integer, db.ForeignKey('dialog.id'))
                               )


# Диалоги
class Dialog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participants = db.relationship('User', secondary=dialog_participants, back_populates='dialogs')
    messages = db.relationship('Message', backref='dialog', lazy='dynamic')


# Таблица для сообщений
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dialog_id = db.Column(db.Integer, db.ForeignKey('dialog.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


# Таблица для услуг
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    composition = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    cost = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String, nullable=False, default="business")


# Таблица для заявок
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.String(20), nullable=False, default="medium")  # medium/high
    theme = db.Column(db.String(100), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    user_data = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="new")  # new/in process/done
    description = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    service = db.relationship('Service', backref='tickets')


# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Роли: 'client', 'employee', 'support'
    dialogs = db.relationship('Dialog', secondary=dialog_participants, back_populates='participants')
    tickets = db.relationship('Ticket', backref='creator', lazy='dynamic')
