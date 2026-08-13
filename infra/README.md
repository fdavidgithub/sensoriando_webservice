# Infraestrutura (AWS CDK — Python)

Provisiona o site estático do Sensoriando Webservice: um bucket S3 privado
servido por CloudFront.

## Stack

`sensoriando-<ambiente>-web`

- Bucket S3 privado (`BLOCK_ALL`, criptografia gerenciada, Origin Access Control)
- Distribuição CloudFront, com 403 e 404 remapeados para `/index.html`
- `BucketDeployment` publica `web/dist` e invalida o cache
- Output `SensoriandoWebUrl`

## Pré-requisitos

- Python 3.11+
- AWS CDK CLI (`cdk --version`)
- Credenciais configuradas para o perfil do `.env`

## Preparação

```bash
cd infra
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

## Uso

```bash
make ls        # lista as stacks do ambiente
make deploy    # builda o SPA e faz o deploy
make destroy   # remove a stack
```

`make deploy` sempre rebuilda o `web/` antes. Rodar `cdk deploy` direto pula
esse passo: um `web/dist` desatualizado é publicado sem aviso.

## Configuração

Os nomes de recurso vêm do `.env` (`SENSORIANDO_ENVIRONMENT`, `AWS_REGION`,
`AWS_PROFILE`). O Parameter Store fica sob `/sensoriando/<ambiente>/web/` e hoje
não tem nenhuma chave declarada — ver a decisão D8 do documento de design.
