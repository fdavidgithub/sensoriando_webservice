# Spec: Things sem conta são públicos por padrão + nome do sensor por associação

- Data: 2026-07-06
- Branch: `feat/thing-visibility-fallback`
- Status: aprovado para plano de implementação

## Contexto

Hoje um `Thing` só aparece nas listagens (pública ou privada) se existir uma
linha correspondente em `accountsthings` (associação thing↔conta). A
visibilidade pública/privada é herdada do plano da conta associada
(`Plans.ispublic`). Um `Thing` cadastrado com seus sensores mas **sem**
conta associada:

- não aparece em nenhuma listagem (nem pública, nem privada);
- quebra com erro 500 se acessado diretamente pela página de detalhe
  (`sensors/views.py::ThingDetails`), pois o código busca a conta com
  `.get()` (que levanta exceção se não encontrar linha).

Além disso, o nome do sensor exibido em todas as telas vem sempre do
catálogo (`sensors.name`), ignorando qualquer nome específico da associação
thing↔sensor. O schema do banco (mantido pelo Sensoriando Core, fora deste
repositório) já foi atualizado com duas colunas novas em `thingssensors`:

- `name` (`varchar(30)`, nullable) — nome customizado da associação
  thing↔sensor.
- `channel` (`integer`, not null) — não utilizado nesta mudança, só precisa
  ser mapeado no ORM para refletir o schema real.

## Objetivo

1. Um `Thing` sem conta associada passa a ser **público por padrão** e
   aparece na listagem pública.
2. O nome do sensor exibido passa a ser `thingssensors.name` quando
   preenchido, com fallback para `sensors.name` quando estiver vazio/nulo.
3. Quando não há conta associada, cidade/estado/país são exibidos com
   fallback amigável em vez de branco ou erro.
4. Corrigir o bug pré-existente de erro 500 na página de detalhe de um
   `Thing` sem conta.

## Decisões de design

### 1. Schema (`base/legacy_tables.py`)

Atualizar o model `Thingssensors` para refletir as colunas já existentes no
banco (schema gerenciado pelo Sensoriando Core, `managed = False` — nenhuma
migration é criada por este repositório):

```python
class Thingssensors(models.Model):
    dt = models.DateTimeField()
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')
    id_sensor = models.ForeignKey(Sensors, models.DO_NOTHING, db_column='id_sensor')
    name = models.CharField(max_length=30, blank=True, null=True)
    channel = models.IntegerField()
```

`channel` é apenas mapeado; não há uso funcional nesta mudança.

### 2. Nome do sensor (fallback via `Coalesce`)

Decisão: a regra de fallback fica no webservice (não numa view do
Sensoriando Core), pois:

- é um cálculo trivial (`COALESCE` de duas colunas já unidas no mesmo
  join que o serializer já faz);
- hoje só o webservice lê o banco diretamente; a futura aplicação mobile
  vai consumir a API do webservice, não o banco — então o valor já resolvido
  chega pronto pra ela;
- é lógica de apresentação, mesma categoria do fallback de cidade/estado/país
  (item 4), que também fica no webservice.

Implementação: usar `django.db.models.functions.Coalesce` na query, em vez
de lógica condicional em Python:

```python
from django.db.models.functions import Coalesce
from django.db.models import F

ThingsSensorsModel.objects.filter(id_thing = obj.id_thing).annotate(
    display_name = Coalesce('name', 'id_sensor__name')
)
```

Pontos afetados:

- `api/serializers.py::DataThingsSerializer.get_sensors` — passa a iterar
  sobre `ThingsSensorsModel` anotado com `display_name`, em vez de re-buscar
  em `SensorsModel` pelos ids.
- `sensors/views.py::ThingDetails` (linha ~45) — troca
  `thingsensor.id_sensor.name` por `thingsensor.name or thingsensor.id_sensor.name`
  (ou usa o mesmo `annotate` com `Coalesce` na queryset de `thingssensors`
  daquela view).

### 3. Thing sem conta → público por padrão

`api/views.py::PublicThingsViewSets.get_queryset` deixa de originar em
`AccountsThingsModel` e passa a originar em `ThingsModel`, incluindo things
sem nenhuma linha em `accountsthings` OU com conta de plano público e status
ativo:

```python
from django.db.models import Q

ThingsModel.objects.filter(
    Q(accountsthings__isnull = True) |
    Q(accountsthings__id_account__status = True,
      accountsthings__id_account__id_plan__ispublic = True)
)
```

Consequência: o objeto entregue ao `DataThingsSerializer` passa a ser uma
instância de `ThingsModel` (não mais de `AccountsThingsModel`). O
serializer precisa ser ajustado:

- `get_thing`, `get_uuid` — passam a ler direto do próprio `obj` (era
  `obj.id_thing.name` / `obj.id_thing.uuid`).
- `get_account` — busca a conta via
  `AccountsModel.objects.filter(accountsthings__id_thing = obj).first()`
  (pode ser `None`).
- `get_sensors`, `get_thingtags`, `get_lastupdate` — passam a filtrar por
  `id_thing = obj` em vez de `id_thing = obj.id_thing`.

`PrivateThingsViewSets` **não muda** — já é escopado à conta do usuário
logado (`id_account = account_id`), então um thing sem conta nunca pode
aparecer ali por definição.

Os filtros de busca por `city`/`state`/`country` continuam usando
`id_account__...`; um thing sem conta simplesmente não casa com esses
filtros (não tem localização), o que é o comportamento esperado.

### 4. Fallback de cidade/estado/país sem conta

Em `DataThingsSerializer.get_account`, quando não há conta associada,
retornar:

```python
{
    "username": None,
    "city": "não registrado",
    "state": "",
    "country": "NR",
}
```

Em `overview/views.py::getCountry()`, pular a conversão via `pycountry`
quando `account["country"] == "NR"` (ou quando `account` for `None`),
evitando o `TypeError` atual de `"country" in None` e evitando chamar
`pycountry.countries.get(alpha_2= "NR")` (que retornaria `None` e quebraria
em `.name`).

### 5. Correção do bug pré-existente na página de detalhe

`sensors/views.py::ThingDetails` (linha ~36) troca:

```python
account = AccountsModel.objects.get(accountsthings__id_thing = thing.id)
```

por um lookup opcional:

```python
account = AccountsModel.objects.filter(accountsthings__id_thing = thing.id).first()
```

Com os mesmos fallbacks do item 4 aplicados ao contexto do template
(`city`, `state`, `country`), e `account.id_plan.ispublic` tratado como
`True` quando `account` é `None` (decide se a página busca dados via
`/data/detail/` público ou `/data/detail/private/`).

## Fora de escopo

- Uso funcional da coluna `channel` (só mapeamento no model).
- Qualquer mudança de schema no Sensoriando Core (já foi feita
  externamente).
- Alteração da listagem privada (`PrivateThingsViewSets`) — não afetada.
- Exibição/remoção do país da UI — decisão revertida: país continua sendo
  exibido normalmente, só com fallback `"NR"` quando não há conta.

## Testes

Não existe nenhuma suíte de testes real no projeto hoje (todos os
`tests.py` são o scaffold vazio do Django). Serão os primeiros testes
reais, cobrindo:

- Thing sem conta aparece na listagem pública (`PublicThingsViewSets`);
  thing com conta de plano privado não aparece.
- Nome do sensor: `thingssensors.name` presente prevalece; em branco cai
  para `sensors.name`.
- Fallback de cidade (`"não registrado"`), estado (`""`) e país (`"NR"`)
  quando não há conta associada.
- Página de detalhe (`ThingDetails`) não retorna 500 para um thing sem
  conta.

## Riscos / pontos de atenção

- Mudar a base do queryset de `AccountsThingsModel` para `ThingsModel` em
  `PublicThingsViewSets` altera o shape do objeto passado ao serializer —
  qualquer outro consumidor desse serializer (se houver) precisa ser
  revisado.
- `Coalesce` em campo `CharField(null=True, blank=True)`: strings vazias
  (`""`) não são `NULL`, então normalmente seria preciso validar a convenção
  de gravação. Confirmado com o time: o Sensoriando Core nunca grava `""` em
  `thingssensors.name`, sempre `NULL` quando não informado — `Coalesce` pode
  ser usado diretamente, sem tratamento extra para string vazia.
