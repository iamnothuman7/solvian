# Solvian

Projeto acadêmico de Sistemas de Informação para estudar dimensionamento fotovoltaico em uma aplicação Django. Integra formulários, consulta de irradiação solar, estimativas de geração e documentos em PDF.

## Escopo implementado

- Dimensionamento a partir de consumo, localização e características da instalação.
- Consulta à API NASA POWER, com cache e estimativas de contingência quando a consulta falha.
- Comparação de geração mensal e detecção experimental de anomalias com Isolation Forest.
- Geração de propostas em PDF com WeasyPrint.
- Estimativas de economia e retorno com os parâmetros informados.

Os cálculos são demonstrativos. Não substituem projeto de engenharia, inspeção de equipamentos ou análise financeira profissional. A detecção de anomalias não comprova a causa de uma falha. Dados estimados de contingência não devem ser confundidos com respostas da NASA.

## Tecnologias e organização

Python, Django, Pandas, NumPy, scikit-learn, Requests e WeasyPrint. SQLite é a configuração local padrão; a configuração também aceita `DATABASE_URL`.

| Diretório | Responsabilidade |
| --- | --- |
| `core/` | Formulários, páginas e fluxo de interação |
| `dimensionamento/` | Cálculos e análise experimental de geração |
| `satelite/` | Integração NASA POWER e cache |
| `relatorios/` | Documentos em PDF |
| `templates/` e `static/` | Interface e recursos visuais |

## Execução local

Use Python compatível com as dependências fixadas em `requirements.txt`. O [Django 6.0 exige Python 3.12 ou posterior nas séries suportadas](https://docs.djangoproject.com/en/6.0/faq/install/). Instale também as dependências de sistema indicadas no [guia do WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).

```sh
git clone https://github.com/iamnothuman7/solvian.git
cd solvian
python -m venv .venv
```

Ative o ambiente com `source .venv/bin/activate` no Linux/macOS ou `.venv\Scripts\Activate.ps1` no PowerShell. Depois:

```sh
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver 127.0.0.1:8000
```

Abra `http://127.0.0.1:8000/`. Use dados fictícios ao explorar os formulários.

## Configuração e limites atuais

- `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS` são lidos do ambiente. A chave padrão serve apenas ao desenvolvimento local.
- Os arquivos de testes existentes ainda são esboços. Não há cobertura funcional comprovada pelo simples comando `manage.py test`.
- `render.yaml` ainda fixa Python 3.11.6, incompatível com o Django 6.0 declarado. Corrija a configuração e valide as dependências antes de tentar esse deploy.
- Para PostgreSQL, instale e configure um driver compatível; a presença de `DATABASE_URL` não instala o driver.
- Valide migrações de todos os aplicativos, geração de PDF, indisponibilidade da API e parâmetros dos cálculos antes de uso real.
- As páginas de simulação são públicas; este projeto não oferece isolamento de clientes de um SaaS.

## Contribuições e uso

Propostas de melhoria podem vir por issue ou pull request, com passos de reprodução e dados fictícios. Não publique credenciais ou dados de clientes. A identificação como projeto acadêmico não equivale a uma licença de software; este repositório não declara uma licença de redistribuição.
