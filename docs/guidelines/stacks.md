# Stack Tecnológica do Projeto

## Visão Geral

O Sensoriando Webservice é uma aplicação Django (web + API REST) que apresenta
os dados de sensores da plataforma Sensoriando, lendo de um banco PostgreSQL
compartilhado e populado pelo Sensoriando Core.

---

## Linguagem e Runtime

- **Python 3.8** (runtime da aplicação — imagem Docker `python:3.8`)
- **Python 3.8 / framework de testes do Django** (ambiente de testes local)

---

## Infraestrutura como Código

- **Docker** (`Dockerfile`) e **docker-compose** (`docker-compose.yaml`)
- Scripts shell de operação: `init.sh` e `run.sh`
- Rede Docker externa `sensoriando` compartilhada com o banco de dados

---

## Serviços de Nuvem Utilizados

Não aplicável — a implantação é **self-hosted** via Docker/docker-compose.
Nenhum provedor de nuvem é referenciado no código.

---

## Integrações Externas

- **Sensoriando Core** — produtor dos dados; popula o banco PostgreSQL
  compartilhado (`sensoriando_database`) consumido por este serviço.
- **API REST própria** — as views web consomem a API interna por HTTP via
  `base.views.callAPI` (`DJANGO_PREFIX_API`).

---

## Bibliotecas Permitidas

### Runtime da Aplicação

Fixadas em `requirements.txt`:

- `Django==3.2`
- `djangorestframework==3.13.1`
- `django-jsonfield==1.4.1`
- `django-cors-headers==3.13.0`
- `djangorestframework-simplejwt==5.2.2`
- `django-rest-swagger==2.2.0`
- `drf-yasg==1.21.4`
- `python-dotenv==0.21.1`
- `psycopg2==2.8.5` / `psycopg2-binary==2.8.5`
- `unicodecsv==0.14.1`
- `markdown==3.3.6`
- `requests==2.27.1`
- `pycountry==22.3.5`
- `python-dateutil==2.8.2`
- `pandas==2.0.3`

### Infraestrutura (IaC)

- Docker
- docker-compose

### Testes

- Framework de testes do Django (`django.test`, executado via
  `python manage.py test`). Nenhuma biblioteca de testes adicional consta em
  `requirements.txt`.

---

## Bibliotecas Proibidas

Nenhuma biblioteca é explicitamente proibida no código. A regra vigente é a de
**fixar a versão** de qualquer dependência em `requirements.txt` e evitar
introduzir bibliotecas não listadas neste documento.

---

## Estrutura de Módulos

```
core/        → configuração do projeto Django
base/        → mapeamento do banco (managed=False), proxy models e utilitários
api/         → API REST (DRF + JWT + Swagger)
overview/    → páginas web públicas/privadas
sensors/     → páginas web de detalhe
users/       → autenticação e conta
```

---

## Adicionando Novas Dependências

Para adicionar uma biblioteca:

1. Verifique se o caso de uso não é coberto pelas bibliotecas existentes.
2. Adicione ao `requirements.txt` com a versão fixada.
3. Atualize este arquivo.
