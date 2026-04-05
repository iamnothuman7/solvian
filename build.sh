#!/usr/bin/env bash
# Script de build para o Render.com
# Executado automaticamente durante o deploy

set -o errexit

# Instalar dependências Python
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

# Executar migrations do banco de dados
python manage.py migrate
