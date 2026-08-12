# Handoff — Migração Django → React + AWS CDK

**Para:** o agente que vai implementar
**Data:** 2026-08-12
**Repositório:** `/mnt/storage/git/sensoriando_webservice`, branch `develop`

---

## 1. O que você vai fazer

Substituir a camada web Django deste repositório por um SPA em React, publicado
como site estático em S3 + CloudFront por uma stack AWS CDK escrita aqui mesmo.

O trabalho já está inteiramente especificado. Você **não** precisa desenhar nada,
tomar decisões de arquitetura, nem pesquisar como as coisas funcionam. Dois
documentos carregam tudo:

| Documento | Papel |
|---|---|
| `docs/superpowers/specs/2026-08-12-migracao-react-cdk-design.md` | As nove decisões, com a razão de cada uma e as alternativas descartadas |
| `docs/superpowers/plans/2026-08-12-migracao-react-cdk.md` | 20 tasks, 136 passos, com o código completo de cada arquivo |

Leia os dois antes de escrever a primeira linha. O plano contém o código real —
não esboços, não "adapte conforme necessário".

---

## 2. Como executar

**Use a skill `superpowers:subagent-driven-development.`** Invoque-a antes de
começar e siga o que ela mandar.

O regime é: um subagente novo por task, revisão em duas etapas entre uma task e a
seguinte. As tasks foram desenhadas exatamente para isso — cada uma termina num
entregável testável de forma independente, e cada uma declara, num bloco
`Interfaces`, o que consome das anteriores e o que produz para as seguintes. Um
subagente que só enxerga a própria task consegue trabalhar a partir desse bloco.

Execute as tasks **em ordem**. As dependências entre elas são reais.

---

## 3. Estado do repositório agora

Nada foi implementado ainda. O que existe é documentação:

```
docs/superpowers/specs/2026-08-12-migracao-react-cdk-design.md   ← o design
docs/superpowers/plans/2026-08-12-migracao-react-cdk.md          ← o plano
docs/superpowers/handoffs/2026-08-12-migracao-react-cdk.md       ← este arquivo
```

O resto do repositório é a aplicação Django que será substituída: `api/`,
`base/`, `core/`, `overview/`, `sensors/`, `users/`, `templates/`, `static/`.

O `.env` já está preenchido com `SENSORIANDO_ENVIRONMENT=development`,
`AWS_REGION=us-east-2` e `AWS_PROFILE=sensoriando`. Não há segredo nele e não
precisa haver.

---

## 4. O que a exploração já apurou

Esta seção existe para você não refazer o trabalho de descoberta. São fatos
verificados no código, não suposições.

### A API já não vive aqui

Os oito endpoints que o `api/` do Django serve foram migrados para um serviço
separado, em AWS Lambda atrás de API Gateway, lendo o mesmo PostgreSQL. O app
`api/` daqui virou duplicação. O SPA consome o serviço externo.

A URL dele não é previsível — a AWS atribui o id do API Gateway no deploy. Por
isso a stack `sensoriando-<ambiente>-api` publica um output `SensoriandoApiUrl` no
CloudFormation, e o build do SPA consulta esse output. O CORS da API já está em
`ALL_ORIGINS`, então a chamada cross-origin funciona.

**A API não tem autenticação.** Não existem `/token/`, `/token/refresh/` nem
`/token/verify/`. Os endpoints `/private` servem uma conta fixa, definida por
`PRIVATE_ACCOUNT_USERNAME` no Parameter Store, independentemente de quem estiver
usando o SPA. Isso é o que torna o login um portão decorativo (decisão D2).

### O que cada tela precisa e o que falta

Seis rotas de escrita e leitura **não existem** na API. As telas que dependem
delas são implementadas por completo e mostram uma mensagem de pendência até que
existam (decisão D6). O plano lista o contrato exato.

Consequência prática: ao rodar o SPA, ver `Recurso ainda não disponível na API`
no cadastro, no perfil e na coluna de unidades **é o comportamento correto**, não
um bug seu.

### Duas armadilhas no código Django que já foram investigadas

**As unidades.** `sensors/views.py` lê `sensorsunits.expression` — uma fórmula em
texto, tipo `"pv * 1.8 + 32"` — aplica com pandas e arredonda por
`sensorsunits.precision`. **Não replique isso.** A decisão D4 tirou toda lógica de
unidade do front-end: o SPA plota o valor cru que a API devolve. A conversão vai
para o banco depois. Se você se pegar escrevendo um avaliador de expressões,
parou de seguir o plano.

**Dois layouts.** `index.html`, `detail.html`, `signin.html`, `signup.html` e
`account.html` usam o design atual (`static/css/style.css`, cards, fundo em
grayscale). Mas `home.html` (a home privada) e `404.html` ficaram num layout
Bootstrap anterior, com `panel panel-primary` e grid `col-sm-*`. A decisão D9
unifica as duas no design atual — é a única diferença visual deliberada, além da
ausência do símbolo de unidade nos gráficos e da remoção de dois itens do menu.

**Preferências em cookie.** Tipo de gráfico, unidade e precisão moram em cookies
hoje, não no banco. Só as puramente visuais migram para `localStorage`
(`chartview`, `chart<id>`). `unit<id>` e `precision<id>` não migram — perderam a
função quando a conversão saiu do front-end.

### Um problema de segurança que não é seu para resolver

`templates/map_world.js` tem uma chave de API do Google commitada
(`AIzaSyD-9tSr…`). Ela está no histórico do git: apagar o arquivo não a remove.
**Não tente reescrever o histórico.** Apenas registre no relatório final que a
chave precisa ser revogada no console do Google. O plano já traz essa nota.

---

## 5. As nove decisões, em uma linha cada

Estão detalhadas no spec, com o porquê. Aqui só para você reconhecê-las quando
aparecerem:

| | Decisão |
|---|---|
| D1 | A URL da API é resolvida no build, consultando o CloudFormation |
| D2 | Login é um portão sem senha; não protege dado nenhum |
| D3 | Publicação só na URL do CloudFront; sem domínio próprio |
| D4 | Zero lógica de unidade no front-end |
| D5 | Filtros na query string; preferências visuais em `localStorage` |
| D6 | Escritas chamam o endpoint previsto e exibem o erro |
| D7 | Remoção completa do Django, com tag `django-final` no commit anterior |
| D8 | Mecanismo de SSM criado, manifesto vazio |
| D9 | Home privada e 404 migram para o layout atual |

Se durante a implementação alguma delas parecer errada, **pare e diga** em vez de
contorná-la em silêncio. Cada uma fechou alternativas que pareciam razoáveis; o
spec registra quais e por quê.

---

## 6. Ordem, e por que ela importa

```
Fase 1 (tasks 1-8)    fundação: cliente de API e funções puras, com testes
Fase 2 (tasks 9-11)   telas públicas
Fase 3 (tasks 12-15)  sessão e telas privadas
Fase 4 (tasks 16-18)  infraestrutura CDK
Fase 5 (tasks 19-20)  corte do Django e guidelines
```

Quatro dependências que não são óbvias e que quebram se você reordenar:

1. **A tag `django-final` nasce na Task 1, passo 1** — antes de qualquer coisa. A
   Task 19 verifica que ela existe e aborta se não existir. Ela é o ponto de
   restauração do site em produção.

2. **A Task 9 copia `static/css/style.css` e quatro imagens para `web/`.** A Task
   19 apaga `static/`. Inverter a ordem leva os assets junto.

3. **A Task 9 cria um `web/src/auth/session.ts` provisório** (três funções que
   não fazem nada) só para o `Header` compilar. A **Task 12 o substitui** pela
   versão real. Não pule esse passo achando que é redundante, e não pule a
   substituição achando que já está pronto.

4. **A Task 16 cria `infra/app.py`, que importa `stacks.web_stack`** — criado só
   na Task 17. Os testes da Task 16 passam mesmo assim; `cdk synth` só funciona
   depois da 17.

---

## 7. Checkpoints numéricos

Use como verificação objetiva ao fim de cada task. Se o número não bater, algo
saiu do plano:

| Depois da task | `cd web && npm test` | `cd infra && ./.venv/bin/python -m pytest tests/unit` |
|---|---|---|
| 4 | 7 | — |
| 5 | 11 | — |
| 6 | 20 | — |
| 7 | 26 | — |
| 8 | 33 | — |
| 12 | 38 | — |
| 16 | 38 | 5 |
| 17 | 38 | 12 |
| 20 | 38 | 12 |

As tasks 9-11 e 13-15 produzem componentes React e **não acrescentam testes** — o
spec não prevê testes de DOM nesta fase. A verificação delas é rodar
`npm run dev` e conferir a tela; cada uma traz a lista exata do que observar.

---

## 8. Quando considerar pronto

```
□ make test                       38 Vitest + 12 pytest
□ cd web && npm run build         conclui, e a URL da API aparece no bundle
□ make deploy                     a stack sobe e imprime SensoriandoWebUrl
□ abrir a URL do CloudFront e percorrer:
    home pública → filtro → detalhe → F5 no detalhe (não pode dar 403)
    → login → home privada → conta
□ comparar home pública e detalhe com web.sensoriando.com.br, lado a lado
□ git tag -l django-final          existe
```

O F5 no detalhe é o teste que pega o erro mais provável da infraestrutura: sem os
`error_responses` 403 e 404 apontando para `/index.html`, o S3 devolve 403 em
qualquer rota profunda.

---

## 9. O que não fazer

- **Não** altere nada fora de `/mnt/storage/git/sensoriando_webservice`. Tudo o
  que é preciso saber está nestes documentos; nenhuma task pede para ler outro
  repositório.
- **Não** aponte o DNS de `web.sensoriando.com.br`. O corte fica para depois, com
  o SPA já validado. O site atual precisa continuar no ar durante todo o trabalho.
- **Não** implemente as seis rotas que faltam na API. Elas são de outro serviço.
- **Não** trate o portão de sessão como controle de acesso, nem "melhore" a
  segurança dele. Ele é assumidamente decorativo (D2) e será substituído por
  Cognito.
- **Não** use `eval()` nem `new Function()` em lugar nenhum de `web/`.
- **Não** acrescente dependências além das fixadas no plano. Em especial: nenhum
  gerenciador de estado global, nenhuma biblioteca de componentes, nenhum
  framework de CSS.
- **Não** reescreva o histórico do git por causa da chave do Google.

---

## 10. Ao terminar

Relate:

1. O resultado dos checkpoints da seção 8, com a saída real dos comandos.
2. Qualquer desvio do plano, com a razão.
3. As pendências que ficaram para outros times — a última seção do plano já as
   lista: as seis rotas da API, o símbolo da unidade em `/data/detail`, e a
   revogação da chave do Google.

Se algo no plano estiver errado ou impossível, **diga em vez de improvisar**. Um
plano com defeito corrigido cedo custa menos que uma implementação que silenciou
o defeito.
