from fabric.contrib.files import append, exists, sed, put
from fabric.api import env, local, run, sudo
from fabric.colors import green
import os
import json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)

with open(os.path.join(PROJECT_DIR, "deploy.json")) as f:
    envs = json.loads(f.read())

REPO_URL = envs['REPO_URL']
PROJECT_NAME = envs['PROJECT_NAME']
REMOTE_HOST_SSH = envs['REMOTE_HOST_SSH']
REMOTE_HOST = envs['REMOTE_HOST']
REMOTE_USER = envs['REMOTE_USER']
ALLOWED_HOSTS = envs['ALLOWED_HOSTS']

env.user = REMOTE_USER
username = env.user
env.hosts = [REMOTE_HOST_SSH, ]
env.key_filename = ["~/.ssh/cole-rochman.pem", ]

virtualenv_folder = '/home/{}/.pyenv/versions/production'.format(env.user)
project_folder = '/home/{}/srv/{}'.format(env.user, PROJECT_NAME)
appname = 'core'


def _get_latest_source():
    print(green('_get_latest_source'))
    if exists(project_folder + '/.git'):
        run('cd %s && git fetch' % (project_folder,))
    else:
        run('git clone %s %s' % (REPO_URL, project_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (project_folder, current_commit))


def _update_settings():
    print(green('_update_settings'))
    settings_path = project_folder + '/{}/settings.py'.format(PROJECT_NAME)
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path, 'ALLOWED_HOSTS = .+$',
        'ALLOWED_HOSTS = [%s]' % ','.join(['\"%s\"' % host for host in ALLOWED_HOSTS]))


def _update_virtualenv():
    print(green('_update_virtualenv'))
    run('%s/bin/pip install -r %s/requirements.txt' % (
        virtualenv_folder, project_folder
    ))


def _update_static_files():
    print(green('_update_static_files'))

    run('cd %s && %s/bin/python3 manage.py collectstatic --noinput' % (
        project_folder, virtualenv_folder
    ))


def _update_database():
    print(green('_update_database'))
    run('cd %s && %s/bin/python3 manage.py makemigrations --noinput' % (
        project_folder, virtualenv_folder
    ))
    run('cd %s && %s/bin/python3 manage.py migrate --noinput' % (
        project_folder, virtualenv_folder
    ))
    run('cd %s && %s/bin/python3 manage.py makemigrations %s --noinput' % (
        project_folder, virtualenv_folder, appname
    ))
    run('cd %s && %s/bin/python3 manage.py migrate %s --noinput' % (
        project_folder, virtualenv_folder, appname
    ))


def _grant_uwsgi():
    print(green('_grant_uwsgi'))
    sudo('sudo chown -R :deploy {}'.format(project_folder))


def _restart_uwsgi():
    print(green('_restart_uwsgi'))
    sudo('sudo cp -f {}/config/uwsgi.service /etc/systemd/system/uwsgi.service'.format(project_folder))
    sudo('sudo systemctl daemon-reload')
    sudo('sudo systemctl restart uwsgi')


def _restart_nginx():
    print(green('_restart_nginx'))
    sudo('sudo cp -f {}/config/nginx.conf /etc/nginx/sites-available/nginx.conf'.format(project_folder))
    sudo('sudo ln -sf /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/nginx.conf')
    sudo('sudo systemctl restart nginx')


def deploy():
    _get_latest_source()
    _update_settings()
    _update_virtualenv()
    _update_static_files()
    _update_database()
    _grant_uwsgi()
    _restart_uwsgi()
    _restart_nginx()
