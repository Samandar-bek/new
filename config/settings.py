import os
from pathlib import Path

# 📁 Asosiy loyiha katalogi
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Maxfiy kalit (test uchun)
SECRET_KEY = 'django-insecure-test-pro-secret-key-2024'

# ⚙️ Debug rejimi
DEBUG = True

ALLOWED_HOSTS = ['*']

# 🔌 Django ilovalari
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',  # 👈 o'zingning ilovang
]

# 🧩 Middleware sozlamalari
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 🔗 URL sozlamalari
ROOT_URLCONF = 'config.urls'

# 🎨 Shablonlar (templates) uchun sozlamalar
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # templates papkasi
            BASE_DIR,                # asosiy papka (index.html joylashgan)
        ],
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

# 🚀 WSGI
WSGI_APPLICATION = 'config.wsgi.application'

# 🛢️ MySQL DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myproject',       # ✅ MySQL da yaratilgan bazaning nomi
        'USER': 'root',            # ✅ MySQL foydalanuvchi nomi
        'PASSWORD': '123456789',   # ✅ MySQL foydalanuvchi paroli
        'HOST': 'localhost',       # ✅ MySQL server manzili
        'PORT': '3306',            # ✅ MySQL porti (standart)
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 300,
    }
}

# 🔑 Parol tekshiruvi
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌍 Til va vaqt zonasi
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# 🖼️ Statik va media fayllar
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 🧱 Model ID konfiguratsiyasi
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 🔐 Maxsus sozlamalar
LOGIN_URL = '/'
SESSION_COOKIE_AGE = 3600  # 1 soat

# ✅ MySQL client o‘rnatilganligiga ishonch hosil qilish
# Terminalda bu buyruqlarni bajarasiz:
# pip install mysqlclient
# python manage.py makemigrations
# python manage.py migrate
