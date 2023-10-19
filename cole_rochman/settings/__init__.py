import os
SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE')

if not SETTINGS_MODULE or SETTINGS_MODULE == 'cole_rochman.settings':
    from .dev import *
# elif SETTINGS_MODULE == 'cole_rochman.settings.prod':
#     from .prod import *
else:
    from .prod import *