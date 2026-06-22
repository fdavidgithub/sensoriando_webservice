# Banco de Dados — {{NOME_PROJETO}}

## Tecnologia

{{BANCO_DE_DADOS}}

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

{{PADROES_DE_ACESSO}}

---

## Regras de Infraestrutura

{{REGRAS_INFRA_DB}}
