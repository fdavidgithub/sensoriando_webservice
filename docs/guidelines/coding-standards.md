# Padrões de Código — Sensoriando Webservice

## Linguagem

Todo código-fonte em **inglês**: identificadores, nomes de arquivo, comentários
e mensagens de log.

O texto visível ao usuário permanece em **português**.

---

## Convenções de Nomenclatura

| Elemento | Padrão |
|---|---|
| Componentes React | PascalCase, arquivo `PascalCase.tsx` |
| Funções e variáveis (TS) | camelCase |
| Tipos e interfaces (TS) | PascalCase |
| Constantes (TS) | UPPER_SNAKE_CASE |
| Módulos TS | `camelCase.ts` |
| Classes (Python) | PascalCase |
| Funções e variáveis (Python) | snake_case |
| Módulos Python | snake_case |

---

## Estrutura das Telas

Uma view busca dados por `useApi` e compõe componentes. Componentes de
apresentação recebem tudo por props e não fazem rede.

```tsx
export default function PublicHome() {
  const things = useApi(() => listPublicThings(filters), [search]);

  return (
    <section className="cards">
      {things.loading && <Loading />}
      {things.error && <ErrorBanner message={things.error} />}
      {things.data?.length === 0 && <EmptyState />}
      {things.data && things.data.length > 0 && (
        <ul>{things.data.map((thing) => <ThingCard key={thing.uuid} thing={thing} />)}</ul>
      )}
    </section>
  );
}
```

Nenhuma tela monta URL na mão: toda chamada passa por `api/endpoints.ts`.

---

## Tratamento de Erros

- Toda tela trata três estados: carregando, erro e vazio.
- Toda falha da API chega como `ApiError`, com `status` 0 para falha de rede.
- Um 404 de rota marcada como pendente vira a mensagem
  `Recurso ainda não disponível na API`.
- Falha de rede nunca resulta em tela branca.

---

## Configuração

- Nenhuma URL, credencial ou identificador de conta fixado em código.
- A URL da API é resolvida no build a partir do CloudFormation.
- Nomes de recurso derivam do `.env` (`SENSORIANDO_ENVIRONMENT`, `AWS_REGION`).

---

## Proibições

- Não usar `eval()` nem `new Function()`.
- Não modificar artefatos de build (`web/dist/`, `infra/cdk.out/`).
- Não introduzir bibliotecas fora de `docs/guidelines/stacks.md`.
- Não fazer rede a partir de componentes de apresentação.
- Não converter nem arredondar valores de sensor no front-end — a API é quem
  entrega o valor pronto (decisão D4 do documento de design).
- Não persistir o ID token: ele vive só em memória (`auth/session.ts`) e some
  ao fechar a aba. Só o refresh token vai para o `localStorage`. Ver a decisão
  D3 do spec de autenticação.
- Não tratar `AuthGate` como decisão única: uma sessão já aprovada pode
  expirar no meio do uso, e o gate precisa reagir a isso (`onSessionExpired`
  em `auth/session.ts`), não só decidir uma vez no mount.
