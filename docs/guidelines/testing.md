# Diretrizes de Testes — {{NOME_PROJETO}}

## Fluxo de Desenvolvimento — TDD

Toda implementação neste projeto segue o ciclo **Red → Green → Refactor**:

1. **Red** — escreva o teste antes do código de produção. O teste deve falhar.
2. **Green** — escreva o mínimo de código necessário para o teste passar.
3. **Refactor** — melhore o código sem quebrar os testes.

Nunca escreva código de produção sem um teste que o justifique.

---

## Framework

{{FRAMEWORK_TESTES}}

---

## Estrutura de Testes

```
tests/
├── units/          → testes unitários por módulo
│   ├── conftest.py
│   └── test_<module_name>.py
├── integration/    → testes de contrato e fluxo entre componentes
│   ├── conftest.py
│   └── test_<flow_name>.py
└── e2e/            → testes end-to-end contra o ambiente real
    ├── conftest.py
    ├── features/
    │   └── <flow_name>.feature
    └── test_<flow_name>.py
```

---

## Testes Unitários (`tests/units/`)

### Regras

- Cada módulo deve ter um arquivo de teste correspondente em `tests/units/`.
- Testes unitários **não devem depender de serviços externos reais**.
- Dependências externas devem ser substituídas por mocks ou stubs.

### Padrão de Carregamento de Módulo

{{EXEMPLO_CARREGAMENTO_MODULO}}

---

## Testes de Integração (`tests/integration/`)

### Regras

- Testam o contrato entre componentes e o fluxo completo sem dependência de infraestrutura real.
- Utilizam fakes locais definidos em `tests/integration/conftest.py`.

### Fixtures Disponíveis

{{FIXTURES_INTEGRACAO}}

---

## Cobertura

- Toda nova lógica implementada deve ter testes correspondentes antes do merge.
- A cobertura é verificada com as ferramentas definidas em `docs/guidelines/stacks.md`.
- Arquivos de configuração de infraestrutura não precisam de cobertura unitária obrigatória.

---

## Testes E2E (`tests/e2e/`)

### Regras

- Testam o fluxo completo contra o ambiente real.
- Requerem credenciais e arquivo de configuração de ambiente (`.env.e2e`).
- Executados manualmente via comando dedicado (nunca junto com o `pytest` geral).
- O ambiente de teste deve estar provisionado antes de rodar.

### Ciclo de Vida

{{COMANDOS_E2E}}

---

## Execução

```bash
{{COMANDOS_EXECUCAO_TESTES}}
```

---

## Proibições

As regras abaixo aplicam-se às camadas **units** e **integration**. A camada **e2e** é uma exceção explícita — ela conecta em serviços reais por design.

- Proibido conectar em serviços externos reais durante os testes.
- Proibido usar `time.sleep` em testes.
- Proibido usar variáveis de ambiente reais; sempre usar mecanismo de mock/patch para variáveis de ambiente.
