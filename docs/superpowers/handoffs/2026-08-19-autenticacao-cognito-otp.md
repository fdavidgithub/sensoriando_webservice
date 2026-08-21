# Handoff — Autenticação via Cognito com OTP por e-mail

**Para:** o agente que vai implementar
**Data:** 2026-08-19
**Repositório:** `/mnt/storage/git/sensoriando_webservice`, branch `feat/autenticacao-cognito-otp`

---

## 1. O que você vai fazer

Trocar o portão de sessão falso deste SPA por autenticação real **sem senha**: o
usuário informa o e-mail, recebe um código de uso único e o digita. E ligar as
telas privadas às rotas de conta da API.

O SPA continua um bundle estático que **só consome a API**. Ele não fala com o
Cognito, não carrega biblioteca de autenticação e não conhece pool id nem client
id — quem conversa com o Cognito é o `SENSORIANDO_API`.

O trabalho já está inteiramente especificado. Dois documentos carregam tudo:

| Documento | Papel |
|---|---|
| `docs/superpowers/specs/2026-08-19-autenticacao-cognito-otp-design.md` | As sete decisões, com a razão de cada uma, e o que ficou fora |
| `docs/superpowers/plans/2026-08-19-autenticacao-cognito-otp.md` | 10 tasks, com o código real de cada arquivo |

Leia os dois antes de escrever a primeira linha.

---

## 2. Como executar

**Use a skill `superpowers:subagent-driven-development`.** Invoque-a antes de
começar e siga o que ela mandar.

O regime é: um subagente novo por task, revisão em duas etapas entre uma task e
a seguinte. Cada task termina num entregável testável de forma independente e
declara, num bloco `Interfaces`, o que consome das anteriores e o que produz
para as seguintes — um subagente que só enxerga a própria task trabalha a partir
desse bloco.

Execute as tasks **em ordem**. As dependências entre elas são reais: a Task 3
quebra a compilação de `SignUp.tsx` e `Account.tsx` de propósito, e só as Tasks
6 e 9 fecham os tipos de novo.

### Branch, e nada de worktree

Trabalhe **direto no diretório do repositório**, na branch
`feat/autenticacao-cognito-otp`, que já existe e já está com o commit dos
documentos. **Não crie worktree.** Se alguma skill sugerir isolar o trabalho num
worktree, ignore essa parte: a instrução do dono do repositório é trabalhar na
branch mesmo.

```bash
cd /mnt/storage/git/sensoriando_webservice
git branch --show-current   # deve responder: feat/autenticacao-cognito-otp
```

`AGENTS.md` proíbe commit em `main` e em `develop`. Commite a cada task, com as
mensagens que o plano já traz.

---

## 3. Estado do repositório agora

Nada foi implementado. O que existe é documentação:

```
docs/superpowers/specs/2026-08-19-autenticacao-cognito-otp-design.md   ← o design
docs/superpowers/plans/2026-08-19-autenticacao-cognito-otp.md          ← o plano
docs/superpowers/handoffs/2026-08-19-autenticacao-cognito-otp.md       ← este arquivo
```

O resto é o SPA em React sobre Vite, publicado em S3 + CloudFront por uma stack
CDK em `infra/`.

| Comando | O quê |
|---|---|
| `cd web && npm test` | Toda a suíte do SPA (vitest) |
| `cd web && npm run build` | `tsc -b` e o bundle — é aqui que erro de tipo aparece |
| `make test` | SPA e síntese do CDK |

Os testes ficam **ao lado do módulo**, como `client.test.ts` ao lado de
`client.ts`. Siga isso.

---

## 4. O que a exploração já apurou

São fatos verificados no código, não suposições.

### O portão atual é assumidamente decorativo

`web/src/auth/session.ts` diz no próprio docstring: *"A convenience gate, not a
security boundary […] the gate only keeps the private screens out of the way
until real authentication (Cognito) lands."* Este trabalho é o "until".

Consequência prática: **não há usuário real para migrar.** Uma sessão antiga no
`localStorage` tem `username` e nenhum refresh token; a Task 1 a trata como
`null` de propósito, e o usuário simplesmente entra de novo.

### Nenhuma biblioteca nova de runtime

Como a API intermedia o Cognito, o SPA **não precisa** de `oidc-client-ts` nem
`amazon-cognito-identity-js`. O `docs/guidelines/stacks.md` fica intacto na
seção de bibliotecas permitidas.

As Tasks 4 e 5 instalam `@testing-library/*` e `jsdom` como **devDependencies** —
são os primeiros testes de componente do repositório. Isso é permitido e o plano
manda registrar no `stacks.md`, na seção de Desenvolvimento, onde `vitest` e
`@types/*` já estão.

### O build não muda

`vite.config.ts` já descobre a URL da API no CloudFormation via
`scripts/resolve_api_url.py`. Pool id e client id **não** são injetados, porque o
navegador nunca os usa.

### Os tipos que o `endpoints.ts` declara hoje não batem com o banco

`PrivateAccount` tem `first_name`/`last_name`; o Odoo tem um `name` só, e
`res.partner.name` é um campo único. `AccountInput` tem `password`; não há senha
nesta plataforma. A Task 3 corrige os dois.

### `web_stack.py` invalida o CloudFront

`distribution_paths=["/*"]` no `BucketDeployment`: o bundle novo propaga assim
que o deploy termina, sem espera de TTL.

---

## 5. As sete decisões, em uma linha cada

| # | Decisão |
|---|---|
| D1 | Nenhuma biblioteca de runtime nova |
| D2 | Nada de novo no build: sem pool id, sem client id |
| D3 | ID token só em memória; refresh token no `localStorage` |
| D4 | Sessão de 30 dias, sem deslizar |
| D5 | Renovação com promessa compartilhada |
| D6 | `name` único, sem `first_name`/`last_name` |
| D7 | Unidade preferida vai para o `localStorage` |

A razão de cada uma está na seção 3 do spec.

---

## 6. A dependência do outro repositório

**Duas tasks aqui dependem de um resultado que só a AWS real dá.**

O plano do `SENSORIANDO_API` tem, ao fim da fase 1 dele, uma verificação
obrigatória: publicar e rodar um cadastro e um login de ponta a ponta. Duas das
três coisas que ela valida decidem o formato de módulos deste repositório:

- **Se `POST /accounts/confirm` não devolver tokens**, o cadastro não entra
  logado, e a Task 6 (`SignUp.tsx`) tem que mandar o usuário ao login.
- **Se o `SECRET_HASH` sobre o e-mail não for aceito**, `login()` e `verifyOtp()`
  mudam de assinatura na Task 3, e a tela da Task 5 junto.

**Confirme o resultado dessa verificação antes de começar as Tasks 3, 5 e 6.**
As Tasks 1 e 2 (`session.ts` e `client.ts`) não dependem dela e podem começar a
qualquer momento.

---

## 7. Checkpoints

```bash
# Fase 1 (após a Task 7)
cd web && npm test && npm run build
grep -rn "getIdToken\|setIdToken" src --include=*.tsx   # nada fora de auth/ e api/

# Fase 3 (após a Task 10)
cd web && npm test && npm run build
grep -rn "first_name\|savePreferredUnit\|password" src   # nada
grep -rn "portão de conveniência\|convenience gate" ../docs ../web/src   # nada
```

O `npm run build` importa tanto quanto o `npm test`: é o `tsc -b` que pega os
tipos trocados na Task 3 e não fechados até a Task 9.

---

## 8. Quando considerar pronto

- `npm test` e `npm run build` passam.
- Um F5 numa tela privada **não** desloga: o `AuthGate` renova antes de
  renderizar.
- O `localStorage` do navegador, após login, contém `username` e
  `refreshToken` — e **nenhum ID token**. Confira no DevTools.
- Cinco telas privadas carregando ao mesmo tempo disparam **uma** chamada a
  `/auth/refresh`, não cinco. O teste de renovação concorrente da Task 2 cobre
  isso, mas vale ver na aba Network.
- A aba Perfil mostra um campo Nome, nenhum Sobrenome, e o E-mail somente
  leitura.

---

## 9. O que não fazer

- **Não** acrescente biblioteca de runtime. Em especial nenhuma de autenticação:
  se você sentiu falta de uma, o desenho foi mal entendido — o SPA não fala com
  o Cognito.
- **Não** persista o ID token no `localStorage` nem em cookie. Ele vive em
  memória, e isso é a decisão D3.
- **Não** implemente `savePreferredUnit` contra a API. Não existe tabela para
  isso; a preferência vai para `lib/prefs.ts` (D7).
- **Não** faça a tela de login tentar descobrir se o e-mail existe antes de
  pedir o código. A API responde igual para os dois casos de propósito.
- **Não** faça componentes de `components/` buscarem dados. Quem busca é
  `views/` (`docs/guidelines/architecture.md`).
- **Não** use `eval()` nem `new Function()`.
- **Não** crie worktree. Trabalhe na branch.
- **Não** commite em `main` nem em `develop`, e **não** faça merge nem abra PR
  por conta própria — a decisão é do usuário (`AGENTS.md`).

---

## 10. Ao terminar

Relate:

1. O resultado dos checkpoints da seção 7, com a saída real dos comandos.
2. As versões exatas das devDependencies instaladas nas Tasks 4 e 5, e a
   confirmação de que entraram no `stacks.md`.
3. Qualquer desvio do plano, com a razão — em especial se a verificação do outro
   repositório (seção 6) tiver obrigado a mudar as Tasks 3, 5 ou 6.
4. O que ficou pendente: a unidade preferida por conta continua local, e voltará
   a ser assunto se um dia o `SENSORIANDO_CORE` ganhar a tabela.

Se algo no plano estiver errado ou impossível, **diga em vez de improvisar**.
