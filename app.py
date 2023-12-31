from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired
from datetime import datetime

from database import drop_all_tables
from models import User, Service, Message, Dialog, dialog_participants, Ticket
from init import app, db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Роут для главной страницы
@app.route('/')
def index():
    return redirect('/service_desk')


def user_exists(username):
    # Проверка наличия пользователя с таким именем
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return "Пользователь с таким именем уже существует."
    return False


def create_user(username, password):
    # Создание нового пользователя
    role = 'employee'
    new_user = User(username=username, password=generate_password_hash(password, salt_length=8), role=role)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)


# Роут для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_exists(username)
        if user:
            return user
        create_user(username, password)
        return redirect('/service_desk')
    return render_template('register.html')


def log(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return user
    return False


# Роут для входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if log(username, password):
            return redirect(url_for('services'))
    return render_template('login.html')


# Роут для выхода
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('service_desk'))


# Роут для панели управления
@app.route('/service_desk', methods=['GET', 'POST'])
def service_desk():
    username = get_username()
    serv = []
    if current_user.is_authenticated and current_user.role == 'support':
        # Отображение всех заявок для пользователей с ролью 'support'
        tickets = Ticket.query.join(Ticket.service).all()
    else:
        # Пользователи с ролью 'client' и 'employee'
        if request.method == 'POST':
            # Создание новой заявки
            priority = 'medium'
            type = request.form.get('type')
            theme = request.form.get('theme')
            service_id = request.form.get('service')
            user_data = request.form.get('user_data')
            description = request.form.get('description')

            if not priority or not theme or not service_id or not user_data or not description:
                flash('Заполните все поля!')
            else:
                creator = None
                if current_user.is_authenticated:
                    creator = current_user
                new_ticket = Ticket(priority=priority, theme=theme, service_id=service_id,
                                    user_data=user_data, description=description, creator=creator,
                                    type=type, date=datetime.now())
                db.session.add(new_ticket)
                db.session.commit()
                return 'Заявка успешно создана!'

        # Отображение созданных заявок для пользователей с ролью 'employee'
        tickets = []
        type_serv = 'business'
        if current_user.is_authenticated:
            type_serv = 'technical'
            tickets = current_user.creator_tickets.all()
        serv = Service.query.filter(Service.type == type_serv).all()
    return render_template('service_desk.html', tickets=tickets, services=serv, username=username)


@app.route('/update_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def update_ticket(ticket_id):
    if current_user.role != 'support':
        flash('У вас нет разрешения для изменения заявок!')
        return redirect(url_for('service_desk'))

    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        flash('Заявка не найдена!')
        return redirect(url_for('service_desk'))

    # Обновите статус заявки (в работе/выполнена)
    new_status = request.form.get('status')
    new_priority = request.form.get('priority')
    if new_status and new_status in ('new', 'process', 'done') or new_priority:
        ticket.status = new_status
        ticket.priority = new_priority
        db.session.commit()
        flash('Заявка обновлена!')
    if 'assign' in request.form:
        if current_user.role == 'support':
            ticket.accountable = current_user.id
            db.session.commit()
        else:
            flash('Вы не можете назначить себя ответственным.')

    return redirect(url_for('service_desk'))


@app.route('/service_desk/<int:ticket_id>')
@login_required
def ticket_description(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        flash('Заявка не найдена!')
        return redirect(url_for('service_desk'))
    return render_template('ticket_description.html', ticket=ticket)


# Роут для страницы сообщений
@app.route('/messenger')
@app.route('/messenger/<int:dialog_id>')
@login_required
def messenger(dialog_id=None):
    if not current_user.is_authenticated:
        return "У вас нет доступа к этой странице"
    user_dialogs_id = Dialog.query.filter(Dialog.participants.any(id=current_user.id)).all()
    for i in range(len(user_dialogs_id)):
        user_dialogs_id[i] = user_dialogs_id[i].id
    user_dialogs = (User.query
                    .join(dialog_participants)
                    .filter(dialog_participants.c.user_id == User.id)
                    .filter(User.id != current_user.id)
                    .filter(dialog_participants.c.dialog_id.in_(user_dialogs_id))
                    .with_entities(User.username, dialog_participants.c.dialog_id)
                    .all())
    print(user_dialogs)

    all_users = User.query.all()
    return render_template('messenger.html', username=current_user.username, user_dialogs=user_dialogs,
                           all_users=all_users, dialog_id=dialog_id)


@app.route('/get_messages', methods=['POST'])
@login_required
def get_messages():
    dialog_id = request.form.get('dialog_id')
    messages = Message.query.filter_by(dialog_id=dialog_id).all()
    participant = (User.query
                   .join(dialog_participants)
                   .filter(dialog_participants.c.dialog_id == dialog_id)
                   .filter(User.id != current_user.id)
                   .first())
    dialog_recipient_id = participant.id
    message_list = [
        {'sender_id': message.sender_id, 'content': message.content} for message in messages]
    return jsonify({'dialog_recipient_id': dialog_recipient_id, 'message_list': message_list})


@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    recipient_id = request.form.get('recipient_id')
    message_content = request.form.get('message')

    # Проверяем, существует ли диалог между текущим пользователем и получателем
    dialog = Dialog.query.filter(
        (Dialog.participants.any(id=current_user.id)) & (Dialog.participants.any(id=recipient_id))
    ).first()

    if not dialog:
        # Если диалога нет, создаем новый
        dialog = Dialog()
        dialog.participants.append(current_user)
        dialog.participants.append(User.query.get(recipient_id))
        db.session.add(dialog)
        db.session.commit()

    # Отправляем сообщение в диалог
    message = Message(sender_id=current_user.id, recipient_id=recipient_id, dialog_id=dialog.id,
                      content=message_content)
    db.session.add(message)
    db.session.commit()

    return redirect('/messenger/' + str(dialog.id))


def get_username():
    username = "client"
    if current_user.is_authenticated:
        username = current_user.username
    return username


def get_serv():
    serv_technical = Service.query.filter(Service.type == 'technical').all()
    serv_business = Service.query.filter(Service.type == 'business').all()
    for serv in serv_business:
        composition = serv.composition.replace(".", ".\n")
        serv.composition = composition
    return serv_technical, serv_business


# Роут для страницы услуг
@app.route('/services')
def services():
    username = get_username()
    serv_technical, serv_business = get_serv()
    return render_template('services.html', services_technical=serv_technical,
                           services_business=serv_business, username=username)


class ServiceForm(FlaskForm):
    group_name = StringField('Название группы', validators=[InputRequired()])
    name = StringField('Название услуги', validators=[InputRequired()])
    composition = TextAreaField('Состав услуги')
    description = TextAreaField('Описание услуги')
    cost = StringField('Цена услуги')


# Добавление услуги
@app.route('/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            group_name=form.group_name.data,
            name=form.name.data,
            composition=form.composition.data,
            description=form.description.data,
            cost=form.cost.data
        )
        db.session.add(service)
        db.session.commit()
        flash('Услуга добавлена успешно', 'success')
        return redirect(url_for('services'))
    return render_template('add_service.html', form=form)


# Редактирование услуги
@app.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        form.populate_obj(service)
        db.session.commit()
        flash('Услуга отредактирована успешно', 'success')
        return redirect(url_for('services'))
    return render_template('edit_service.html', form=form, service=service)


# Удаление услуги
@app.route('/delete_service/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Услуга удалена успешно', 'success')
    return redirect(url_for('services'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
