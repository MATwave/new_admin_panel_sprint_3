import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

include(
    'components/database.py',
    'components/auth_password_validation.py',
    'components/installed_apps.py',
    'components/middleware.py',
    'components/templates.py',
    'components/django_logging.py',
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', "127.0.0.1").split(' ')

if DEBUG:
    import socket

    INTERNAL_IPS = ['127.0.0.1', '::1', 'localhost']

    # get ip address for docker host
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    for ip in ips:
        # replace last octet in IP with .1
        ip = '{}.1'.format(ip.rsplit('.', 1)[0])
        INTERNAL_IPS.append(ip)

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True if DEBUG else False,
    }
    

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = ['movies/locale']

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

