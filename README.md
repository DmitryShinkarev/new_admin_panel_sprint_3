# Инструкция

1. Создать сеть
   
        docker network create --driver bridge app_movies_net

2. Запустить сборку образа из докер-компоус

        docker-compose up -d --build db admin_panel nginx


3. Подключиться к контейнеру с admin_panel и выполнить создание миграций и суперпользователя.

        python manage.py makemigrations
        python manage.py migrate
        python manage.py createsuperuser

4. Запустить процесс переноса данных из базы litesql в том же контейнере из директории sqlite_to_postgres

        cd sqlite_to_postgres
        python load_data.py

5. Запустить Elasticsearch и сопутствующие конетейнеры.

        docker-compose up -d --build es redis etl

# Заключительное задание первого модуля

Ваша задача в этом уроке — загрузить данные в Elasticsearch из PostgreSQL. Подробности задания в папке `etl`.