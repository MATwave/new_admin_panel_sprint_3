INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'movies.apps.MoviesConfig',
    "debug_toolbar",
    "django_extensions",
# для Try it out swagger'а
    "corsheaders",
]

CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:8080",
                        "http://localhost:8080"]


