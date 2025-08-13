# yamdb_final
yamdb_final

![example workflow](https://github.com/dayterr/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

API для YaMDB. YaMDb содержит отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: «Фильмы» и «Музыка». Список категорий может расширить админ. У произведений есть название, описание, жанр, год создания и категория.

Файл .env должен лежать в корневой папке. В себе он содержит следующие данные:

DB_ENGINE – используемая база данных
DB_NAME – имя БД
POSTGRES_USER – имя пользователя
POSTGRES_PASSWORD – пароль
DB_HOST=db
DB_PORT – порт БД
SECRET_KEY – секретный ключ Django
DEBUG – включен ли режим дебага в Django
ALLOWED_HOSTS – разрешённые хосты

Для запуска программы нужны Docker и docker-compose.

Инструкция для установки Docker на русском языке: [ссылка](https://dker.ru/docs/docker-engine/install/).

Инструкция для установки docker-compose: [ссылка](https://docs.docker.com/compose/install/).

Клонировать репозиторий: git clone https://github.com/dayterr/yamdb_final.git

Запустить программу: docker-compose up

Создать суперпользователя: docker-compose exec web python manage.py createsuperuser

Заполнить базу данных: django-admin loaddata fixtures.json

Ознакомиться с документацией: http://127.0.0.1/redoc/

Адрес: http://178.154.195.129/api/v1/

Использованные технологии: Django REST Framework, Docker, GitHub Actions

Автор: Мария Дайтер – https://github.com/dayterr