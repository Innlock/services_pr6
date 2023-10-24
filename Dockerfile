# Используем официальный образ Python
FROM python:3.10

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip uninstall -y Werkzeug && \
    pip install Werkzeug==2.3.7

# Копируем все файлы приложения в контейнер
COPY . .

# Определите порт, который Flask будет слушать
EXPOSE 5000

# Запускаем Flask приложение
CMD ["python", "app.py"]
