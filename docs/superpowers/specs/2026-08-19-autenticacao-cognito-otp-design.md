# Autenticação via Cognito com OTP por e-mail — sensoriando_webservice

Data: 2026-08-19
Repositórios envolvidos: `sensoriando_webservice` (este) e `SENSORIANDO_API`
Spec par: `SENSORIANDO_API/docs/superpowers/specs/2026-08-19-autenticacao-cognito-otp-design.md`

---

## 1. Objetivo

Trocar o portão de sessão falso por autenticação real, sem senha: o usuário
informa o e-mail, recebe um código de uso único e o digita.

O SPA continua sendo um bundle estático que **só consome a API**. Ele não fala
com o Cognito, não carrega biblioteca de autenticação e não conhece pool id nem
client id. Toda a conversa com o Cognito acontece do lado servidor, nos
endpoints descritos no spec par.

Este spec cobre o lado navegador.

---

## 2. Estado de partida

`web/src/auth/session.ts` declara o que ele é hoje, no próprio docstring:

> A convenience gate, not a security boundary. […] the gate only keeps the
> private screens out of the way until real authentication (Cognito) lands.

Não há senha, e as rotas `/private` da API servem a conta fixa de
`PRIVATE_ACCOUNT_USERNAME` independentemente de quem entrou. Este spec é o
"until Cognito lands".

Seis rotas estão marcadas como pendentes em `api/endpoints.ts` pela função
`pending()`. Cinco passam a existir; uma sai (seção 7).

---

## 3. Decisões

| # | Decisão | Razão |
|---|---------|-------|
| D1 | Nenhuma biblioteca nova | Como a API intermedia o Cognito, `oidc-client-ts` e `amazon-cognito-identity-js` são desnecessários. `stacks.md` fica intacto na lista de bibliotecas permitidas. |
| D2 | Nada de novo no build | A URL da API já vem do CloudFormation via `scripts/resolve_api_url.py`. Pool id e client id não são injetados porque o navegador nunca os usa. |
| D3 | ID token **só em memória**; refresh token em `localStorage` | Reduz a janela em que um XSS captura o token que dá acesso imediato. O refresh token persiste para o usuário continuar logado entre visitas. |
| D4 | Sessão de 30 dias, sem deslizar | Prazo do refresh token no Cognito, contado da emissão. Passados 30 dias o usuário refaz o OTP mesmo tendo usado todo dia. |
| D5 | Renovação com promessa compartilhada | Várias views carregam em paralelo; sem isso, cinco 401 simultâneos disparariam cinco renovações. |
| D6 | `name` único, sem `first_name`/`last_name` | `res.partner.name` no Odoo é um campo só. Quebrar por espaço seria adivinhação. |
| D7 | Unidade preferida vai para `localStorage` | Não existe tabela no schema que ligue conta a unidade. `lib/prefs.ts` já guarda período e tipo de gráfico exatamente assim. |

---

## 4. Sessão

### 4.1 `web/src/auth/session.ts` — reescrito

Deixa de ser portão de conveniência. Passa a guardar:

- em `localStorage`: `{ username, refreshToken }`
- em variável de módulo, **fora do `localStorage`**: o ID token e o instante em
  que expira

```ts
export interface Session { username: string; }

export function readSession(): Session | null;
export function writeSession(username: string, refreshToken: string): void;
export function clearSession(): void;

export function readRefreshToken(): string | null;
export function getIdToken(): string | null;      // memória
export function setIdToken(token: string, expiresIn: number): void;
export function clearIdToken(): void;
```

A chave `sensoriando.session` do `localStorage` é reaproveitada. Uma sessão
antiga, gravada pelo portão falso, tem `username` mas não tem `refreshToken`:
`readSession()` devolve `null` nesse caso, e o usuário cai no login. É a
migração — não há usuário real para preservar, já que o portão nunca autenticou
ninguém.

O docstring do módulo é reescrito: deixa de dizer que não é fronteira de
segurança, e passa a explicar por que o ID token não é persistido.

### 4.2 `web/src/api/client.ts` — alterado

- `request()` recebe se a chamada é autenticada. Sendo, injeta
  `Authorization: Bearer <idToken>`.
- Sem ID token em memória mas com refresh token guardado (caso do boot), renova
  antes de enviar.
- Resposta `401` numa chamada autenticada: renova **uma vez** e repete a
  requisição. Segundo `401` → limpa a sessão e propaga um `ApiError` que o
  `AuthGate` reconhece como "precisa entrar de novo".
- A renovação é uma **promessa compartilhada** em variável de módulo: chamadas
  concorrentes aguardam a mesma, e ela é limpa ao resolver ou rejeitar.

`ApiError` continua com a mesma forma. A distinção entre "servidor disse não" e
"não houve servidor" pelo `status === 0` permanece.

### 4.3 `web/src/auth/AuthGate.tsx` — alterado

Hoje é síncrono: lê o `localStorage` e decide. Passa a ter três estados, porque
no boot existe refresh token mas ainda não existe ID token:

1. sem sessão → `Navigate` para `/users/login`
2. com sessão e sem ID token → renova, mostrando `<Loading />`
3. com ID token → renderiza os filhos

Sem o estado 2, a primeira chamada de toda tela privada nasceria 401.

---

## 5. Telas

### 5.1 `views/LoginPage.tsx` — reescrito

Duas etapas, com estado local `"email" | "code"`:

1. **E-mail** — um campo, botão "Receber código". Chama `login({ email })` e
   guarda `session` e `destination` da resposta.
2. **Código** — mostra "Enviamos um código para `f***@e***.com`", campo de 6
   dígitos, botão "Entrar", e um "Reenviar código" que volta à etapa 1.

Sucesso: `writeSession(username, refresh_token)`, `setIdToken(...)`, navega
para `/home/private`.

O texto atual ("A autenticação ainda não foi implementada") sai. Entra um aviso
de que a sessão dura 30 dias (D4).

Como a API não distingue e-mail cadastrado de não cadastrado (D10 do spec par),
a etapa 1 **sempre** avança para a etapa 2. Um e-mail inexistente falha só na
etapa 2, com "código inválido". Isso é deliberado e a tela não deve tentar
contornar.

### 5.2 `views/SignUp.tsx` — reescrito

Campos: `username` (máx. 20), `name`, `email`, `phone` (opcional), `city`,
`state`, `country`. **O campo `password` sai** — não há senha.

Duas etapas, como o login:

1. **Formulário** → `signUp(form)` → 202 com `destination`.
2. **Código** → `confirmSignUp({ username, code })` → 201 com os tokens.

Confirmado, o usuário **já entra logado** (o `ConfirmSignUp` do Cognito devolve
uma `Session` que a API troca por tokens). Não digita código duas vezes: grava a
sessão e navega para `/home/private`.

O `502` do spec par — conta criada mas cadastro no ERP falhou — mostra a
mensagem da API e leva ao login mesmo assim, porque o próximo login refaz o
provisionamento.

### 5.3 `views/Account.tsx` — alterado

- **Aba Perfil**: passa a consumir `GET/PUT /accounts/private` de verdade. O
  formulário troca `first_name`/`last_name` por um campo `name` e ganha
  `phone`. O campo `email` fica **somente leitura**: é o que autentica, e não é
  alterável por esta tela.
- **Aba Centrais**: `linkThing` deixa de ser `pending()`. Trata `404` (central
  inexistente) e `409` (já vinculada a outra conta) com mensagens próprias.
- **Aba Sensores**: `listSensorUnits` deixa de ser `pending()`;
  `savePreferredUnit` some, e a escolha passa a gravar em `lib/prefs.ts`. A tela
  não muda de aparência — muda o destino do dado.

### 5.4 `components/Header.tsx` — alterado

Já lê `readSession()` e já tem "Sair" chamando `clearSession()`. Passa a limpar
também o ID token em memória. O resto continua igual.

---

## 6. `api/endpoints.ts`

**Funções novas**

```ts
export function signUp(input: AccountInput): Promise<{ destination: string }>;
export function confirmSignUp(input: { username: string; code: string }): Promise<AuthTokens>;
export function resendCode(input: { username: string }): Promise<{ destination: string }>;
export function login(input: { email: string }): Promise<{ session: string; destination: string }>;
export function verifyOtp(input: { email: string; code: string; session: string }): Promise<AuthTokens>;
export function refresh(input: { refresh_token: string; username: string }): Promise<{ id_token: string; expires_in: number }>;
```

**Saem de `pending()`**: `listSensorUnits`, `readPrivateAccount`,
`savePrivateAccount`, `createAccount` (vira `signUp`), `linkThing`.

**Sai do arquivo**: `savePreferredUnit` e o tipo `PreferredUnitInput`.

**Tipos alterados**: `AccountInput` perde `password`, troca
`first_name`/`last_name` por `name` e ganha `phone?`. `ProfileInput` e
`PrivateAccount` fazem a mesma troca; `PrivateAccount` ganha `phone`.

`PENDING_MESSAGE` e a função `pending()` **permanecem** — continuam úteis para a
próxima rota que a API ainda não expuser.

---

## 7. `lib/prefs.ts`

Ganha a unidade preferida por sensor, no mesmo padrão das existentes:

```ts
export function readPreferredUnit(sensorId: number): number | null;
export function writePreferredUnit(sensorId: number, unitId: number): void;
```

Chave `unit<sensorId>`, alinhada ao `chart<sensorId>` já usado.

Motivo de a preferência não ir para o servidor: das 25 tabelas do schema,
nenhuma liga conta a unidade. `SensorsUnits` é catálogo por sensor, com um
`isdefault` global. Criar a tabela exigiria alterar o `SENSORIANDO_CORE`, que
está fora do escopo. Está registrado no spec par, seção 12.

---

## 8. Testes

`vitest`, com os arquivos `*.test.ts` ao lado do módulo, como já é a prática do
repositório.

- **`session.test.ts`** (existe, reescrito): ID token não persiste no
  `localStorage`; sessão antiga sem `refreshToken` é lida como `null`;
  `clearSession` limpa os dois.
- **`client.test.ts`** (existe, ampliado): header injetado só em chamada
  autenticada; `401` renova e repete; segundo `401` limpa a sessão; **duas
  chamadas concorrentes disparam uma renovação só**.
- **`endpoints.test.ts`** (existe, ampliado): as seis funções novas montando
  método, caminho e corpo certos.
- **`prefs.test.ts`** (existe, ampliado): unidade preferida, incluindo valor
  ausente e valor inválido no `localStorage`.
- **Telas**: login em duas etapas; cadastro que confirma e entra logado; perfil
  com `email` somente leitura.

---

## 9. Ordem de entrega

Espelha as três fases do spec par.

1. **Autenticação** — `session.ts`, `client.ts`, `AuthGate.tsx`,
   `LoginPage.tsx`, `SignUp.tsx`, `Header.tsx`, e as seis funções de
   `endpoints.ts`.
2. **O corte** — nenhuma mudança neste repositório. É o deploy do authorizer no
   lado da API.
3. **Conta** — `Account.tsx` nas três abas, `prefs.ts`, e as rotas de conta
   saindo de `pending()`.

**A ordem de deploy é obrigatória**: API fase 1 → **este repositório fase 1** →
API fase 2. Publicar o authorizer antes do frontend novo derruba todas as telas
privadas.

---

## 10. Fora de escopo

- Alterar `email` ou `username` depois do cadastro.
- Recuperação de conta por outro canal. Sem senha não há "esqueci a senha":
  quem perde o e-mail perde a conta.
- Login federado, passkeys, SMS.
- Cookie `HttpOnly` para o refresh token: exigiria pôr a API atrás do mesmo
  CloudFront do SPA, que hoje são domínios distintos. Mudança de infra
  descartada para este trabalho.

---

## 11. Riscos

| Risco | Mitigação |
|---|---|
| Refresh token em `localStorage` é alcançável por XSS | O ID token, que dá acesso imediato, não é persistido. `stacks.md` já proíbe `eval()` e `new Function()` em `web/`. |
| Renovação concorrente | Promessa compartilhada, com teste dedicado (D5). |
| Sessão de 30 dias expirando no meio do uso | O `client.ts` trata o `401` da renovação levando ao login com mensagem clara, não com erro genérico. |
| Usuário fecha a aba entre cadastro e código | O código chega por e-mail e o `username` está no formulário; ele reabre o cadastro e usa "Reenviar código". Nenhum dado se perde: os atributos ficam no Cognito até a confirmação. |

---

## 12. Documentação a atualizar

- `docs/guidelines/architecture.md` — o módulo `auth/` deixa de ser "portão de
  conveniência"; descrever a renovação no `client.ts` e o novo fluxo de dados.
- `docs/guidelines/stacks.md` — registrar que **nenhuma biblioteca foi
  adicionada**, e por quê. Cognito entra na lista de serviços, mas como serviço
  alcançado *pela API*, não pelo SPA.
