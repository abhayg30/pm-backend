release: python manage.py makemigrations auths
release: python manage.py makemigrations industry
release: python manage.py makemigrations student
release: python manage.py makemigrations application
release: python manage.py makemigrations progression
release: python manage.py makemigrations ratings
release: python manage.py migrate --no-input

web: gunicorn powerpuff.wsgi