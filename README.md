# Solvian — Energia Solar Inteligente

Sistema All-in-One para empresas de energia solar. Dimensionamento automatizado com dados de satélite (NASA POWER), geração de propostas em PDF e manutenção preditiva com Inteligência Artificial.

## 🚀 Como Rodar Localmente

```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar migrations
python manage.py migrate

# 4. Rodar o servidor
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## 🛰️ Funcionalidades

- **Dimensionamento Solar**: Cálculo automático de potência, painéis e geração
- **Dados de Satélite (NASA POWER)**: Irradiação solar real para qualquer localização
- **Proposta em PDF**: Documento profissional para enviar ao cliente
- **Manutenção Preditiva (IA)**: Detecção de anomalias com Scikit-learn
- **Análise Financeira**: Payback, ROI, economia em 25 anos

## 🛠️ Stack Tecnológica

- **Backend**: Django (Python)
- **Dados de Satélite**: API NASA POWER
- **IA/ML**: Pandas + Scikit-learn
- **PDF**: WeasyPrint
- **Deploy**: Render.com

## ☁️ Deploy no Render.com

1. Suba o código para o GitHub
2. Acesse [render.com](https://render.com) e conecte o repositório
3. Crie um **Web Service** com:
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn solvian.wsgi:application`
4. Adicione as variáveis de ambiente:
   - `SECRET_KEY` (gerar uma nova)
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `.onrender.com`

## 📄 Licença

Projeto acadêmico — TCC em Sistemas de Informação.
