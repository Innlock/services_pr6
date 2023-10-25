from models import Service, User, Message
from init import db, app
from sqlalchemy import inspect

services_data1 = [
    ["Обработка (услуги администрирования)", "10000 руб", "business"],
    ["Хранение (услуги администрирования)", "10000 руб", "business"],
    ["Дизайн (услуги создания)", "5000 руб", "business"],
    ["Развитие (услуги создания)", "7000 руб", "business"],
    ["Проектирование (услуги создания)", "15000 руб", "business"]
]
services_data2 = [
    ["Веб-серверы и хостинг-ресурсы", "technical"],
    ["Облачные ресурсы", "technical"],
    ["Системы мониторинга и отчетности", "technical"],
    ["Серверное оборудование", "technical"]
]


def drop_all_tables():
    with app.app_context():
        db.reflect()
        db.drop_all()


def fill_services():
    for service_name in services_data1:
        service = Service(name=service_name[0], description=service_name[1], type=service_name[2])
        db.session.add(service)
    for service_name in services_data2:
        service = Service(name=service_name[0], type=service_name[1])
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
