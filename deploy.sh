git pull origin master
python3 manage.py migrate
python3 manage.py collectstatic
sudo service nginx restart
sudo service uwsgi restart
# sudo /home/ubuntu/restart_celery.sh