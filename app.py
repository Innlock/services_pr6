from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/services'
app.config['SECRET_KEY'] = 'services_pr6'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Роли: 'client', 'employee', 'support'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

    # Таблица для сообщений


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)


# Таблица для услуг
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)


# Роут для главной страницы
@app.route('/')
def index():
    return "Добро пожаловать на главную страницу!"


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
        new_user = User(username=username, password=generate_password_hash(password), role=role)
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
    return redirect(url_for('index'))


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
    if current_user.role == 'support':
        return "Страница сообщений для сотрудника технической поддержки"
    return "У вас нет доступа к этой странице"


# Роут для страницы услуг
@app.route('/services')
@login_required
def services():
    if current_user.role != 'client':
        return "У вас нет доступа к этой странице"
    # Здесь вы можете извлечь данные о услугах из базы данных и передать их в шаблон
    return "Страница услуг для клиента"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
