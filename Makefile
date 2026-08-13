.PHONY: help test test-web test-infra ls deploy destroy config-check config-ensure

PROJECT_ENV = set -a; . ./.env; set +a;

help: ## Lista os alvos disponiveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

## Testes
test: test-web test-infra ## Roda toda a suite

test-web: ## Testes do SPA
	cd web && npm test

test-infra: ## Testes de sintese da stack CDK
	cd infra && ./.venv/bin/python -m pytest tests/unit -v

## Configuracao (SSM Parameter Store)
config-check: ## Confere o Parameter Store do ambiente (somente leitura)
	$(PROJECT_ENV) python3 scripts/config_parameters.py check

config-ensure: ## Publica as chaves ausentes, perguntando o valor quando preciso
	$(PROJECT_ENV) python3 scripts/config_parameters.py ensure

## Ambiente
ls: ## Lista as stacks que serao criadas no ambiente
	$(PROJECT_ENV) cd infra && cdk ls

deploy: config-ensure ## Builda o SPA e faz deploy da stack
	cd web && npm run build
	$(PROJECT_ENV) cd infra && cdk deploy --all --require-approval never

destroy: ## Destroi a stack na AWS
	$(PROJECT_ENV) cd infra && cdk destroy --all --force
