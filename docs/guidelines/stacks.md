# Stack Tecnológica do Projeto

## Visão Geral

O Sensoriando Webservice é um SPA em React que apresenta os dados de sensores
servidos pela Sensoriando API. É publicado como site estático em S3 + CloudFront.

Não há servidor de aplicação e não há acesso ao banco de dados a partir deste
repositório.

---

## Linguagem e Runtime

- **TypeScript 5.5** sobre **React 18**, empacotado por **Vite 8**
- **Python 3.11+** apenas para a infraestrutura (AWS CDK) e os scripts de build

---

## Infraestrutura como Código

- **AWS CDK (Python)** — `infra/`
- Stack única: `sensoriando-<ambiente>-web`

---

## Serviços de Nuvem Utilizados

- **S3** — hospedagem do bundle
- **CloudFront** — distribuição
- **CloudFormation** — origem da URL da API, lida no build
- **SSM Parameter Store** — mecanismo de configuração (sem chaves declaradas hoje)

---

## Integrações Externas

- **Sensoriando API** — origem de todos os dados, por HTTP.

---

## Bibliotecas Permitidas

### SPA (`web/package.json`, versões fixadas)

- `react`, `react-dom` — 18.3
- `react-router-dom` — 7.1
- `chart.js` — 4.4

### Desenvolvimento

- `vite`, `@vitejs/plugin-react`, `typescript`, `vitest`, `@types/*`

### Infraestrutura (`infra/requirements.txt`, versões fixadas)

- `aws-cdk-lib`, `constructs`, `boto3`, `botocore`, `pytest`

---

## Bibliotecas Proibidas

- Nenhum gerenciador de estado global (Redux, Zustand, MobX). Cinco telas sem
  estado mutável compartilhado não justificam um.
- Nenhuma biblioteca de componentes ou framework de CSS. O estilo é o
  `style.css` portado.
- `eval()` e `new Function()` em qualquer lugar de `web/`.

---

## Estrutura de Módulos

```
web/src/api/         cliente HTTP, endpoints tipados e formas dos dados
web/src/auth/        portão de sessão
web/src/lib/         funções puras (filtros, preferências, formatação, país)
web/src/components/  apresentação, sem rede
web/src/views/       telas, que buscam dados e compõem componentes
infra/stacks/        stacks CDK
scripts/             resolução da URL da API e parâmetros no SSM
```

---

## Adicionando Novas Dependências

1. Verifique se o caso de uso não é coberto pelo que já existe.
2. Fixe a versão exata (`npm install --save-exact`).
3. Atualize este arquivo.
