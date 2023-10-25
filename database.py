from models import Service, User, Message
from init import db, app
from sqlalchemy import inspect

services_data = [
    "обработка (услуги администрирования)",
    "хранение (услуги администрирования)",
    "дизайн (услуги создания)",
    "развитие (услуги создания)",
    "проектирование (услуги создания)"
]


def drop_all_tables():
    with app.app_context():
        db.reflect()
        db.drop_all()


def fill_services():
    for service_name in services_data:
        service = Service(name=service_name)
        db.session.add(service)
    db.session.commit()


fill_user_table = False
with app.app_context():
    # проверить, существует ли таблица и выставить флаг, если нет
    inspector = inspect(db.engine)
    if "user" not in inspector.get_table_names():
        fill_user_table = True

    # создать таблицы
    db.create_all()

    # заполнить таблицы, если они только созданы
    if fill_user_table:
        fill_services()
