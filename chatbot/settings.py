"""
Django 프로젝트의 설정 파일
데이터베이스, 미들웨어, 템플릿 등 프로젝트의 모든 설정을 관리
"""
import os
from pathlib import Path

# 프로젝트 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# 보안 설정
SECRET_KEY = 'django-insecure-your-secret-key'  # 실제 배포 시 변경 필요
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# 설치된 앱 목록
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chatbot', 
    'corsheaders',# 여러분의 앱 이름
]

# 미들웨어 설정
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# CORS 설정
CORS_ALLOW_ALL_ORIGINS = True  # 개발 환경에서만 사용. 프로덕션에서는 특정 도메인만 허용하도록 설정

# URL 설정
ROOT_URLCONF = 'chatbot.urls'

# 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # SQLite 데이터베이스 사용
        'NAME': BASE_DIR / 'db.sqlite3',        # 데이터베이스 파일 위치
    }
}

# 정적 파일 설정
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 로그인 관련 설정
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'chat'

# 기본 자동 필드 설정
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# settings.py
LOGOUT_REDIRECT_URL = '/login/'  # 로그아웃 후 리디렉션할 URL