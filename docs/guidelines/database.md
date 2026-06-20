# Banco de Dados — Sensoriando Webservice

## Tecnologia

**PostgreSQL** (driver `psycopg2` / `psycopg2-binary`), configurado em
`core/settings.py` via `django.db.backends.postgresql_psycopg2` e parametrizado
pelas variáveis `POSTGRES_*` do ambiente.

O banco (`sensoriando_database`) é **compartilhado** e populado pelo
[Sensoriando Core](https://github.com/fdavidgithub/sensoriando_core/). Este
serviço apenas lê os dados: **todas as tabelas e views são mapeadas com
`managed = False`** (`base/legacy_tables.py` e `base/legacy_views.py`), ou seja,
o Django não cria, altera nem remove o schema.

> Observação: as convenções de nomenclatura abaixo descrevem o padrão de
> referência do projeto. O **schema legado existente**, por ser de
> responsabilidade do Sensoriando Core, segue convenções próprias (ver
> "Convenções do schema legado" mais adiante).

---

## Convenção de Nomenclatura

### Tabelas

- Nomes sempre no **plural** e em PascalCase: `Things`, `Sensors`, `Readings`

### Colunas

- Nomes no **singular**
- Chave primária: `id` (auto increment)
- Campo de criação: `dt` (datetime, valor padrão = data/hora atual)
- Campos de data: prefixo `dt` + identificador descritivo — ex.: `dtCreated`, `dtLimit`, `dtExpired`
- Chave estrangeira: `<nome_tabela_referenciada_singular>_id` — ex.: se `Sensors` referencia `Things`, o campo é `things_id`

---

## Estrutura Padrão de Tabela (Relacional)

Toda tabela deve ter ao menos as seguintes colunas:

| Coluna | Tipo       | Descrição                              |
|--------|------------|----------------------------------------|
| `id`   | INT AI PK  | Chave primária auto increment          |
| `dt`   | DATETIME   | Data/hora de criação do registro (NOW) |

### Exemplo — tabela principal `Entities`

```sql
CREATE TABLE Entities (
    id    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    dt    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name  VARCHAR(255) NOT NULL
    -- demais colunas específicas do domínio
);
```

### Exemplo — tabela `Items` com relacionamento para `Entities`

```sql
CREATE TABLE Items (
    id          INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    dt          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    entities_id INT          NOT NULL,
    label       VARCHAR(255) NOT NULL,
    dtLimit     DATETIME     NULL,
    -- demais colunas específicas do domínio
    FOREIGN KEY (entities_id) REFERENCES Entities(id)
);
```

---

## Padrões de Acesso

- O acesso ao banco é feito exclusivamente pelo **Django ORM**.
- As tabelas/views são mapeadas em `base/legacy_tables.py` e
  `base/legacy_views.py` com `managed = False`.
- Em `base/models.py` há **proxy models** (`Meta.proxy = True`) que adicionam
  `__str__` e metadados de exibição sem alterar o schema.
- Os serializers (`api/serializers.py`) e as views (`api/views.py`) consomem
  esses modelos; as views web acessam os dados pela API REST via
  `base.views.callAPI`.
- Agregações por período (segundo/minuto/hora) usam funções do ORM
  (`Trunc*`, `Avg`); agregações por dia/mês/ano usam as views
  `vwthingssensorsdata_*` e/ou as tabelas pré-agregadas
  `dailyaveragedata`, `monthlyaveragedata`, `yearlyaveragedata`.

### Convenções do schema legado

Padrões observados nas tabelas mapeadas (definidas pelo Sensoriando Core):

- Nomes de tabela em **snake_case minúsculo** e plural: `things`, `sensors`,
  `accounts`, `thingssensorsdata`.
- Coluna de criação `dt` (`DateTimeField`) presente em todas as tabelas.
- Chave primária implícita `id` (AutoField do Django).
- Chave estrangeira com prefixo **`id_`** + tabela referenciada no singular —
  ex.: `id_thing`, `id_sensor`, `id_account` (atributo `db_column`).
- Restrições de unicidade via `unique_together` / `unique=True`.

---

## Regras de Infraestrutura

- O schema é de responsabilidade do **Sensoriando Core**; este serviço **não**
  deve criar nem alterar tabelas (`managed = False`).
- Migrações Django existem apenas para os apps próprios sem modelos de schema
  (geradas em runtime pelo `entrypoint.sh`); arquivos de migração são ignorados
  no versionamento (ver `.gitignore`).
- As credenciais e o host do banco são lidos das variáveis `POSTGRES_*` do
  ambiente; nunca devem ser fixados no código.
- O banco é acessado pela rede Docker externa `sensoriando`, na qual o container
  `sensoriando_database` deve estar disponível.
