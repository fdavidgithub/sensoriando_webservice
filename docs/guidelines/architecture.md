# Arquitetura do Sistema Sensoriando Webservice

## Visão Geral

O Sensoriando Webservice é a camada de apresentação da plataforma Sensoriando
(*Hub de Sensores*). É um SPA estático: não tem servidor de aplicação, não tem
banco de dados e não guarda estado no servidor.

Todos os dados vêm da Sensoriando API, que por sua vez lê o PostgreSQL populado
pelo Sensoriando Core via MQTT.

```
Navegador → CloudFront → S3 (bundle estático)
    │
    └── HTTPS → API Gateway → Lambdas → PostgreSQL (Neon)
                     │            └────→ Cognito (identidade)
                     └── authorizer valida o ID token
```

---

## Módulos Principais

```
web/src/
  api/          client.ts     → única camada que conhece fetch; normaliza erro em ApiError
                endpoints.ts  → uma função por rota; marca as rotas ainda inexistentes
                types.ts      → formas dos dados da API
  auth/         session.ts    → refresh token no localStorage, ID token em memória
                AuthGate.tsx  → renova antes de renderizar; redireciona quem não tem sessão
  lib/          filters.ts    → filtros ↔ query string
                prefs.ts      → período e tipo de gráfico em localStorage
                format.ts     → rótulos de gráfico por período
                country.ts    → alpha-2 → nome, via Intl.DisplayNames
                useApi.ts     → hook de carregamento/erro por view
  components/                 → apresentação; recebem dados por props, não fazem rede
  views/                      → telas; buscam dados e compõem componentes

infra/stacks/   settings.py   → nomes derivados do ambiente
                web_stack.py  → bucket privado + CloudFront + publicação do build

scripts/        resolve_api_url.py    → descobre a URL da API no CloudFormation
                config_parameters.py  → parâmetros no SSM
```

---

## Fluxo de Dados

1. No build, `vite.config.ts` chama `scripts/resolve_api_url.py`, que lê o output
   `SensoriandoApiUrl` da stack `sensoriando-<ambiente>-api` no CloudFormation e
   injeta a URL no bundle.
2. No navegador, cada view chama `useApi` com uma função de `api/endpoints.ts`.
3. `api/client.ts` faz a requisição e converte qualquer falha em `ApiError`.
4. A view renderiza um de três estados: carregando, erro ou vazio.
5. Nas rotas privadas, `client.ts` injeta o ID token (`Authorization: Bearer`) e,
   num 401, renova o token exatamente uma vez antes de repetir a requisição — a
   renovação é compartilhada entre chamadas concorrentes, então várias telas
   abrindo juntas disparam uma única troca de token.

Rotas que a API ainda não expõe estão marcadas em `endpoints.ts`: um 404 vindo
delas vira a mensagem `Recurso ainda não disponível na API`, distinta de um erro
genérico, para que uma pendência conhecida não se confunda com um defeito.

---

## Decisões de Arquitetura

Registradas com a razão em
`docs/superpowers/specs/2026-08-12-migracao-react-cdk-design.md`.
