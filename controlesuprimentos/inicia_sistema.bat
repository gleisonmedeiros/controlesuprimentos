call C:\controlesuprimentos\venv\Scripts\activate
cd C:\controlesuprimentos\controlesuprimentos
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
waitress-serve --listen=0.0.0.0:8000 controlesuprimentos.wsgi:application


