# Padrões de Código — {{NOME_PROJETO}}

## Linguagem

Todo código-fonte deve ser escrito em **inglês**, incluindo nomes de variáveis, funções, classes, arquivos, campos de banco de dados, comentários, mensagens de log e mensagens de erro.

---

## Convenções de Nomenclatura

| Elemento                      | Padrão                              |
|-------------------------------|-------------------------------------|
| Classes                       | PascalCase                          |
| Funções / métodos             | snake_case                          |
| Variáveis                     | snake_case                          |
| Constantes                    | UPPER_CASE                          |
| Arquivos                      | snake_case                          |
| Tabelas (banco de dados)      | snake_case (plural)                 |
| Colunas (banco de dados)      | snake_case                          |
| Índices                       | snake_case com prefixo `idx_`       |
| Primary Keys                  | snake_case com prefixo `pk_`        |
| Foreign Keys                  | snake_case com prefixo `fk_`        |
| Constraints Unique            | snake_case com prefixo `uq_`        |
| Views                         | snake_case                          |
| Functions / Procedures (DB)   | snake_case                          |

---

## Estrutura do Handler / Ponto de Entrada

{{EXEMPLO_HANDLER}}

---

## Variáveis de Ambiente

- Todas as configurações de ambiente são lidas via variáveis de ambiente.
- Nunca hardcode URLs, credenciais ou configurações sensíveis no código.
- Variáveis obrigatórias para execução:

{{VARIAVEIS_DE_AMBIENTE}}

---

## Tratamento de Erros

- Erros operacionais (entrada inválida, campo ausente) retornam código `400`.
- Erros de infraestrutura retornam código `500`.
- Erros de contrato (payload fora do formato esperado) retornam `200` com `status: "error"` no body.
- Nunca deixe exceções não tratadas propagarem sem retornar uma resposta estruturada.

---

## Proibições

- Não modificar arquivos gerados (ex: `dist/`, artefatos de build).
- Não introduzir bibliotecas não listadas em `docs/guidelines/stacks.md`.
- Não bypassar as camadas de serviço ou repositório.
- Não usar `print` para logs; use um mecanismo de logging estruturado.

{{PROIBICOES_ADICIONAIS}}
