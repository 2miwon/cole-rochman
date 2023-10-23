git pull origin master
python3 manage.py migrate
python3 manage.py collectstatic -y
sudo service nginx restart
sudo service uwsgi restart
