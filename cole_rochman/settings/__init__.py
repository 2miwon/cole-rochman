import os
SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE')
STATIC_ROOT = '/var/www/cole-rochman/static'

if SETTINGS_MODULE == 'cole_rochman.settings.dev':
    from .dev import *
else:
    from .prod import *