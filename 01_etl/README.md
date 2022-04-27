# Инструкция

1. Запустить сборку образа из докер-компоус

        docker-compose up -d --build db admin_panel nginx


2. Подключиться к контейнеру с admin_panel и выполнить создание миграций и суперпользователя.

        python manage.py makemigrations
        python manage.py migrate
        python manage.py createsuperuser

3. Запустить процесс переноса данных из базы litesql в том же контейнере из директории sqlite_to_postgres

        cd sqlite_to_postgres
        python load_data.py

4. Запустить Elasticsearch и сопутствующие конетейнеры.

        docker-compose up -d --build es redis etl

# Заключительное задание первого модуля

Ваша задача в этом уроке — загрузить данные в Elasticsearch из PostgreSQL. Подробности задания в папке `etl`.
