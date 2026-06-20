# Padrões de Código — Sensoriando Webservice

## Linguagem

Todo código-fonte deve ser escrito em **inglês**, incluindo nomes de variáveis, funções, classes, arquivos, campos de banco de dados, comentários, mensagens de log e mensagens de erro.

---

## Convenções de Nomenclatura

| Elemento                      | Padrão                              |
|-------------------------------|-------------------------------------|
| Classes                       | PascalCase                          |
| Funções / métodos             | snake_case                          |
| Variáveis                     | snake_case                          |
| Constantes                    | UPPER_CASE                          |
| Arquivos                      | snake_case                          |
| Tabelas (banco de dados)      | snake_case (plural)                 |
| Colunas (banco de dados)      | snake_case                          |
| Índices                       | snake_case com prefixo `idx_`       |
| Primary Keys                  | snake_case com prefixo `pk_`        |
| Foreign Keys                  | snake_case com prefixo `fk_`        |
| Constraints Unique            | snake_case com prefixo `uq_`        |
| Views                         | snake_case                          |
| Functions / Procedures (DB)   | snake_case                          |

---

## Estrutura do Handler / Ponto de Entrada

Os pontos de entrada da API são views do Django REST Framework, registradas em
`api/urls.py`. Endpoints de leitura usam `ModelViewSet`; endpoints com regra de
negócio usam `APIView`. Endpoints privados são protegidos por JWT.

```python
# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class PrivateStatisticsViewSets(APIView):
    def get(self, request, *args, **kwargs):
        data = self.build_data(request.user)
        serializer = serializers.DataStatsSerializer(data)
        return Response(serializer.data)
```

```python
# api/urls.py
path('data/stats/private/', views.PrivateStatisticsViewSets.as_view(), name='PrivateStatistics'),
```

A documentação OpenAPI/Swagger é gerada por `drf-yasg` (acessível na raiz de
`/api/`).

---

## Variáveis de Ambiente

- Todas as configurações de ambiente são lidas via variáveis de ambiente.
- Nunca hardcode URLs, credenciais ou configurações sensíveis no código.
- Variáveis obrigatórias para execução (lidas em `core/settings.py`; ver
  `env.example`):

| Variável | Descrição |
|----------|-----------|
| `DJANGO_PORT` | Porta do servidor Django |
| `DJANGO_PARAMS` | Parâmetros extras do `runserver` |
| `DJANGO_DEBUG` | Ativa o modo debug |
| `DJANGO_PREFIX_API` | URL base da API consumida pelas views web (`callAPI`) |
| `POSTGRES_HOST` | Host/container do banco |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do banco |
| `POSTGRES_DB` | Nome do banco |
| `POSTGRES_PORT` | Porta do banco |

> `SECRET_KEY` está atualmente fixada em `core/settings.py` (valor de
> desenvolvimento) e deveria, em produção, ser lida de variável de ambiente.

---

## Tratamento de Erros

- Erros operacionais (entrada inválida, campo ausente) retornam código `400`.
- Erros de infraestrutura retornam código `500`.
- Erros de contrato (payload fora do formato esperado) retornam `200` com `status: "error"` no body.
- Nunca deixe exceções não tratadas propagarem sem retornar uma resposta estruturada.

---

## Proibições

- Não modificar arquivos gerados (ex: `dist/`, artefatos de build).
- Não introduzir bibliotecas não listadas em `docs/guidelines/stacks.md`.
- Não bypassar as camadas de serviço ou repositório.
- Não usar `print` para logs; use um mecanismo de logging estruturado.

- Não criar nem alterar o schema do banco a partir deste serviço: as tabelas de
  domínio são `managed = False` (ver `docs/guidelines/database.md`).
- Não fixar `SECRET_KEY`, credenciais ou URLs no código — usar variáveis de
  ambiente.
- Não adicionar dependências fora de `requirements.txt` com versão fixada (ver
  `docs/guidelines/stacks.md`).
