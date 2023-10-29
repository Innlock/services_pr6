from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from database import drop_all_tables
from models import User, Service, Message
from init import app, db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Роут для главной страницы
@app.route('/')
def index():
    return redirect(url_for('login'))


# Роут для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'employee'

        # Проверка наличия пользователя с таким именем
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Пользователь с таким именем уже существует."

        # Создание нового пользователя
        new_user = User(username=username, password=generate_password_hash(password, salt_length=8), role=role)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('dashboard'))

    return render_template('register.html')


# Роут для входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')


# Роут для выхода
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('dashboard'))


# Роут для панели управления
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'client':
        return "Панель управления клиента"
    elif current_user.role == 'employee':
        return "Панель управления рядового сотрудника"
    elif current_user.role == 'support':
        return "Панель управления сотрудника технической поддержки"


# Роут для страницы сообщений
@app.route('/messenger')
@login_required
def messenger():
    if current_user.role == 'client':
        return "У вас нет доступа к этой странице"
    return render_template('messenger.html', username=current_user.username)


# Роут для страницы услуг
@app.route('/services')
def services():
    serv_technical = Service.query.filter(Service.type == 'technical').all()
    serv_business = Service.query.filter(Service.type == 'business').all()
    for serv in serv_business:
        composition = serv.composition.replace(".", ".\n")
        serv.composition = composition
    username = "Клиент"
    if current_user.is_authenticated:
        username = current_user.username
    return render_template('services.html', services_technical=serv_technical,
                           services_business=serv_business, username=username)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
