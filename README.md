Скачать проект. Для установки библиотек последовательно выполнить команды:
- `python.exe -m pip install --upgrade pip --user` (можно пропустить)
- `pip install -r requirements.txt`
- `pip uninstall -y Werkzeug`
- `pip install Werkzeug==2.3.7`

Запустить доккер. В папке с проектом запустить команду `docker-compose up` для запуска бд. Далее выполнить команду `python app.py `.