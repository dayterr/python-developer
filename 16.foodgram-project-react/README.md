# Продуктовый помощник
![example workflow](https://github.com/dayterr/foodgram-project-react/actions/workflows/foodgram-workfolow.yml/badge.svg)

Дипломный проект Яндекс.Практикума по специальности "Python-разработчик" – "Продуктовый помощник". На этом срвисе пользователи могут публиковать свои любимые рецепты, отмечать понравившиеся рецепты и даже получать список ингредиентов, необходимых для приготовления выбранных блюд, в формате PDF.

Проект доступен по адресу: http://178.154.195.129/

# Стэк
- Python 3; 
- Django; 
- Django Rest Framework;
- PostgreSQL;
- nginx;
- Docker.

# Запуск проекта

Для запуска программы необходимы **Docker** и **docker-compose.

Инструкция для установки **Docker** на русском языке: [ссылка](https://dker.ru/docs/docker-engine/install/).

Инструкция для установки **docker-compose**: [ссылка](https://docs.docker.com/compose/install/).

Файл .env должен лежать в корневой папке. В себе он содержит следующие данные:

- DB_ENGINE – используемая база данных
- DB_NAME – имя БД
- POSTGRES_USER – имя пользователя
- POSTGRES_PASSWORD – пароль
- DB_HOST=db
- DB_PORT – порт БД
- SECRET_KEY – секретный ключ Django
- DEBUG – включен ли режим дебага в Django
- ALLOWED_HOSTS – разрешённые хосты

Клонировать репозиторий: ```git clone https://github.com/dayterr/yamdb_final.git```

Запустить программу: ```docker-compose up```

Осуществить миграции: 
```
docker-compose exec -T web python manage.py makemigrations recipes users --no-input
docker-compose exec -T web python manage.py migrate --no-input
```

Создать суперпользователя: ```docker-compose exec web python manage.py createsuperuser```

Заполнить базу данных: ```docker-compose exec -T web python manage.py loaddata fixtures.json```

Собрать статику: ```docker-compose exec -T web python manage.py collectstatic --no-input```

Автор: Мария Дайтер – https://github.com/dayterr
