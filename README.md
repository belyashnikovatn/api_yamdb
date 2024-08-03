# Проект api_yamdb
Цель проекта -- научиться работать в команде.   
ТЗ -- доки Redoc.

## Содержание
- [Технологии](#технологии)
- [Запуск проекта](#запуск-проекта)
- [Выполненные задачи](#задачи)
- [Функционал](#функционал)

## Технологии:
Python + Django REST Framework + аутентификация (позже расписать какая именно)


## Запуск проекта (для винды):
- $ python -m venv venv
- $ source venv/Scripts/activate
- $ python -m pip install --upgrade pip
- $ pip install -r requirements.txt
- $ cd api_yamdb
- $ python manage.py migrate
- $ python manage.py loaddata reviews_db.json // для загрузки данных
- $ python manage.py runserver
- $ python manage.py import_csv_data // для загрузки данных


## Выполненные задачи
- создали приложения:
- reviews для работы с проивзедениями
- api для сервиса
- users для кастомизации модели User 
