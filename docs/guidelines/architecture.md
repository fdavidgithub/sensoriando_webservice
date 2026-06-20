# Arquitetura do Sistema Sensoriando Webservice

## Visão Geral

O Sensoriando Webservice é a camada web e de API da plataforma Sensoriando
(*Hub de Sensores*). Ele expõe uma API REST e páginas web que apresentam os
dados de sensores coletados pela plataforma.

A aplicação **não é dona do schema do banco de dados**: ela lê e apresenta os
dados de um banco PostgreSQL compartilhado, populado pelo
[Sensoriando Core](https://github.com/fdavidgithub/sensoriando_core/) (ingestão
via MQTT). Por isso, todas as tabelas de domínio são mapeadas com
`managed = False`.

Construída em Django 3.2 com Django REST Framework, autenticação JWT
(SimpleJWT) e documentação de API via Swagger/OpenAPI (drf-yasg).

---

## Módulos Principais

```
core/        → projeto Django (settings, urls raiz, wsgi)
base/        → camada de dados e utilitários compartilhados
               - legacy_tables.py  → mapeamento das tabelas do banco (managed=False)
               - legacy_views.py   → mapeamento das views do banco (vw*)
               - models.py         → proxy models (__str__/Meta) sobre as tabelas legadas
               - views.py          → helper callAPI() e views utilitárias
               - constants.py      → constantes de domínio (estados, gráficos)
api/         → API REST (viewsets, APIViews, serializers, rotas e Swagger)
overview/    → páginas web públicas/privadas (home/listagem)
sensors/     → páginas web de detalhe de um Thing/sensor
users/       → autenticação, cadastro (signup) e área da conta
templates/   → templates HTML server-rendered
static/      → assets estáticos (css, js, img)
```

---

## Fluxo de Dados

```
Sensoriando Core (MQTT)  ──escreve──►  PostgreSQL (sensoriando_database)
                                              │
                                              │ leitura (Django ORM, managed=False)
                                              ▼
                                    base.models (proxy models)
                                              │
                                              ▼
                                    api.serializers ──► api.views (REST)
                                              ▲                 │
                                              │ HTTP (callAPI)  │ JSON
                                              │                 ▼
                          overview / sensors / users  ──►  templates HTML
                                              │
                                              ▼
                                          Navegador
```

As páginas web (overview/sensors/users) **consomem a própria API REST por HTTP**
através do helper `base.views.callAPI`, que aponta para `DJANGO_PREFIX_API`.

---

## Camadas Arquiteturais

1. **Camada de dados (`base/legacy_tables.py`, `base/legacy_views.py`)**
   Mapeamento Django ORM das tabelas e views existentes no PostgreSQL. Todas com
   `managed = False` — o Django não cria nem altera essas tabelas.

2. **Camada de modelos de domínio (`base/models.py`)**
   Proxy models que adicionam `__str__` e metadados de exibição sobre as tabelas
   legadas, sem alterar o schema.

3. **Camada de serialização (`api/serializers.py`)**
   Serializers do DRF que convertem os modelos em JSON e calculam campos
   derivados (ex.: `lastupdate`, estatísticas).

4. **Camada de API (`api/views.py`, `api/urls.py`)**
   Viewsets e APIViews REST, com endpoints públicos e privados (JWT).

5. **Camada de apresentação web (`overview/`, `sensors/`, `users/`)**
   Views Django que renderizam templates HTML e consomem a API via `callAPI`.

---

## Infraestrutura

- Execução containerizada via **Docker** e **docker-compose**.
- Imagem base `python:3.8`; container `sensoriando_webservice` servido por
  `manage.py runserver` (ver `entrypoint.sh`).
- Rede Docker externa `sensoriando`, compartilhada com o container de banco
  `sensoriando_database` (provido pelo Sensoriando Core).
- Scripts de operação: `init.sh` (preparação da primeira execução) e `run.sh`
  (subir os containers).
- Configuração via variáveis de ambiente (`.env`); ver `env.example`.

---

## Princípios Arquiteturais

- **Banco compartilhado e não gerenciado:** o schema é de responsabilidade do
  Sensoriando Core; este serviço apenas lê/apresenta (`managed = False`).
- **Separação por camadas:** dados → modelos → serializers → API → apresentação.
- **Distinção público/privado:** endpoints e dados são segmentados pelo plano da
  conta (`plans.ispublic`); o acesso privado exige autenticação JWT.
- **Configuração por ambiente:** nenhuma credencial ou URL é fixada no código
  (ver `docs/guidelines/coding-standards.md`).
- **Idioma:** código-fonte em inglês; documentação em `/docs` em português.
