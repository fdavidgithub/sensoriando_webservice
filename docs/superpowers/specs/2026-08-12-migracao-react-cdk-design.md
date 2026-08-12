# Migração do Sensoriando Webservice: Django → React + AWS CDK

**Data:** 2026-08-12
**Status:** aprovado, aguardando plano de implementação

## Problema

O `sensoriando_webservice` é hoje uma aplicação Django que faz duas coisas: serve
uma API REST (`api/`) e renderiza páginas HTML no servidor (`overview/`,
`sensors/`, `users/`, `templates/`). A implantação é self-hosted via
`docker-compose`.

A API já foi migrada para outro repositório. O `SENSORIANDO_API` expõe os mesmos
oito endpoints em AWS Lambda atrás de API Gateway, lendo o mesmo PostgreSQL
(Neon). O app `api/` deste repositório virou, portanto, duplicação: dois lugares
servindo o mesmo contrato, livres para divergir.

Sobra para este repositório um único papel: **ser o front-end**. Este documento
descreve a substituição da camada web Django por um SPA em React, publicado como
site estático em S3 + CloudFront, provisionado por AWS CDK.

## Objetivo

Um SPA React que reproduz fielmente as telas atuais, consome o `SENSORIANDO_API`
por HTTP, descobre a URL da API dinamicamente, e é implantado por uma stack CDK
neste repositório. Nenhum código Python de aplicação permanece.

## Não-objetivos

- **Não** alterar o `SENSORIANDO_API` nem qualquer outro repositório. `../UDUU` e
  `../SENSORIANDO_API` são referência de leitura apenas.
- **Não** implementar autenticação real. Entra depois, provavelmente com Cognito.
- **Não** redesenhar a interface. O visual atual é portado como está.
- **Não** apontar o DNS de `web.sensoriando.com.br` para a nova infraestrutura.
  Isso é uma decisão de corte posterior, fora deste escopo.

---

## Decisões

Registradas com a razão, porque cada uma fecha alternativas que parecem
razoáveis à primeira vista.

### D1 — A URL da API é resolvida no build

`web/vite.config.ts` executa `scripts/resolve_api_url.py`, que consulta o output
`SensoriandoApiUrl` da stack `sensoriando-<ambiente>-api` no CloudFormation, e
injeta o valor em `VITE_API_BASE_URL`.

É exatamente o mecanismo já em uso em `UDUU/dashboard` e `SENSORIANDO_API` — um
só modelo mental para os três repositórios, e o script existe pronto para portar.

Alternativas descartadas: um `config.json` lido em runtime (a consulta ao
CloudFormation não desaparece, só muda do Vite para o synth do CDK, em troca de
um estado de carregamento e um caminho de erro a mais em toda tela); e um
behavior `/api/*` no CloudFront com origin no API Gateway (elimina CORS, mas o
CORS da API já é `ALL_ORIGINS`, então resolveria um problema inexistente, ao
custo de acoplar as duas stacks).

Custo aceito: todo `npm run build` exige credencial AWS válida, e a URL fica
congelada no bundle. Se a API for destruída e recriada com id novo, o SPA aponta
para o vazio até um rebuild. É raro e visível.

### D2 — Login é um portão sem senha

A tela de login tem apenas um botão "Entrar", que grava uma flag em
`localStorage`. Sem usuário, sem senha, sem credencial no `.env` nem no SSM.

A razão é que num SPA estático não existe segredo: qualquer senha embutida no
bundle é legível por qualquer pessoa com a URL, via DevTools. Um usuário e senha
falsos dariam a aparência de proteção sem entregar nenhuma. Além disso, os
endpoints `/private` da API servem a conta fixa de `PRIVATE_ACCOUNT_USERNAME`
**independentemente de quem logou** — o portão controla o acesso à tela, nunca
aos dados.

Isso fica documentado no código (`web/src/auth/session.ts`) e no README como
barreira de conveniência, não de segurança.

### D3 — Publicação apenas na URL do CloudFront

A stack cria S3 + CloudFront e devolve o domínio gerado pela AWS. Sem domínio
próprio, sem certificado ACM, sem Route53.

Assim o `web.sensoriando.com.br` atual permanece no ar, intocado, durante toda a
migração. A validação acontece na URL nova e o corte de DNS vira uma decisão
separada, tomada com o SPA já funcionando.

### D4 — Zero lógica de unidade no front-end

O SPA exibe o valor exatamente como a API o devolve. Nenhuma conversão, nenhum
arredondamento.

Hoje `sensors/views.py` lê `sensorsunits.expression` (uma fórmula em texto, como
`"pv * 1.8 + 32"`), aplica com pandas e arredonda por `sensorsunits.precision`.
Replicar isso em JavaScript exigiria avaliar no navegador uma string vinda do
servidor — e um avaliador aritmético restrito para não usar `eval()`.

A estrutura será alterada depois para que a unidade preferida do usuário fique
gravada no banco e a API já devolva o valor convertido. Escrever o conversor
agora seria construir código com data de validade conhecida.

**Consequência registrada:** enquanto `/data/detail` devolver apenas `dtread`,
`value` e `message`, o gráfico fica sem o símbolo da unidade no rótulo. Quando a
API passar a converter, faz sentido devolver o símbolo junto. Isso é trabalho do
`SENSORIANDO_API`, anotado aqui apenas como nota de contrato.

### D5 — Filtros na query string, não em cookie

Hoje os filtros da home vão para o cookie `setFilterHome` e a página faz
`location.reload()`. No SPA vão para a query string
(`/?sensor=temperatura&sensor_tag=externo`).

O resultado passa a ser compartilhável por link, o botão voltar do navegador
funciona, e some o recarregamento de página inteira. O comportamento visual —
modal de filtros, clicar numa cidade ou sensor do card para filtrar — é idêntico.

As preferências **puramente visuais** saem de cookie para `localStorage`,
mantendo as mesmas chaves: `chartview` (período exibido) e `chart<id>` (tipo de
gráfico por sensor).

Os cookies `unit<id>` e `precision<id>` **não** migram. Eles existem hoje só para
alimentar a conversão que D4 elimina do front-end; com a unidade preferida indo
para o banco, guardá-los no navegador não teria efeito nenhum. Os seletores de
unidade e precisão da aba Conta→Sensores passam a depender dos endpoints
previstos, como o resto daquela aba.

### D6 — Escritas chamam o endpoint previsto e exibem o erro

As telas de escrita são implementadas por completo, contra o contrato de rotas
definido abaixo. Enquanto essas rotas não existirem no `SENSORIANDO_API`, a
chamada retorna 404 e a tela mostra uma mensagem clara.

Assim o código deste repositório fica pronto: quando a API subir, funciona sem
precisar voltar aqui. As alternativas — botão desabilitado, ou salvar em
`localStorage` — exigiriam uma segunda passagem por cada formulário.

### D7 — Remoção completa do Django, com tag no commit anterior

Saem `api/`, `base/`, `core/`, `overview/`, `sensors/`, `users/`, `templates/`,
`static/`, `manage.py`, `Dockerfile`, `docker-compose.yaml`, `requirements.txt`,
`init.sh`, `run.sh` e `entrypoint.sh`.

Antes disso, a tag git `django-final` marca o último commit funcional. O site em
produção hoje é construído a partir desse código; a tag garante que reconstruí-lo
seja um `git checkout`, não uma arqueologia no histórico.

### D8 — Mecanismo de SSM criado, manifesto vazio

`scripts/config_parameters.py` e o alvo `make config-ensure` são portados do
padrão de referência, com o manifesto de chaves vazio.

As decisões acima esvaziaram a lista de segredos: não há credencial (D2), a URL
da API vem do CloudFormation (D1) e não há domínio nem certificado (D3). As
constantes de comportamento ficam em `web/src/config.ts`, como no
`UDUU/dashboard`.

O mecanismo entra agora para que a primeira chave real — configuração do Cognito,
domínio, ARN de certificado — seja só uma declaração no manifesto.

### D9 — Layout unificado: a home privada e o 404 migram para o design atual

O repositório tem dois layouts convivendo. `index.html`, `detail.html`,
`signin.html`, `signup.html` e `account.html` usam o design atual (`head.html` +
`static/css/style.css`, cards, background em grayscale). `home.html` (a home
privada) e `404.html` ficaram no layout anterior, em Bootstrap via
`common.html`, com `panel panel-primary` e grid `col-sm-*`.

No SPA, as duas passam a usar o layout atual. A home privada reaproveita o mesmo
`ThingCard` da home pública e ganha um painel "Indicadores" com plano, total de
registros e retenção (de `/data/stats/private`).

Reproduzir o Bootstrap legado obrigaria o bundle a carregar dois sistemas de
estilo e preservaria no código novo uma inconsistência que já era dívida.

**Consequência registrada:** é a única diferença visual deliberada em relação à
produção, além das já listadas em D4 e na remoção dos itens do menu.

---

## Arquitetura

```
Navegador → CloudFront → S3 (bundle estático)
    │
    └── HTTPS → API Gateway → Lambdas → PostgreSQL (Neon)
                (SENSORIANDO_API, outro repositório)
```

O SPA é estático. Não há servidor de aplicação neste repositório depois da
migração: toda leitura e escrita passa pelo `SENSORIANDO_API`.

### Layout do repositório

```
sensoriando_webservice/
├── web/                      SPA React + Vite + TypeScript
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts        resolve a URL da API no build
│   ├── public/img/           background, bars, service-1, nosensor
│   └── src/
│       ├── main.tsx
│       ├── App.tsx           rotas
│       ├── config.ts         constantes de comportamento
│       ├── api/              client.ts, endpoints.ts, types.ts
│       ├── auth/             session.ts, AuthGate.tsx, LoginPage.tsx
│       ├── lib/              filters.ts, prefs.ts, format.ts, country.ts
│       ├── components/       Header, Footer, ThingCard, FilterDialog,
│       │                     SensorChart, EmptyState, ErrorBanner
│       ├── views/            PublicHome, PrivateHome, ThingDetail,
│       │                     Account, SignUp, NotFound
│       └── styles/           style.css portado de static/css/
├── infra/                    CDK Python
│   ├── app.py
│   ├── cdk.json
│   ├── requirements.txt
│   ├── stacks/settings.py
│   ├── stacks/web_stack.py
│   └── tests/unit/test_web_stack.py
├── scripts/
│   ├── _dotenv.py
│   ├── resolve_api_url.py
│   └── config_parameters.py
├── Makefile
├── env.example
└── docs/
```

### Unidades e fronteiras

Cada unidade tem um propósito e pode ser entendida sem ler as outras.

| Unidade | Faz | Depende de |
|---|---|---|
| `api/types.ts` | Descreve as formas dos dados da API | nada |
| `api/client.ts` | Única coisa que sabe o que é `fetch`; monta URL, serializa corpo, normaliza erro em `ApiError` | `config.ts` |
| `api/endpoints.ts` | Uma função tipada por rota; marca as rotas ainda inexistentes | `client.ts`, `types.ts` |
| `auth/session.ts` | Lê e grava a flag de sessão | `localStorage` |
| `lib/filters.ts` | Converte query string ↔ objeto de filtros | nada |
| `lib/prefs.ts` | Lê e grava preferências de gráfico | `localStorage` |
| `lib/country.ts` | Código alpha-2 → nome do país | `Intl.DisplayNames` |
| `components/*` | Apresentação; recebem dados por props | nada de rede |
| `views/*` | Buscam dados e compõem componentes | `endpoints.ts`, `lib/*` |

Nenhuma tela monta URL na mão, e nenhum componente de apresentação faz rede.

---

## Rotas do SPA

Os caminhos são os mesmos de hoje, para não quebrar links e favoritos.

| Rota | View | Origem | Protegida |
|---|---|---|---|
| `/` | `PublicHome` | `index.html` | não |
| `/home/private` | `PrivateHome` | `home.html` | sim |
| `/thing/detail/:uuid` | `ThingDetail` | `detail.html` | não |
| `/users/login` | `LoginPage` | `signin.html` | não |
| `/users/signup` | `SignUp` | `signup.html` | não |
| `/users/account/:username/:tab` | `Account` | `account.html` | sim |
| `*` | `NotFound` | `404.html` | não |

O menu perde dois itens: **"Mapa"**, que aponta para `/` porque a rota do mapa
está comentada em `base/urls.py` (funcionalidade morta), e **"API"**, que aponta
para o Swagger do Django, que deixa de existir.

---

## Contrato de API

### Endpoints existentes (`SENSORIANDO_API`)

| Método | Rota | Consumido por |
|---|---|---|
| GET | `/sensors` | filtros da home |
| GET | `/sensors/tags` | filtros da home |
| GET | `/accounts` | — (disponível, sem uso atual) |
| POST | `/things` | `PublicHome` |
| POST | `/things/private` | `PrivateHome`, `Account` |
| POST | `/data/detail` | `ThingDetail` |
| POST | `/data/detail/private` | `ThingDetail` |
| GET | `/data/stats/private` | `PrivateHome`, `Account` |

Filtros aceitos por `/things` e `/things/private`: `thing`, `city`, `state`,
`country`, `sensor`, `thing_tag`, `sensor_tag`. Períodos aceitos por
`/data/detail`: `second` (padrão), `minute`, `hour`, `day`, `month`, `year`.

### Endpoints previstos (ainda não existem)

O React é escrito contra estas rotas. Até existirem, retornam 404 e a tela exibe
"recurso ainda não disponível na API".

| Método | Rota | Serve | Consumido por |
|---|---|---|---|
| GET | `/sensors/units` | unidades disponíveis por sensor, para montar o seletor | Conta→Sensores |
| PUT | `/accounts/private/sensors/units` | gravar unidade e precisão preferidas | Conta→Sensores |
| GET | `/accounts/private` | perfil da conta servida, com e-mail | Conta→Perfil |
| PUT | `/accounts/private` | editar perfil | Conta→Perfil |
| POST | `/accounts` | criar conta | SignUp |
| POST | `/accounts/private/things` | vincular thing à conta | Conta→Things |

### O que cada tela consegue exibir hoje

| Tela | Renderiza | Pendente |
|---|---|---|
| `PublicHome` | completa | — |
| `ThingDetail` | completa | símbolo da unidade no rótulo |
| `PrivateHome` | completa | — |
| `SignUp` | formulário completo | o salvar |
| Conta→Perfil | cidade, estado, país (de `/things/private`), usuário e plano (de `/data/stats/private`) | e-mail; o salvar |
| Conta→Things | completa | vincular thing |
| Conta→Sensores | seletor de tipo de gráfico (`localStorage`) | lista de unidades; seletor de precisão; o salvar |

---

## Infraestrutura

### Stack `sensoriando-<ambiente>-web`

- **Bucket S3** privado: `BLOCK_ALL`, criptografia gerenciada pelo S3, acesso
  exclusivamente por Origin Access Control.
- **Distribuição CloudFront**: `default_root_object = index.html`,
  `REDIRECT_TO_HTTPS`, e as respostas de erro **403 e 404 remapeadas para
  `/index.html` com status 200**. Esse remapeamento é o que faz um F5 em
  `/thing/detail/<uuid>` continuar funcionando: o S3 não conhece essa chave, e
  sem isso devolveria 403.
- **BucketDeployment** publica `web/dist` e invalida `/*`.
- **Output** `SensoriandoWebUrl`.

Se `web/dist` não existir no synth, o upload é pulado com aviso em `stderr` em
vez de quebrar o deploy — mesmo comportamento do `DashboardStack` do UDUU.
Atenção ao mesmo ponto cego de lá: um `dist/` **desatualizado** não é detectado,
e é publicado silenciosamente. Por isso `make deploy` sempre rebuilda antes.

`infra/stacks/settings.py` é o de `SENSORIANDO_API` portado: lê o `.env`, exige
`SENSORIANDO_ENVIRONMENT` e `AWS_REGION`, e monta o prefixo
`sensoriando-<ambiente>`.

### Build

`web/vite.config.ts` chama `scripts/resolve_api_url.py` e injeta o resultado em
`VITE_API_BASE_URL`. Falha na consulta produz string vazia, e `config.apiConfigured`
fica falso: o app mostra um aviso de configuração, nunca uma página em branco sem
explicação.

Em desenvolvimento (`npm run dev`), o Vite faz proxy de `/things`, `/sensors`,
`/accounts` e `/data` para a API, mantendo mesma origem localmente.

### Makefile

| Alvo | Faz |
|---|---|
| `make deploy` | `config-ensure`, build do `web/`, `cdk deploy --all --require-approval never` |
| `make destroy` | `cdk destroy --all --force` |
| `make ls` | lista as stacks do ambiente |
| `make config-check` | confere o Parameter Store contra o manifesto |
| `make config-ensure` | confere e pergunta as chaves ausentes |

---

## Tratamento de erros

Toda tela trata três estados: **carregando**, **erro** e **vazio**.

`api/client.ts` normaliza qualquer falha — HTTP, rede, JSON malformado — no tipo
`ApiError { status, message }`. `api/endpoints.ts` marca quais rotas ainda não
existem; um 404 vindo de uma delas produz a mensagem específica "recurso ainda
não disponível na API", distinta de um erro genérico. Isso importa: sem essa
distinção, uma pendência conhecida se confunde com um bug.

O estado vazio reaproveita o card existente ("Ops… Não há dispositivos para
exibir", com `nosensor.png`). Falha de rede vira faixa no topo da página, nunca
tela branca.

---

## Testes

**Vitest**, sobre funções puras, sem DOM:

- `lib/filters.ts` — query string ↔ objeto de filtros, ida e volta, incluindo
  valores ausentes e os casos especiais `"não registrado"` (cidade) e `"NR"`
  (país), que a API trata como "thing sem conta".
- `lib/prefs.ts` — `chartview` e `chart<id>` com e sem valor gravado, e os
  padrões (`second` e `line`).
- `lib/country.ts` — alpha-2 conhecido, desconhecido e `"NR"`.
- `lib/format.ts` — formatação de data e de última leitura, incluindo o `"---"`
  de quando não há leitura.
- `api/client.ts` — montagem de URL, serialização do corpo, e a normalização de
  erro para 404, 500 e falha de rede.

**pytest + `aws_cdk.assertions.Template`**, espelhando
`UDUU/infra/tests/unit/test_dashboard_stack.py`:

- o bucket bloqueia todo acesso público;
- os dois `error_responses` (403 e 404) apontam para `/index.html` com status 200;
- o output `SensoriandoWebUrl` existe;
- o synth não falha quando `web/dist` está ausente.

Sem testes end-to-end nesta fase.

---

## Ordem de execução

1. Tag `django-final` no commit atual de `develop`.
2. Branch de trabalho.
3. Scaffold de `web/` e `infra/`; portar `scripts/` e `Makefile`.
4. Portar as telas, do público para o privado: `PublicHome` → `ThingDetail` →
   `PrivateHome` → `LoginPage` → `Account` → `SignUp`.
5. Remover o Django (D7); atualizar `.gitignore` (`node_modules`, `dist`,
   `cdk.out`), `env.example` e `README.md`.
6. Atualizar `docs/guidelines/` — `stacks.md`, `architecture.md` e
   `coding-standards.md` descrevem a stack Django e ficam falsos após a migração.
   `database.md` deixa de se aplicar: este repositório não fala mais com o banco.
7. `make deploy` e validação na URL do CloudFront, com o site atual ainda no ar.

O corte de DNS não faz parte desta entrega.

---

## Riscos e pontos de atenção

**Chave de API do Google exposta.** `templates/map_world.js` contém uma chave
(`AIzaSyD-9tSr…`) commitada. Ela está no histórico do git: apagar o arquivo não a
remove. Deve ser revogada no console do Google, independentemente desta migração.

**Build acoplado à AWS.** Por D1, `npm run build` sem credencial válida produz um
bundle sem URL de API. O aviso de configuração na tela evita que isso passe
despercebido, mas quem builda precisa saber disso.

**Paridade visual.** O critério de aceitação é comparação lado a lado com
`web.sensoriando.com.br`. As diferenças conhecidas e aceitas são: ausência do
símbolo da unidade nos gráficos (D4), os dois itens removidos do menu, e a home
privada e o 404 migrados para o layout atual (D9).

**Sessão sem valor de segurança.** Por D2, o portão não protege dado nenhum. Se
alguém interpretar `/home/private` como conteúdo protegido, a leitura está
errada. Documentado no código e no README.
