sudo service nginx restart
sudo service uwsgi restart
python3 manage.py migrate
python3 manage.py collectstatic