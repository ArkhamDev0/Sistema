from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-v&6lxqpn0m6&6w8%nt&p!rj+(4ps(#@mc4s=k3z&xb-vy!!dgd'
DEBUG = True
ALLOWED_HOSTS = ['*']  # Permite cualquier host (solo para desarrollo local)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # Para servir archivos estáticos
    'visitantes',
    'users'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'museo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "visitantes" / "templates" / "dj"],  # Cambiado para apuntar a la carpeta 'dj'
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'museo.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Cambiar a PostgreSQL
        'NAME': 'helpdesk',  # Reemplaza con el nombre de tu base de datos
        'USER': 'miguel',  # Reemplaza con tu usuario de PostgreSQL
        'PASSWORD': '123',  # Reemplaza con tu contraseña de PostgreSQL
        'HOST': 'localhost',  # Cambia esto si tu base de datos está en otro servidor
        'PORT': '5432',  # El puerto por defecto para PostgreSQL
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-VE'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'visitantes', 'static'),  # Ruta al directorio estático dentro de la app 'visitantes'
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de autenticación
LOGIN_URL = 'login'  # URL a la que se redirige a los no autenticados
LOGIN_REDIRECT_URL = 'visitor_list'  # URL a la que se redirige a los usuarios después de iniciar sesión

# Añadir estas líneas al final
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://172.20.10.151:8000']
SESSION_COOKIE_SECURE = False

AUTH_USER_MODEL = 'users.CustomUser'  # Asegúrate de que esto sea correcto