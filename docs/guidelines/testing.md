# Diretrizes de Testes — Sensoriando Webservice

## Fluxo de Desenvolvimento — TDD

Toda implementação neste projeto segue o ciclo **Red → Green → Refactor**:

1. **Red** — escreva o teste antes do código de produção. O teste deve falhar.
2. **Green** — escreva o mínimo de código necessário para o teste passar.
3. **Refactor** — melhore o código sem quebrar os testes.

Nunca escreva código de produção sem um teste que o justifique.

---

## Frameworks

- **SPA (`web/`)** — **Vitest**, executado via `npm test` (`vitest run`). Os
  testes são colocalizados com o módulo que testam, no padrão `src/**/*.test.ts`.
- **Infraestrutura (`infra/`)** — **pytest**, executado via
  `./.venv/bin/python -m pytest tests/unit -v` (ou `make test-infra`).

O alvo `make test` roda as duas suítes (`test-web` e `test-infra`).

---

## Estrutura de Testes

```
web/src/**/*.test.ts   → testes colocalizados com o módulo (api, auth, lib)
infra/tests/unit/      → testes de síntese da stack CDK (settings, web_stack)
```

Não há testes e2e nem suíte de integração neste repositório: o SPA é estático e
depende apenas da Sensoriando API, e a infraestrutura é validada por síntese.

---

## Testes Unitários

### Regras

- Cada módulo do SPA deve ter um arquivo de teste correspondente, no mesmo
  diretório (`*.test.ts`).
- Testes **não devem depender de serviços externos reais**: `fetch`, `localStorage`
  e variáveis de ambiente são mockados ou stubados.
- Os testes da infra não sobem stack nem chamam a AWS; validam os objetos CDK
  sintetizados em memória.

---

## Cobertura

- Toda nova lógica implementada deve ter testes correspondentes antes do merge.
- A cobertura é verificada com as ferramentas definidas em
  `docs/guidelines/stacks.md`.
- Arquivos de configuração de infraestrutura não precisam de cobertura unitária
  obrigatória.

---

## Execução

```bash
make test          # suíte completa (web + infra)
make test-web      # somente os testes do SPA
make test-infra    # somente os testes da infra
```

---

## Proibições

- Proibido conectar em serviços externos reais durante os testes.
- Proibido usar `time.sleep` em testes.
- Proibido usar variáveis de ambiente reais; sempre usar mecanismo de mock/patch
  para variáveis de ambiente.
