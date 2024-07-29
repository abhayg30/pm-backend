release: python manage.py makemigrations --no-input
release: python manage.py migrate --no-input
release: python3 manage.py crontab add --no-input


web: gunicorn powerpuff.wsgi