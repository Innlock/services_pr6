from models import Service, User, Message, Ticket
from init import db, app
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash

services_data1 = [
    ["Услуги администрирования", "Обработка",
     "Обработка шаблонов и исходных файлов.Управление контентом и редактирование." +
     "Техническая поддержка и решение проблем.",
     '''Это  комплексное решение для управления контентом и редактирования информации. 
     Мы обеспечиваем эффективное управление вашей информационной системой, облегчая процессы работы 
     с цифровыми данными и поддерживая бесперебойную деятельность вашего бизнеса.''',
     "10000 руб", "business"],
    ["Услуги администрирования", "Хранение",
     "Обработка и хранение шаблонов и исходных файлов.Мониторинг и резервное копирование данных." +
     "Техническая поддержка и решение проблем.", '''Наши услуги хранения предоставляют вам безопасное 
     и надежное хранилище для ваших важных данных и ресурсов. Мы гарантируем конфиденциальность и 
     доступность ваших информационных активов, обеспечивая их сохранность и доступность при необходимости.''',
     "10000 руб", "business"],
    ["Услуги создания", "Дизайн",
     "Создание уникальных веб-дизайнов.Разработка адаптивных и мобильных версий.",
     '''Мы предоставляем профессиональный дизайн, который подчеркнет уникальность вашего бренда 
     и привлечет внимание вашей целевой аудитории.''',
     "5000 руб", "business"],
    ["Услуги создания", "Разработка",
     "Верстка и программирование сайтов.Разработка адаптивных и мобильных версий.",
     '''Наши услуги разработки предоставляют комплексное решение для создания и улучшения 
     вашего веб-приложения. Мы гарантируем высокое качество, соблюдение сроков и индивидуальный подход, 
     чтобы ваш проект соответствовал вашим потребностям и ожиданиям.''',
     "7000 руб", "business"],
    ["Услуги создания", "Проектирование",
     "Анализ требований и концептуальное проектирование.Разработка информационной архитектуры." +
     "Создание прототипов и макетов интерфейса.", '''Наши услуги проектирования предоставляют вам 
     экспертную помощь в разработке инновационных и функциональных концепций для ваших проектов.''',
     "15000 руб", "business"]
]
services_data2 = [
    # Добавить сюда Компоненты
    ["Услуги администрирования", "Обработка", "Компоненты?", "technical"],
    ["Услуги администрирования", "Хранение", "Компоненты?", "technical"],
    ["Услуги создания", "Дизайн", "Компоненты?", "technical"],
    ["Услуги создания", "Разработка", "Компоненты?", "technical"],
    ["Услуги создания", "Проектирование", "Компоненты?", "technical"],
]
users = [
    ["user1", "123", "employee"],
    ["user2", "123", "employee"],
    ["user3", "123", "employee"],
    ["support1", "123", "support"],
    ["support2", "123", "support"],
    ["support3", "123", "support"]
]
tickets = [
    ['Помогите', 1, 'user123@com', 'проблема не во мне', 1],
    ['Помогите2', 2, 'user123@com', 'проблема не во мне 2', 1]
]


def drop_all_tables():
    with app.app_context():
        db.reflect()
        db.drop_all()


def fill_services():
    for service_name in services_data1:
        service = Service(group_name=service_name[0], name=service_name[1], composition=service_name[2],
                          description=service_name[3], cost=service_name[4], type=service_name[5])
        db.session.add(service)
    for service_name in services_data2:
        service = Service(group_name=service_name[0], name=service_name[1], composition=service_name[2],
                          type=service_name[3])
        db.session.add(service)
    db.session.commit()


def fill_users():
    for user in users:
        new_user = User(username=user[0], password=generate_password_hash(user[1], salt_length=8), role=user[2])
        db.session.add(new_user)
    db.session.commit()


def fill_tickets():
    for ticket in tickets:
        new_ticket = Ticket(theme=ticket[0], service_id=ticket[1], user_data=ticket[2],
                            description=ticket[3], creator_id=ticket[4])
        db.session.add(new_ticket)
        db.session.commit()


fill_tables = False
with app.app_context():
    drop_all_tables()
    # проверить, существует ли таблица и выставить флаг, если нет
    inspector = inspect(db.engine)
    if "user" not in inspector.get_table_names() or "service" not in inspector.get_table_names():
        fill_tables = True

    # создать таблицы
    db.create_all()

    # заполнить таблицы, если они только созданы
    if fill_tables:
        fill_services()
        fill_users()
        fill_tickets()
