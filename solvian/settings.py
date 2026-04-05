"""
Configurações do Django para o projeto Solvian.
Suporta desenvolvimento local (SQLite) e produção (PostgreSQL no Render.com).
Usa python-decouple para variáveis de ambiente.
"""

import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url

# ==============================================================================
# CAMINHOS BASE
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SEGURANÇA
# ==============================================================================

# Em produção, defina a SECRET_KEY como variável de ambiente
SECRET_KEY = config('SECRET_KEY', default='django-insecure-solvian-dev-key-mude-em-producao-123456')

# Em produção, defina DEBUG=False
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ==============================================================================
# APLICAÇÕES INSTALADAS
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do Solvian
    'core.apps.CoreConfig',
    'satelite.apps.SateliteConfig',
    'dimensionamento.apps.DimensionamentoConfig',
    'relatorios.apps.RelatoriosConfig',
]

# ==============================================================================
# MIDDLEWARE
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise para servir arquivos estáticos em produção
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'solvian.urls'

# ==============================================================================
# TEMPLATES
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'solvian.wsgi.application'

# ==============================================================================
# BANCO DE DADOS
# ==============================================================================

# SQLite para desenvolvimento local, PostgreSQL para produção (via DATABASE_URL)
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
    )
}

# ==============================================================================
# INTERNACIONALIZAÇÃO
# ==============================================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# ARQUIVOS ESTÁTICOS
# ==============================================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise para compressão e cache de estáticos em produção
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ==============================================================================
# ARQUIVOS DE MÍDIA (uploads)
# ==============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================================
# CHAVE PRIMÁRIA PADRÃO
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# CONFIGURAÇÕES DE SEGURANÇA PARA PRODUÇÃO
# ==============================================================================

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ==============================================================================
# CONFIGURAÇÕES DA NASA POWER API
# ==============================================================================

NASA_POWER_API_URL = 'https://power.larc.nasa.gov/api/temporal/climatology/point'
NASA_POWER_TIMEOUT = 30  # Timeout em segundos para a API

# ==============================================================================
# CONFIGURAÇÕES DO SISTEMA SOLAR (valores padrão para cálculos)
# ==============================================================================

# Eficiência padrão do sistema fotovoltaico (perdas por temperatura, sujeira, etc.)
EFICIENCIA_SISTEMA = config('EFICIENCIA_SISTEMA', default=0.80, cast=float)

# Potência padrão de cada painel solar em Watts-pico
POTENCIA_PAINEL_WP = config('POTENCIA_PAINEL_WP', default=550, cast=int)

# Custo médio por Watt-pico instalado (R$/Wp) — ajustável por região
CUSTO_POR_WP = config('CUSTO_POR_WP', default=4.50, cast=float)

# Horas de sol pico padrão (usado como fallback se a API falhar)
HSP_PADRAO = config('HSP_PADRAO', default=4.5, cast=float)
