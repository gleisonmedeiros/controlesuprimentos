call C:\controlesuprimentos\venv\Scripts\activate
cd C:\controlesuprimentos\controlesuprimentos
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
gunicorn controlesuprimentos.wsgi:application --bind 0.0.0.0:8000 --workers 3


