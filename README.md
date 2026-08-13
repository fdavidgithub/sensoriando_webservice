# Sensoriando Webservice

Front-end da plataforma Sensoriando: um SPA em React que apresenta os dados de
sensores lidos da Sensoriando API.

Publicado como site estático em S3 + CloudFront.

## Arquitetura

```
Navegador → CloudFront → S3 (bundle estático)
    │
    └── HTTPS → API Gateway → Lambdas → PostgreSQL (Neon)
                (Sensoriando API, serviço externo)
```

Este repositório não tem servidor de aplicação nem fala com o banco: toda
leitura e escrita passa pela API.

## Estrutura

```
web/      SPA React + Vite + TypeScript
infra/    stack CDK do site estático
scripts/  resolução da URL da API e parâmetros no SSM
docs/     guidelines, specs e planos
```

## Desenvolvimento

```bash
cp env.example .env    # preencha ambiente, região e perfil AWS
cd web && npm install
npm run dev            # http://localhost:5173
```

A URL da API é descoberta no build a partir da conta AWS do ambiente. Sem
credencial válida, o app abre com um aviso de configuração em vez de dados.

## Testes

```bash
make test
```

## Deploy

```bash
make deploy
```

## Autenticação

Ainda não existe. A tela de login é um portão sem senha, que apenas libera as
telas privadas para inspeção — não protege dado nenhum, e os endpoints
`/private` da API servem sempre a mesma conta. Ver a decisão D2 em
`docs/superpowers/specs/2026-08-12-migracao-react-cdk-design.md`.
