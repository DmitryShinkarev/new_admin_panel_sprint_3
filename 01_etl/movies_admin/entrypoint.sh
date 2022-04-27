#!/bin/sh
if [ "$POSTGRES_DB" = "movies_database" ]
then
    echo "Waiting for postgres..."

   open=0;
   while [ $open -eq 0 ]
   do
      check_port=`nc -v -w 1 -i 1 postgres 5432 &> /dev/stdout`
      echo $check_port
      if [[ "$check_port" == *"succeeded"* ]]
      then
        break
      fi
        sleep 1
  done

    echo "PostgreSQL started"
fi

cd..

python manage.py flush --no-input
#python manage.py makemigrations
#python manage.py migrate
python manage.py collectstatic --no-input --clear
#python manage.py createsuperuser

gunicorn config.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile -