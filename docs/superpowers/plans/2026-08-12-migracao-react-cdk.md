# Migração Django → React + AWS CDK — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Substituir a camada web Django deste repositório por um SPA React que consome o `SENSORIANDO_API`, publicado em S3 + CloudFront por uma stack AWS CDK.

**Architecture:** O SPA é estático e não tem servidor de aplicação. `web/vite.config.ts` descobre a URL da API no build consultando o output `SensoriandoApiUrl` da stack `sensoriando-<ambiente>-api` no CloudFormation, e injeta em `VITE_API_BASE_URL`. Uma stack CDK (`sensoriando-<ambiente>-web`) cria bucket privado + CloudFront com OAC e publica `web/dist`.

**Tech Stack:** React 18, TypeScript 5, Vite 8, Vitest 4, react-router-dom 7, chart.js 4, AWS CDK 2 (Python), pytest.

**Spec:** `docs/superpowers/specs/2026-08-12-migracao-react-cdk-design.md`

## Global Constraints

- Todo código-fonte em **inglês** (identificadores, comentários, mensagens de log). Texto de interface visível ao usuário permanece em **português**, como hoje. Ver `docs/guidelines/coding-standards.md`.
- **Não** alterar nenhum arquivo fora de `/mnt/storage/git/sensoriando_webservice`. `../UDUU` e `../SENSORIANDO_API` são referência de leitura apenas.
- Versões fixadas em `package.json` e `infra/requirements.txt`. Nenhuma dependência além das listadas neste plano.
- Nenhum segredo, URL ou credencial fixado em código.
- Nenhuma lógica de conversão ou arredondamento de unidade no front-end (D4 do spec).
- `eval()` e `new Function()` são proibidos em todo o `web/`.
- Nomes de arquivo em `web/src/`: `camelCase.ts` para módulos, `PascalCase.tsx` para componentes React.
- Mensagem de pendência de API, exata e única: `Recurso ainda não disponível na API`.
- Commits com prefixo convencional (`feat:`, `test:`, `chore:`, `docs:`, `refactor:`).

## Formas de dados da API (referência para todas as tasks)

Derivadas de `api/serializers.py` do Django, que o `SENSORIANDO_API` reproduz.

```
GET  /sensors            → [{ id: number, name: string }]
GET  /sensors/tags       → [{ name: string }]
GET  /accounts           → [{ username, city, state, country }]
POST /things             → Thing[]
POST /things/private     → Thing[]
POST /data/detail        → [{ dtread: string, value: number, message: string|null }]
GET  /data/stats/private → { user, plan, records, record_unit,
                             retation_current, retation_full, retation_unit }

Thing = {
  thing: string, uuid: string, lastupdate: string,   // "dd/mm/aaaa HH:MM:SS" ou "---"
  account: { username: string|null, city: string, state: string, country: string },
  sensors: [{ id: number, name: string }],
  thingtags: [{ id: number, name: string }]
}
```

Things sem conta chegam com `city: "não registrado"`, `state: ""`, `country: "NR"`, `username: null`.

---

## Fase 1 — Fundação

### Task 1: Marcar o Django e criar o esqueleto do SPA

**Files:**
- Create: `web/package.json`, `web/tsconfig.json`, `web/tsconfig.node.json`, `web/index.html`, `web/src/main.tsx`, `web/src/App.tsx`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: nada
- Produces: projeto Vite buildável em `web/`; `npm test` e `npm run build` funcionando

- [ ] **Step 1: Criar a tag do último commit Django**

A tag marca o último commit em que o site em produção pode ser reconstruído. Precisa existir antes de qualquer remoção.

```bash
git tag -a django-final -m "Último commit funcional da aplicação Django, antes da migração para React"
git tag -l django-final
```

Esperado: imprime `django-final`.

- [ ] **Step 2: Criar `web/package.json`**

```json
{
  "name": "sensoriando-web",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "chart.js": "4.4.7",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "react-router-dom": "7.1.1"
  },
  "devDependencies": {
    "@types/react": "18.3.3",
    "@types/react-dom": "18.3.0",
    "@vitejs/plugin-react": "4.3.1",
    "typescript": "5.5.4",
    "vite": "8.0.16",
    "vitest": "4.1.9"
  }
}
```

- [ ] **Step 3: Criar `web/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 4: Criar `web/tsconfig.node.json`**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "types": ["node"]
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 5: Criar `web/index.html`**

```html
<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta
      name="description"
      content="Sensoriando: Sensores públicos. Sensoriando é um hub MQTT de sensores."
    />
    <title>Sensoriando: Webservice</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Criar `web/src/App.tsx` provisório**

Substituído na Task 9 pelas rotas reais. Existe agora só para o build passar.

```tsx
export default function App() {
  return <h1>Sensoriando</h1>;
}
```

- [ ] **Step 7: Criar `web/src/main.tsx`**

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";

const container = document.getElementById("root");
if (!container) {
  throw new Error("root element is missing from index.html");
}

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

- [ ] **Step 8: Adicionar as exclusões ao `.gitignore`**

Acrescentar ao final do arquivo existente:

```gitignore

# Front-end
web/node_modules/
web/dist/
web/tsconfig.tsbuildinfo

# CDK
infra/cdk.out/
infra/.venv/
```

- [ ] **Step 9: Instalar e verificar que o build passa**

```bash
cd web && npm install && npm run build
```

Esperado: termina sem erro e cria `web/dist/index.html`. (O aviso de `vite.config.ts` ausente não ocorre: o Vite usa os padrões.)

- [ ] **Step 10: Commit**

```bash
git add .gitignore web/package.json web/package-lock.json web/tsconfig.json web/tsconfig.node.json web/index.html web/src/main.tsx web/src/App.tsx
git commit -m "chore: esqueleto do SPA React com Vite e TypeScript"
```

---

### Task 2: Resolver a URL da API a partir do CloudFormation

**Files:**
- Create: `scripts/_dotenv.py`, `scripts/resolve_api_url.py`

**Interfaces:**
- Consumes: nada
- Produces: `scripts/resolve_api_url.py` imprime a URL base da API em stdout e sai com 0; sai com 2 e mensagem em stderr quando não consegue resolver. Consumido pela Task 3.

- [ ] **Step 1: Criar `scripts/_dotenv.py`**

Leitor de `.env` sem dependências. Precisa ser stdlib pura porque roda dentro do `npm run build`, onde nenhuma dependência Python do projeto está garantida.

```python
"""Minimal .env reader shared by the build-time resolver scripts.

Deliberately not python-dotenv: these scripts run before the project's own
dependencies are guaranteed to be installed (e.g. from `npm run build`'s
subprocess call), so this stays stdlib-only.
"""

from pathlib import Path


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")

    return values
```

- [ ] **Step 2: Criar `scripts/resolve_api_url.py`**

Difere da versão do `SENSORIANDO_API` em dois pontos deliberados: lê o `.env` (porque `npm run build` não herda o `set -a` do `make`) e honra `AWS_PROFILE` (porque sem isso o boto3 cai no perfil default do shell, que pode ser outra conta).

```python
#!/usr/bin/env python3
"""Resolve the public URL of an environment's API Gateway.

The identifier AWS assigns to the API is not predictable, so the base URL
cannot be committed to source. It is discovered from the deployed stack's
CloudFormation output instead.

Usage:
    python scripts/resolve_api_url.py [--env development] [--region us-east-2]
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _dotenv import load_dotenv  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_KEY = "SensoriandoApiUrl"


def stack_name(environment_name: str) -> str:
    return f"sensoriando-{environment_name}-api"


def resolve(environment_name: str, region: str, profile: str | None) -> str:
    import boto3

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    client = session.client("cloudformation", region_name=region)
    description = client.describe_stacks(StackName=stack_name(environment_name))

    for output in description["Stacks"][0].get("Outputs", []):
        if output["OutputKey"].startswith(OUTPUT_KEY):
            return output["OutputValue"]

    raise LookupError(f"{OUTPUT_KEY} is absent from {stack_name(environment_name)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", dest="environment_name")
    parser.add_argument("--region")
    arguments = parser.parse_args()

    file_values = load_dotenv(REPOSITORY_ROOT / ".env")

    environment_name = (
        arguments.environment_name
        or os.environ.get("SENSORIANDO_ENVIRONMENT")
        or file_values.get("SENSORIANDO_ENVIRONMENT")
    )
    region = (
        arguments.region
        or os.environ.get("AWS_REGION")
        or file_values.get("AWS_REGION")
    )
    profile = os.environ.get("AWS_PROFILE") or file_values.get("AWS_PROFILE")

    if not environment_name or not region:
        sys.stderr.write("SENSORIANDO_ENVIRONMENT and AWS_REGION must be set\n")
        return 2

    try:
        print(resolve(environment_name, region, profile))
    except Exception as error:  # noqa: BLE001 - the caller only needs the failure
        sys.stderr.write(f"could not resolve the API URL: {error}\n")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Verificar que o script falha de forma limpa sem ambiente**

```bash
cd /mnt/storage/git/sensoriando_webservice
env -u SENSORIANDO_ENVIRONMENT -u AWS_REGION python3 -c "
import sys, pathlib
sys.argv = ['resolve_api_url.py']
sys.path.insert(0, 'scripts')
import runpy
try:
    runpy.run_path('scripts/resolve_api_url.py', run_name='__main__')
except SystemExit as e:
    print('exit code:', e.code)
"
```

Esperado: sai com código 0 ou 2. Com o `.env` do repositório presente (que define `SENSORIANDO_ENVIRONMENT` e `AWS_REGION`), o script tenta chamar a AWS; sem credencial válida imprime `could not resolve the API URL:` em stderr e sai com 2. Ambos os desfechos são corretos — o que não pode acontecer é traceback não tratado.

- [ ] **Step 4: Verificar o caminho de sucesso contra a AWS**

```bash
cd /mnt/storage/git/sensoriando_webservice
set -a; . ./.env; set +a
python3 scripts/resolve_api_url.py
```

Esperado, se a stack da API estiver implantada: uma URL `https://<id>.execute-api.us-east-2.amazonaws.com/<ambiente>/`. Se não estiver, mensagem de erro em stderr e código 2 — registre qual dos dois ocorreu e siga; a Task 3 trata o caso de falha.

- [ ] **Step 5: Commit**

```bash
git add scripts/_dotenv.py scripts/resolve_api_url.py
git commit -m "feat: resolver a URL da API pelo output do CloudFormation"
```

---

### Task 3: Configuração do build e do cliente

**Files:**
- Create: `web/vite.config.ts`, `web/src/config.ts`
- Modify: `web/package.json` (adicionar `@types/node`)

**Interfaces:**
- Consumes: `scripts/resolve_api_url.py` (Task 2)
- Produces: `config` de `web/src/config.ts` com `{ apiBaseUrl: string, apiConfigured: boolean, defaultPeriod: Period, defaultChartType: ChartType }`. Consumido pelas Tasks 4, 8, 9, 11.

- [ ] **Step 1: Adicionar `@types/node` às devDependencies**

Necessário porque `vite.config.ts` usa `node:child_process`.

```bash
cd web && npm install --save-dev --save-exact @types/node@22.20.1
```

- [ ] **Step 2: Criar `web/src/config.ts`**

```ts
// The build injects the API base URL discovered from the deployed account.
// An empty string means the lookup failed: the app then shows a configuration
// notice instead of firing requests at a relative path that cannot answer them.
const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL as string | undefined;

export const config = {
  // In dev, a relative base sends requests through the Vite proxy (see
  // vite.config.ts), keeping the browser on a single origin. Production builds
  // call the API directly; CORS is handled server-side.
  apiBaseUrl: import.meta.env.DEV ? "" : (rawApiBaseUrl ?? ""),
  apiConfigured: import.meta.env.DEV || Boolean(rawApiBaseUrl),
  defaultPeriod: "second",
  defaultChartType: "line",
} as const;
```

- [ ] **Step 3: Criar `web/vite.config.ts`**

```ts
/// <reference types="vitest/config" />
import { execFileSync } from "node:child_process";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The API Gateway id is assigned by AWS at deploy time, so the base URL is not
// committed. It is discovered from the deployed account at build time. A
// failure yields an empty string, which the app reports as "not configured"
// rather than silently producing a bundle that calls nothing.
function resolveApiBaseUrl(): string {
  try {
    const script = new URL("../scripts/resolve_api_url.py", import.meta.url).pathname;
    return execFileSync("python3", [script], { encoding: "utf8" }).trim();
  } catch {
    return "";
  }
}

// Every path prefix the API owns. Listed explicitly so that a future prefix is
// a deliberate addition here rather than a silent dev/prod difference.
const API_PREFIXES = ["/sensors", "/accounts", "/things", "/data"];

export default defineConfig(() => {
  const apiTarget = resolveApiBaseUrl();

  // Dev-only proxy: the browser talks to the Vite dev server (same origin) and
  // Vite forwards API calls, so CORS does not apply locally.
  const proxy = apiTarget
    ? Object.fromEntries(
        API_PREFIXES.map((prefix) => [
          prefix,
          { target: apiTarget, changeOrigin: true, secure: true },
        ]),
      )
    : undefined;

  return {
    plugins: [react()],
    define: {
      "import.meta.env.VITE_API_BASE_URL": JSON.stringify(apiTarget),
    },
    server: { proxy },
    test: {
      environment: "node",
      include: ["src/**/*.test.ts"],
    },
  };
});
```

- [ ] **Step 4: Verificar que o build ainda passa**

```bash
cd web && npm run build
```

Esperado: build conclui. Se a AWS não estiver acessível, conclui igualmente — `resolveApiBaseUrl` devolve string vazia por desenho.

- [ ] **Step 5: Confirmar que a URL foi de fato embutida**

```bash
cd web && grep -ro "execute-api" dist/assets/ | head -1
```

Esperado: uma linha com `execute-api` se a stack da API estiver implantada. Nenhuma saída significa que a resolução falhou — aceitável neste momento, e a tela de aviso da Task 9 cobre o caso.

- [ ] **Step 6: Commit**

```bash
git add web/vite.config.ts web/src/config.ts web/package.json web/package-lock.json
git commit -m "feat: injetar a URL da API no build e configurar o proxy de desenvolvimento"
```

---

### Task 4: Cliente HTTP

**Files:**
- Create: `web/src/api/types.ts`, `web/src/api/client.ts`, `web/src/api/client.test.ts`

**Interfaces:**
- Consumes: `config` (Task 3)
- Produces:
  - `class ApiError extends Error { readonly status: number }` — `status` 0 significa falha de rede
  - `apiGet<T>(path: string): Promise<T>`
  - `apiPost<T>(path: string, body?: unknown): Promise<T>`
  - `apiPut<T>(path: string, body?: unknown): Promise<T>`
  - tipos `Sensor`, `SensorTag`, `Account`, `Thing`, `ThingSensor`, `ThingTag`, `Reading`, `Stats`, `SensorUnit`
  - Consumido pela Task 5.

- [ ] **Step 1: Criar `web/src/api/types.ts`**

```ts
export interface Sensor {
  id: number;
  name: string;
}

export interface SensorTag {
  name: string;
}

export interface Account {
  username: string | null;
  city: string;
  state: string;
  country: string;
}

export interface ThingSensor {
  id: number;
  name: string;
}

// The API serializes thing tags with the sensor serializer, so they carry an
// `id` alongside the name.
export interface ThingTag {
  id: number;
  name: string;
}

export interface Thing {
  thing: string;
  uuid: string;
  /** Already formatted by the API as "dd/mm/aaaa HH:MM:SS", or "---". */
  lastupdate: string;
  account: Account;
  sensors: ThingSensor[];
  thingtags: ThingTag[];
}

export interface Reading {
  dtread: string;
  value: number;
  message: string | null;
}

export interface Stats {
  user: string;
  plan: string;
  records: number;
  record_unit: string;
  retation_current: number;
  retation_full: number;
  retation_unit: string;
}

/** Served by GET /sensors/units, which does not exist yet. */
export interface SensorUnit {
  id: number;
  id_sensor: number;
  name: string;
  initial: string | null;
  precision: number | null;
  isdefault: boolean;
}
```

- [ ] **Step 2: Escrever os testes que falham**

Criar `web/src/api/client.test.ts`:

```ts
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiGet, apiPost } from "./client";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("apiGet", () => {
  it("returns the parsed body on success", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([{ id: 1, name: "temp" }]));
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiGet("/sensors")).resolves.toEqual([{ id: 1, name: "temp" }]);
    expect(fetchMock).toHaveBeenCalledWith(
      "/sensors",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("joins the base URL without doubling the slash", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    await apiGet("/sensors", "https://api.example.com/development/");

    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.example.com/development/sensors",
      expect.anything(),
    );
  });

  it("raises ApiError carrying the HTTP status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({}, 404)));

    await expect(apiGet("/missing")).rejects.toMatchObject({
      name: "ApiError",
      status: 404,
    });
  });

  it("reports a network failure as status 0", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("failed to fetch")));

    await expect(apiGet("/sensors")).rejects.toMatchObject({
      name: "ApiError",
      status: 0,
    });
  });

  it("reports a malformed body as status 0 rather than crashing", async () => {
    const broken = new Response("not json", {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(broken));

    await expect(apiGet("/sensors")).rejects.toBeInstanceOf(ApiError);
  });
});

describe("apiPost", () => {
  it("sends the body as JSON", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    await apiPost("/things", { sensor: "temperatura" });

    expect(fetchMock).toHaveBeenCalledWith(
      "/things",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ sensor: "temperatura" }),
        headers: { "Content-Type": "application/json" },
      }),
    );
  });

  it("omits the body when there is none", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    await apiPost("/things");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.body).toBeUndefined();
  });
});
```

- [ ] **Step 3: Rodar os testes e confirmar que falham**

```bash
cd web && npm test
```

Esperado: FAIL — `Failed to resolve import "./client"`.

- [ ] **Step 4: Implementar `web/src/api/client.ts`**

```ts
import { config } from "../config";

/**
 * Every failure the API layer can produce, in one shape.
 *
 * `status` is the HTTP status, or 0 when the request never got an answer —
 * network down, CORS refusal, malformed body. Callers that need to tell
 * "the server said no" from "there was no server" check for 0.
 */
export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function buildUrl(path: string, baseUrl: string): string {
  if (!baseUrl) return path;
  return `${baseUrl.replace(/\/$/, "")}${path}`;
}

async function request<T>(
  method: "GET" | "POST" | "PUT",
  path: string,
  body: unknown,
  baseUrl: string,
): Promise<T> {
  const init: RequestInit = { method };

  if (body !== undefined) {
    init.body = JSON.stringify(body);
    init.headers = { "Content-Type": "application/json" };
  }

  let response: Response;
  try {
    response = await fetch(buildUrl(path, baseUrl), init);
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new ApiError(0, `Falha de conexão com a API: ${detail}`);
  }

  if (!response.ok) {
    throw new ApiError(response.status, `A API respondeu ${response.status}`);
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError(0, "A API respondeu num formato inesperado");
  }
}

export function apiGet<T>(path: string, baseUrl: string = config.apiBaseUrl): Promise<T> {
  return request<T>("GET", path, undefined, baseUrl);
}

export function apiPost<T>(
  path: string,
  body?: unknown,
  baseUrl: string = config.apiBaseUrl,
): Promise<T> {
  return request<T>("POST", path, body, baseUrl);
}

export function apiPut<T>(
  path: string,
  body?: unknown,
  baseUrl: string = config.apiBaseUrl,
): Promise<T> {
  return request<T>("PUT", path, body, baseUrl);
}
```

- [ ] **Step 5: Rodar os testes e confirmar que passam**

```bash
cd web && npm test
```

Esperado: PASS, 7 testes.

- [ ] **Step 6: Commit**

```bash
git add web/src/api/types.ts web/src/api/client.ts web/src/api/client.test.ts
git commit -m "feat: cliente HTTP com erro normalizado em ApiError"
```

---

### Task 5: Endpoints tipados

**Files:**
- Create: `web/src/api/endpoints.ts`, `web/src/api/endpoints.test.ts`

**Interfaces:**
- Consumes: `apiGet`, `apiPost`, `apiPut`, `ApiError`, tipos (Task 4)
- Produces:
  - `PENDING_MESSAGE = "Recurso ainda não disponível na API"`
  - `listSensors()`, `listSensorTags()`, `listPublicThings(filters)`, `listPrivateThings(filters)`, `readPublicDetail(args)`, `readPrivateDetail(args)`, `readPrivateStats()`
  - pendentes: `listSensorUnits()`, `savePreferredUnit(input)`, `readPrivateAccount()`, `savePrivateAccount(input)`, `createAccount(input)`, `linkThing(input)`
  - Consumido pelas Tasks 10, 11, 13, 14, 15.

- [ ] **Step 1: Escrever os testes que falham**

Criar `web/src/api/endpoints.test.ts`:

```ts
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "./client";
import { PENDING_MESSAGE, listSensors, listSensorUnits, readPrivateAccount } from "./endpoints";

afterEach(() => {
  vi.unstubAllGlobals();
});

function respond(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("existing endpoints", () => {
  it("listSensors calls GET /sensors", async () => {
    const fetchMock = vi.fn().mockResolvedValue(respond([{ id: 1, name: "temp" }]));
    vi.stubGlobal("fetch", fetchMock);

    await expect(listSensors()).resolves.toEqual([{ id: 1, name: "temp" }]);
    expect(fetchMock.mock.calls[0][0]).toBe("/sensors");
  });
});

describe("pending endpoints", () => {
  it("turns a 404 into the pending message", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respond({}, 404)));

    await expect(listSensorUnits()).rejects.toMatchObject({
      status: 404,
      message: PENDING_MESSAGE,
    });
  });

  it("leaves other failures untouched", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(respond({}, 500)));

    const error = await readPrivateAccount().catch((caught: unknown) => caught);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(500);
    expect((error as ApiError).message).not.toBe(PENDING_MESSAGE);
  });

  it("passes a successful response straight through once the route exists", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(respond([{ id: 1, id_sensor: 1, name: "Celsius", initial: "C", precision: 2, isdefault: true }])),
    );

    await expect(listSensorUnits()).resolves.toHaveLength(1);
  });
});
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

```bash
cd web && npm test
```

Esperado: FAIL — `Failed to resolve import "./endpoints"`.

- [ ] **Step 3: Implementar `web/src/api/endpoints.ts`**

```ts
import { ApiError, apiGet, apiPost, apiPut } from "./client";
import type { Reading, Sensor, SensorTag, SensorUnit, Stats, Thing } from "./types";

/**
 * Shown when a route this app already calls does not exist in the API yet.
 * Distinct from a generic failure on purpose: a known gap must not read as a
 * bug. See the "Endpoints previstos" table in the design document.
 */
export const PENDING_MESSAGE = "Recurso ainda não disponível na API";

/**
 * Marks a call whose route is not deployed yet. A 404 from such a route is the
 * expected state, not an error worth a stack trace; anything else passes
 * through untouched so real failures stay visible.
 */
async function pending<T>(call: () => Promise<T>): Promise<T> {
  try {
    return await call();
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      throw new ApiError(404, PENDING_MESSAGE);
    }
    throw error;
  }
}

export type ThingFilters = Record<string, string>;

export type Period = "second" | "minute" | "hour" | "day" | "month" | "year";

export interface DetailQuery {
  thing: string;
  sensor: string;
  period: Period;
}

export interface AccountInput {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  city: string;
  state: string;
  country: string;
}

export interface ProfileInput {
  first_name: string;
  last_name: string;
  email: string;
  city: string;
  state: string;
  country: string;
}

export interface PreferredUnitInput {
  id_sensor: number;
  id_unit: number;
  precision: number;
}

export interface PrivateAccount {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  city: string;
  state: string;
  country: string;
}

// --- Routes that exist ------------------------------------------------------

export function listSensors(): Promise<Sensor[]> {
  return apiGet<Sensor[]>("/sensors");
}

export function listSensorTags(): Promise<SensorTag[]> {
  return apiGet<SensorTag[]>("/sensors/tags");
}

export function listPublicThings(filters: ThingFilters = {}): Promise<Thing[]> {
  return apiPost<Thing[]>("/things", filters);
}

export function listPrivateThings(filters: ThingFilters = {}): Promise<Thing[]> {
  return apiPost<Thing[]>("/things/private", filters);
}

export function readPublicDetail(query: DetailQuery): Promise<Reading[]> {
  return apiPost<Reading[]>("/data/detail", query);
}

export function readPrivateDetail(query: DetailQuery): Promise<Reading[]> {
  return apiPost<Reading[]>("/data/detail/private", query);
}

export function readPrivateStats(): Promise<Stats> {
  return apiGet<Stats>("/data/stats/private");
}

// --- Routes the API still has to expose -------------------------------------

export function listSensorUnits(): Promise<SensorUnit[]> {
  return pending(() => apiGet<SensorUnit[]>("/sensors/units"));
}

export function savePreferredUnit(input: PreferredUnitInput): Promise<void> {
  return pending(() => apiPut<void>("/accounts/private/sensors/units", input));
}

export function readPrivateAccount(): Promise<PrivateAccount> {
  return pending(() => apiGet<PrivateAccount>("/accounts/private"));
}

export function savePrivateAccount(input: ProfileInput): Promise<void> {
  return pending(() => apiPut<void>("/accounts/private", input));
}

export function createAccount(input: AccountInput): Promise<void> {
  return pending(() => apiPost<void>("/accounts", input));
}

export function linkThing(input: { uuid: string }): Promise<void> {
  return pending(() => apiPost<void>("/accounts/private/things", input));
}
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

```bash
cd web && npm test
```

Esperado: PASS, 11 testes no total.

- [ ] **Step 5: Commit**

```bash
git add web/src/api/endpoints.ts web/src/api/endpoints.test.ts
git commit -m "feat: endpoints tipados, com as rotas pendentes marcadas"
```

---

### Task 6: Filtros na query string

**Files:**
- Create: `web/src/lib/filters.ts`, `web/src/lib/filters.test.ts`

**Interfaces:**
- Consumes: nada
- Produces:
  - `FILTER_KEYS: readonly FilterKey[]`
  - `type Filters = Partial<Record<FilterKey, string>>`
  - `filtersFromSearch(search: string): Filters`
  - `searchFromFilters(filters: Filters): string`
  - Consumido pelas Tasks 10, 13.

- [ ] **Step 1: Escrever os testes que falham**

Criar `web/src/lib/filters.test.ts`:

```ts
import { describe, expect, it } from "vitest";

import { filtersFromSearch, searchFromFilters } from "./filters";

describe("filtersFromSearch", () => {
  it("reads the keys the API accepts", () => {
    expect(filtersFromSearch("?sensor=temperatura&sensor_tag=externo")).toEqual({
      sensor: "temperatura",
      sensor_tag: "externo",
    });
  });

  it("ignores keys the API does not accept", () => {
    expect(filtersFromSearch("?sensor=temperatura&utm_source=x")).toEqual({
      sensor: "temperatura",
    });
  });

  it("drops empty values so they are never sent as filters", () => {
    expect(filtersFromSearch("?sensor=&city=Lavras")).toEqual({ city: "Lavras" });
  });

  it("returns nothing for an empty search", () => {
    expect(filtersFromSearch("")).toEqual({});
    expect(filtersFromSearch("?")).toEqual({});
  });

  it("keeps the sentinels the API uses for things without an account", () => {
    expect(filtersFromSearch("?city=n%C3%A3o%20registrado&country=NR")).toEqual({
      city: "não registrado",
      country: "NR",
    });
  });
});

describe("searchFromFilters", () => {
  it("builds a query string", () => {
    expect(searchFromFilters({ sensor: "temperatura" })).toBe("?sensor=temperatura");
  });

  it("returns an empty string when there is no filter", () => {
    expect(searchFromFilters({})).toBe("");
  });

  it("omits empty values", () => {
    expect(searchFromFilters({ sensor: "", city: "Lavras" })).toBe("?city=Lavras");
  });

  it("round-trips through filtersFromSearch", () => {
    const filters = { city: "não registrado", country: "NR", sensor: "temperatura" };
    expect(filtersFromSearch(searchFromFilters(filters))).toEqual(filters);
  });
});
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

```bash
cd web && npm test
```

Esperado: FAIL — `Failed to resolve import "./filters"`.

- [ ] **Step 3: Implementar `web/src/lib/filters.ts`**

```ts
/**
 * The filter keys POST /things and POST /things/private accept. Anything else
 * in the query string is not a filter and is dropped, so that an unrelated
 * parameter (an analytics tag, say) never reaches the API as one.
 */
export const FILTER_KEYS = [
  "thing",
  "city",
  "state",
  "country",
  "sensor",
  "thing_tag",
  "sensor_tag",
] as const;

export type FilterKey = (typeof FILTER_KEYS)[number];

export type Filters = Partial<Record<FilterKey, string>>;

function isFilterKey(key: string): key is FilterKey {
  return (FILTER_KEYS as readonly string[]).includes(key);
}

export function filtersFromSearch(search: string): Filters {
  const parameters = new URLSearchParams(search);
  const filters: Filters = {};

  for (const key of FILTER_KEYS) {
    const value = parameters.get(key);
    if (value) {
      filters[key] = value;
    }
  }

  return filters;
}

export function searchFromFilters(filters: Filters): string {
  const parameters = new URLSearchParams();

  for (const [key, value] of Object.entries(filters)) {
    if (value && isFilterKey(key)) {
      parameters.set(key, value);
    }
  }

  const search = parameters.toString();
  return search ? `?${search}` : "";
}
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

```bash
cd web && npm test
```

Esperado: PASS, 20 testes no total.

- [ ] **Step 5: Commit**

```bash
git add web/src/lib/filters.ts web/src/lib/filters.test.ts
git commit -m "feat: filtros da home lidos e escritos na query string"
```

---

### Task 7: Nome de país e rótulos de gráfico

**Files:**
- Create: `web/src/lib/country.ts`, `web/src/lib/country.test.ts`, `web/src/lib/format.ts`, `web/src/lib/format.test.ts`

**Interfaces:**
- Consumes: `Period` (Task 5)
- Produces:
  - `countryName(code: string | null | undefined): string`
  - `chartLabel(period: Period, date: Date): string` — o título do eixo X
  - `chartLegend(period: Period, date: Date): string` — o rótulo de cada ponto
  - Consumido pelas Tasks 10, 11, 13.

- [ ] **Step 1: Escrever os testes de país que falham**

Criar `web/src/lib/country.test.ts`:

```ts
import { describe, expect, it } from "vitest";

import { countryName } from "./country";

describe("countryName", () => {
  it("translates a known alpha-2 code", () => {
    expect(countryName("BR")).toBe("Brasil");
  });

  // The API sends "NR" for a thing with no account. Django left it untranslated,
  // and so do we — it is a sentinel, not a country.
  it("leaves the no-account sentinel alone", () => {
    expect(countryName("NR")).toBe("NR");
  });

  it("returns the code itself when it is not a country", () => {
    expect(countryName("ZZ")).toBe("ZZ");
  });

  it("returns an empty string for a missing value", () => {
    expect(countryName(null)).toBe("");
    expect(countryName(undefined)).toBe("");
    expect(countryName("")).toBe("");
  });
});
```

- [ ] **Step 2: Escrever os testes de formatação que falham**

Criar `web/src/lib/format.test.ts`:

```ts
import { describe, expect, it } from "vitest";

import { chartLabel, chartLegend } from "./format";

// 2026-03-09 14:07:42 local time.
const moment = new Date(2026, 2, 9, 14, 7, 42);

describe("chartLabel", () => {
  it("matches the Django format for each period", () => {
    expect(chartLabel("second", moment)).toBe("09/03/2026 14:07");
    expect(chartLabel("minute", moment)).toBe("09/03/2026 14h");
    expect(chartLabel("hour", moment)).toBe("09/03/2026");
    expect(chartLabel("day", moment)).toBe("03/2026");
    expect(chartLabel("month", moment)).toBe("2026");
    expect(chartLabel("year", moment)).toBe("");
  });
});

describe("chartLegend", () => {
  it("matches the Django format for each period", () => {
    expect(chartLegend("second", moment)).toBe("42");
    expect(chartLegend("minute", moment)).toBe("07");
    expect(chartLegend("hour", moment)).toBe("14");
    expect(chartLegend("day", moment)).toBe("09");
    expect(chartLegend("month", moment)).toBe("03");
    expect(chartLegend("year", moment)).toBe("2026");
  });
});
```

- [ ] **Step 3: Rodar os testes e confirmar que falham**

```bash
cd web && npm test
```

Esperado: FAIL — imports de `./country` e `./format` não resolvem.

- [ ] **Step 4: Implementar `web/src/lib/country.ts`**

```ts
/** The API's sentinel for a thing that belongs to no account. */
const NO_ACCOUNT = "NR";

// Intl.DisplayNames is built into the browser, which is why no country table
// and no dependency is needed here to replace Django's pycountry.
const displayNames = new Intl.DisplayNames(["pt-BR"], {
  type: "region",
  fallback: "none",
});

export function countryName(code: string | null | undefined): string {
  if (!code) return "";
  if (code === NO_ACCOUNT) return code;

  try {
    return displayNames.of(code) ?? code;
  } catch {
    // Intl throws on a structurally invalid code (not two letters).
    return code;
  }
}
```

- [ ] **Step 5: Implementar `web/src/lib/format.ts`**

```ts
import type { Period } from "../api/endpoints";

function pad(value: number): string {
  return String(value).padStart(2, "0");
}

/**
 * The X axis title: what the whole series has in common. Mirrors the `label`
 * entries of `dateFormats` in the Django view it replaces.
 */
export function chartLabel(period: Period, date: Date): string {
  const day = pad(date.getDate());
  const month = pad(date.getMonth() + 1);
  const year = date.getFullYear();
  const hour = pad(date.getHours());
  const minute = pad(date.getMinutes());

  switch (period) {
    case "second":
      return `${day}/${month}/${year} ${hour}:${minute}`;
    case "minute":
      return `${day}/${month}/${year} ${hour}h`;
    case "hour":
      return `${day}/${month}/${year}`;
    case "day":
      return `${month}/${year}`;
    case "month":
      return `${year}`;
    case "year":
      return "";
  }
}

/**
 * The per-point label: the one unit that varies inside the period. Mirrors the
 * `legend` entries of the same Django table.
 */
export function chartLegend(period: Period, date: Date): string {
  switch (period) {
    case "second":
      return pad(date.getSeconds());
    case "minute":
      return pad(date.getMinutes());
    case "hour":
      return pad(date.getHours());
    case "day":
      return pad(date.getDate());
    case "month":
      return pad(date.getMonth() + 1);
    case "year":
      return String(date.getFullYear());
  }
}
```

- [ ] **Step 6: Rodar os testes e confirmar que passam**

```bash
cd web && npm test
```

Esperado: PASS, 26 testes no total.

- [ ] **Step 7: Commit**

```bash
git add web/src/lib/country.ts web/src/lib/country.test.ts web/src/lib/format.ts web/src/lib/format.test.ts
git commit -m "feat: nome de pais via Intl e rotulos de grafico por periodo"
```

---

### Task 8: Preferências de exibição

**Files:**
- Create: `web/src/lib/prefs.ts`, `web/src/lib/prefs.test.ts`

**Interfaces:**
- Consumes: `Period` (Task 5), `config` (Task 3)
- Produces:
  - `type ChartType = "line" | "bar" | "table" | "display"`
  - `readPeriod(): Period` / `writePeriod(period: Period): void`
  - `readChartType(sensorId: number): ChartType` / `writeChartType(sensorId: number, type: ChartType): void`
  - Consumido pelas Tasks 11, 15.

Só as preferências puramente visuais migram. `unit<id>` e `precision<id>` ficam de fora por D4 do spec: existiam para alimentar a conversão que o front-end não faz mais.

- [ ] **Step 1: Escrever os testes que falham**

Criar `web/src/lib/prefs.test.ts`:

```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

import { readChartType, readPeriod, writeChartType, writePeriod } from "./prefs";

function memoryStorage(): Storage {
  const entries = new Map<string, string>();
  return {
    get length() {
      return entries.size;
    },
    clear: () => entries.clear(),
    getItem: (key: string) => entries.get(key) ?? null,
    key: (index: number) => Array.from(entries.keys())[index] ?? null,
    removeItem: (key: string) => void entries.delete(key),
    setItem: (key: string, value: string) => void entries.set(key, value),
  } as Storage;
}

beforeEach(() => {
  vi.stubGlobal("localStorage", memoryStorage());
});

describe("readPeriod", () => {
  it("defaults to second when nothing is stored", () => {
    expect(readPeriod()).toBe("second");
  });

  it("returns what was written", () => {
    writePeriod("month");
    expect(readPeriod()).toBe("month");
  });

  it("falls back to the default when the stored value is not a period", () => {
    localStorage.setItem("chartview", "fortnight");
    expect(readPeriod()).toBe("second");
  });
});

describe("readChartType", () => {
  it("defaults to line when nothing is stored", () => {
    expect(readChartType(7)).toBe("line");
  });

  it("keeps one value per sensor", () => {
    writeChartType(7, "bar");
    writeChartType(9, "table");

    expect(readChartType(7)).toBe("bar");
    expect(readChartType(9)).toBe("table");
    expect(readChartType(11)).toBe("line");
  });

  it("uses the same key Django used, so a returning user keeps the setting", () => {
    writeChartType(7, "bar");
    expect(localStorage.getItem("chart7")).toBe("bar");
  });

  it("falls back to the default when the stored value is not a chart type", () => {
    localStorage.setItem("chart7", "pie");
    expect(readChartType(7)).toBe("line");
  });
});
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

```bash
cd web && npm test
```

Esperado: FAIL — `Failed to resolve import "./prefs"`.

- [ ] **Step 3: Implementar `web/src/lib/prefs.ts`**

```ts
import type { Period } from "../api/endpoints";
import { config } from "../config";

export type ChartType = "line" | "bar" | "table" | "display";

const PERIODS: readonly Period[] = ["second", "minute", "hour", "day", "month", "year"];
const CHART_TYPES: readonly ChartType[] = ["line", "bar", "table", "display"];

// The keys Django wrote as cookies. Kept identical so a returning visitor does
// not silently lose the setting they picked.
const PERIOD_KEY = "chartview";
const chartTypeKey = (sensorId: number) => `chart${sensorId}`;

function read<T extends string>(key: string, allowed: readonly T[], fallback: T): T {
  const stored = localStorage.getItem(key);
  return stored !== null && (allowed as readonly string[]).includes(stored)
    ? (stored as T)
    : fallback;
}

export function readPeriod(): Period {
  return read(PERIOD_KEY, PERIODS, config.defaultPeriod);
}

export function writePeriod(period: Period): void {
  localStorage.setItem(PERIOD_KEY, period);
}

export function readChartType(sensorId: number): ChartType {
  return read(chartTypeKey(sensorId), CHART_TYPES, config.defaultChartType);
}

export function writeChartType(sensorId: number, type: ChartType): void {
  localStorage.setItem(chartTypeKey(sensorId), type);
}
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

```bash
cd web && npm test
```

Esperado: PASS, 33 testes no total.

- [ ] **Step 5: Commit**

```bash
git add web/src/lib/prefs.ts web/src/lib/prefs.test.ts
git commit -m "feat: preferencias de periodo e tipo de grafico em localStorage"
```

---

## Fase 2 — Telas públicas

> As tasks desta fase produzem componentes React. O spec não prevê testes de DOM (`Testes`, `sem testes end-to-end nesta fase`), então a verificação é executar o app e comparar com a produção — o critério de aceitação que o próprio spec define. Cada task traz os passos exatos dessa verificação.

### Task 9: Estilos, layout base e rotas

**Files:**
- Create: `web/src/styles/style.css`, `web/src/components/Header.tsx`, `web/src/components/Footer.tsx`, `web/src/components/Background.tsx`, `web/src/components/EmptyState.tsx`, `web/src/components/ErrorBanner.tsx`, `web/src/components/Loading.tsx`, `web/src/views/NotFound.tsx`, `web/public/img/` (4 imagens)
- Modify: `web/src/App.tsx`, `web/src/main.tsx`

**Interfaces:**
- Consumes: `config` (Task 3)
- Produces:
  - `<Header />`, `<Footer />`, `<Background />`
  - `<Loading />`, `<EmptyState message?: string />`, `<ErrorBanner message: string />`
  - `<App />` com as rotas do spec
  - Consumido por todas as tasks de tela seguintes.

- [ ] **Step 1: Copiar os estilos e as imagens**

O CSS é portado como está: a fidelidade visual é o critério de aceitação, e reescrevê-lo introduziria diferenças sem pedido.

```bash
cd /mnt/storage/git/sensoriando_webservice
mkdir -p web/src/styles web/public/img
cp static/css/style.css web/src/styles/style.css
cp static/img/background.jpeg static/img/bars.svg static/img/service-1.png static/img/nosensor.png web/public/img/
ls -la web/public/img/
```

Esperado: as quatro imagens presentes.

- [ ] **Step 2: Criar `web/src/components/Background.tsx`**

```tsx
export default function Background() {
  return (
    <section className="background">
      <img className="grayscale" src="/img/background.jpeg" alt="technology components" />
    </section>
  );
}
```

- [ ] **Step 3: Criar `web/src/components/Header.tsx`**

O menu perde "Mapa" (rota morta desde que foi comentada no Django) e "API" (o Swagger sumiu com o Django). Ver a seção "Rotas do SPA" do spec.

```tsx
import { Link, useNavigate } from "react-router-dom";

import { readSession, clearSession } from "../auth/session";

export default function Header() {
  const session = readSession();
  const navigate = useNavigate();

  // clearSession only touches localStorage, which React does not observe. The
  // navigation is what re-renders this component so the menu flips back to
  // "Cadastrar / Entrar" instead of still showing the username.
  function signOut() {
    clearSession();
    navigate("/", { replace: true });
  }

  return (
    <nav>
      <Link to="/" className="font-27px">
        Sensoriando
      </Link>

      <div className="dropdown">
        <img src="/img/bars.svg" alt="menu icon" />

        <div className="dropdown-content">
          {session ? (
            <>
              <Link to="/home/private" className="font-16px">
                Meus dispositivos
              </Link>
              <Link to={`/users/account/${session.username}/profile`} className="font-16px">
                {session.username}
              </Link>
              <button className="font-16px" onClick={signOut} type="button">
                Sair
              </button>
            </>
          ) : (
            <>
              <Link to="/users/signup" className="font-16px">
                Cadastrar
              </Link>
              <Link to="/users/login" className="font-16px">
                Entrar
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
```

> Este componente importa `../auth/session`, criado na Task 12. Para manter a Task 9 verificável isoladamente, crie agora o arquivo mínimo abaixo; a Task 12 o substitui pela versão completa.

Criar `web/src/auth/session.ts` provisório:

```ts
export interface Session {
  username: string;
}

export function readSession(): Session | null {
  return null;
}

export function clearSession(): void {}
```

- [ ] **Step 4: Criar `web/src/components/Footer.tsx`**

Reproduz `templates/footer.html`, que hoje é uma casca com um título e dois blocos vazios.

```tsx
export default function Footer() {
  return (
    <div>
      <div className="stats">
        <h3 className="font-22px">Estatisticas</h3>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Criar os três componentes de estado**

`web/src/components/Loading.tsx`:

```tsx
export default function Loading() {
  return <p className="font-17px">Carregando…</p>;
}
```

`web/src/components/EmptyState.tsx` — reaproveita o card "Ops…" que já existe em `templates/things.html`:

```tsx
interface Props {
  message?: string;
}

export default function EmptyState({ message = "Não há dispositivos para exibir." }: Props) {
  return (
    <ul>
      <li>
        <div>
          <img src="/img/nosensor.png" alt="Icon" />
        </div>
        <h3 className="font-22px">Ops...</h3>
        <p className="font-17px">{message}</p>
      </li>
    </ul>
  );
}
```

`web/src/components/ErrorBanner.tsx`:

```tsx
interface Props {
  message: string;
}

export default function ErrorBanner({ message }: Props) {
  return (
    <p className="font-17px" role="alert">
      {message}
    </p>
  );
}
```

- [ ] **Step 6: Criar `web/src/views/NotFound.tsx`**

Por D9 do spec, o 404 passa a usar o layout atual em vez do Bootstrap legado.

```tsx
export default function NotFound() {
  return (
    <section className="home">
      <div>
        <h1 className="font-36px">Página não encontrada</h1>
      </div>
    </section>
  );
}
```

- [ ] **Step 7: Reescrever `web/src/App.tsx` com as rotas**

As rotas privadas ganham o `AuthGate` na Task 12; até lá apontam direto para as views.

```tsx
import { BrowserRouter, Route, Routes } from "react-router-dom";

import Background from "./components/Background";
import Footer from "./components/Footer";
import Header from "./components/Header";
import NotFound from "./views/NotFound";
import { config } from "./config";

function ConfigurationNotice() {
  return (
    <section className="home">
      <div>
        <h1 className="font-36px">Aplicação sem configuração</h1>
        <p className="font-17px">
          A URL da API não foi resolvida durante o build. Refaça o build com acesso à
          conta AWS do ambiente.
        </p>
      </div>
    </section>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Background />
      <header>
        <Header />
      </header>

      <main>
        {config.apiConfigured ? (
          <Routes>
            <Route path="/" element={<NotFound />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        ) : (
          <ConfigurationNotice />
        )}
      </main>

      <footer>
        <Footer />
      </footer>
    </BrowserRouter>
  );
}
```

- [ ] **Step 8: Importar o CSS em `web/src/main.tsx`**

Acrescentar a linha de import abaixo dos imports existentes:

```tsx
import "./styles/style.css";
```

- [ ] **Step 9: Verificar build e testes**

```bash
cd web && npm run build && npm test
```

Esperado: build conclui; 33 testes passam (nenhum teste novo nesta task).

- [ ] **Step 10: Verificar visualmente**

```bash
cd web && npm run dev
```

Abrir `http://localhost:5173`. Esperado: o background em grayscale, a barra "Sensoriando" com o ícone de menu, o menu abrindo com "Cadastrar" e "Entrar", e o rodapé com "Estatisticas". Comparar com `web.sensoriando.com.br`: cabeçalho, rodapé e fundo devem estar iguais.

- [ ] **Step 11: Commit**

```bash
git add web/src/styles web/public/img web/src/components web/src/views/NotFound.tsx web/src/auth/session.ts web/src/App.tsx web/src/main.tsx
git commit -m "feat: layout base, estilos portados e roteamento do SPA"
```

---

### Task 10: Home pública

**Files:**
- Create: `web/src/components/ThingCard.tsx`, `web/src/components/FilterDialog.tsx`, `web/src/lib/useApi.ts`, `web/src/views/PublicHome.tsx`
- Modify: `web/src/App.tsx`

**Interfaces:**
- Consumes: `listSensors`, `listSensorTags`, `listPublicThings` (Task 5); `filtersFromSearch`, `searchFromFilters` (Task 6); `countryName` (Task 7)
- Produces:
  - `useApi<T>(call: () => Promise<T>, deps: unknown[]): { data: T | null; loading: boolean; error: string | null }`
  - `<ThingCard thing={thing} onFilter={(key, value) => void} />`
  - `<FilterDialog sensors tags filters onApply onClear />`
  - Consumido pelas Tasks 11, 13, 15.

- [ ] **Step 1: Criar `web/src/lib/useApi.ts`**

Um hook por view, sem store global: cinco telas e nenhum estado mutável compartilhado não justificam um gerenciador de estado.

```ts
import { useEffect, useState } from "react";

import { ApiError } from "../api/client";

interface State<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(call: () => Promise<T>, deps: unknown[]): State<T> {
  const [state, setState] = useState<State<T>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let active = true;
    setState({ data: null, loading: true, error: null });

    call()
      .then((data) => {
        if (active) setState({ data, loading: false, error: null });
      })
      .catch((error: unknown) => {
        if (!active) return;
        const message =
          error instanceof ApiError ? error.message : "Falha inesperada ao ler a API";
        setState({ data: null, loading: false, error: message });
      });

    return () => {
      // The view may unmount (or the filters may change) before the request
      // settles; without this the late answer would overwrite fresher state.
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}
```

- [ ] **Step 2: Criar `web/src/components/ThingCard.tsx`**

Reproduz `templates/things.html`, com as mesmas classes CSS.

```tsx
import { Link } from "react-router-dom";

import type { Thing } from "../api/types";
import type { FilterKey } from "../lib/filters";
import { countryName } from "../lib/country";

interface Props {
  thing: Thing;
  onFilter: (key: FilterKey, value: string) => void;
}

export default function ThingCard({ thing, onFilter }: Props) {
  return (
    <li>
      <div className="card-icon">
        <img src="/img/service-1.png" alt="Icon" />
      </div>

      <h3 className="font-22px">
        <Link to={`/thing/detail/${thing.uuid}`} className="underline-black__half">
          {thing.thing}
        </Link>
      </h3>

      <div className="font-13px card-body">
        <div className="column">
          <div>
            <b>Cidade</b>
          </div>
          <div>
            <b>Pais</b>
          </div>
          <div>
            <b>Sensores</b>
          </div>
          <div>
            <b>Tags</b>
          </div>
        </div>

        <div className="column">
          <div>
            <button
              type="button"
              className="underline-black"
              onClick={() => onFilter("city", thing.account.city)}
            >
              {thing.account.city}
            </button>
            {" / "}
            <button
              type="button"
              className="underline-black"
              onClick={() => onFilter("state", thing.account.state)}
            >
              {thing.account.state}
            </button>
          </div>

          <div>
            <button
              type="button"
              className="underline-black"
              onClick={() => onFilter("country", thing.account.country)}
            >
              {countryName(thing.account.country)}
            </button>
          </div>

          <div>
            {thing.sensors.map((sensor) => (
              <button
                key={sensor.id}
                type="button"
                className="underline-black"
                onClick={() => onFilter("sensor", sensor.name)}
              >
                {sensor.name}
              </button>
            ))}
          </div>

          <div>
            {thing.thingtags.map((tag) => (
              <button
                key={tag.id}
                type="button"
                className="underline-black"
                onClick={() => onFilter("thing_tag", tag.name)}
              >
                {tag.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="card-body">
        <div className="column">
          <div>
            <b className="font-13px">Última leitura</b>
          </div>
        </div>
        <div className="column">
          <div className="font-13px">{thing.lastupdate}</div>
        </div>
      </div>
    </li>
  );
}
```

- [ ] **Step 3: Criar `web/src/components/FilterDialog.tsx`**

```tsx
import { useState } from "react";

import type { Sensor, SensorTag } from "../api/types";
import type { Filters } from "../lib/filters";

interface Props {
  open: boolean;
  sensors: Sensor[];
  tags: SensorTag[];
  filters: Filters;
  onApply: (filters: Filters) => void;
  onClear: () => void;
  onClose: () => void;
}

export default function FilterDialog({
  open,
  sensors,
  tags,
  filters,
  onApply,
  onClear,
  onClose,
}: Props) {
  const [sensor, setSensor] = useState(filters.sensor ?? "");
  const [sensorTag, setSensorTag] = useState(filters.sensor_tag ?? "");

  if (!open) return null;

  function apply() {
    onApply({ sensor, sensor_tag: sensorTag });
  }

  function clear() {
    setSensor("");
    setSensorTag("");
    onClear();
  }

  return (
    <dialog id="filter" open>
      <div className="dialog-container">
        <div className="modal-header">
          <h5 className="modal-title font-22px">Filtros</h5>
          <button type="button" onClick={onClose}>
            X
          </button>
        </div>

        <div>
          <select
            className="font-13px"
            value={sensor}
            onChange={(event) => setSensor(event.target.value)}
          >
            <option value="">Todos sensores</option>
            {sensors.map((item) => (
              <option key={item.id} value={item.name}>
                {item.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <select
            className="font-13px"
            value={sensorTag}
            onChange={(event) => setSensorTag(event.target.value)}
          >
            <option value="">Todas tags</option>
            {tags.map((item) => (
              <option key={item.name} value={item.name}>
                {item.name}
              </option>
            ))}
          </select>
        </div>

        <div className="modal-button-div">
          <button type="button" className="btn btn-primary btn-sm font-13px" onClick={apply}>
            Aplicar
          </button>
          <button type="button" className="btn btn-primary btn-sm font-13px" onClick={clear}>
            Limpar
          </button>
        </div>
      </div>
    </dialog>
  );
}
```

- [ ] **Step 4: Criar `web/src/views/PublicHome.tsx`**

```tsx
import { useCallback, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { listPublicThings, listSensorTags, listSensors } from "../api/endpoints";
import EmptyState from "../components/EmptyState";
import ErrorBanner from "../components/ErrorBanner";
import FilterDialog from "../components/FilterDialog";
import Loading from "../components/Loading";
import ThingCard from "../components/ThingCard";
import { useApi } from "../lib/useApi";
import {
  type FilterKey,
  type Filters,
  filtersFromSearch,
  searchFromFilters,
} from "../lib/filters";

export default function PublicHome() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [dialogOpen, setDialogOpen] = useState(false);

  const search = searchParams.toString();
  const filters = useMemo(() => filtersFromSearch(search), [search]);

  const things = useApi(() => listPublicThings(filters), [search]);
  const sensors = useApi(() => listSensors(), []);
  const tags = useApi(() => listSensorTags(), []);

  const applyFilters = useCallback(
    (next: Filters) => {
      setSearchParams(new URLSearchParams(searchFromFilters(next)));
      setDialogOpen(false);
    },
    [setSearchParams],
  );

  const addFilter = useCallback(
    (key: FilterKey, value: string) => applyFilters({ ...filters, [key]: value }),
    [applyFilters, filters],
  );

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">Dispositivos</h1>
          <button className="font-16px" type="button" onClick={() => setDialogOpen(true)}>
            Filtros
          </button>
        </div>
      </section>

      <section className="cards">
        {things.loading && <Loading />}
        {things.error && <ErrorBanner message={things.error} />}
        {things.data?.length === 0 && <EmptyState />}
        {things.data && things.data.length > 0 && (
          <ul>
            {things.data.map((thing) => (
              <ThingCard key={thing.uuid} thing={thing} onFilter={addFilter} />
            ))}
          </ul>
        )}
      </section>

      <FilterDialog
        open={dialogOpen}
        sensors={sensors.data ?? []}
        tags={tags.data ?? []}
        filters={filters}
        onApply={applyFilters}
        onClear={() => applyFilters({})}
        onClose={() => setDialogOpen(false)}
      />
    </>
  );
}
```

- [ ] **Step 5: Ligar a rota em `web/src/App.tsx`**

Substituir o bloco `<Routes>` por:

```tsx
          <Routes>
            <Route path="/" element={<PublicHome />} />
            <Route path="/home" element={<PublicHome />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
```

E acrescentar o import:

```tsx
import PublicHome from "./views/PublicHome";
```

- [ ] **Step 6: Verificar build e testes**

```bash
cd web && npm run build && npm test
```

Esperado: build conclui; 33 testes passam.

- [ ] **Step 7: Verificar visualmente contra a produção**

```bash
cd web && npm run dev
```

Abrir `http://localhost:5173` e comparar com `http://web.sensoriando.com.br`:

1. Os cards listam os mesmos dispositivos, com cidade, país, sensores, tags e última leitura.
2. Clicar em "Filtros" abre o modal com os selects de sensores e tags preenchidos.
3. Aplicar um filtro muda a URL para `?sensor=...` e reduz a lista.
4. Clicar num sensor dentro de um card aplica aquele filtro.
5. "Limpar" volta a URL para `/` e restaura a lista completa.
6. O botão voltar do navegador desfaz o último filtro.

- [ ] **Step 8: Commit**

```bash
git add web/src/lib/useApi.ts web/src/components/ThingCard.tsx web/src/components/FilterDialog.tsx web/src/views/PublicHome.tsx web/src/App.tsx
git commit -m "feat: home publica com cards e filtros na query string"
```

---

### Task 11: Detalhe do dispositivo

**Files:**
- Create: `web/src/components/SensorChart.tsx`, `web/src/views/ThingDetail.tsx`
- Modify: `web/src/App.tsx`

**Interfaces:**
- Consumes: `readPublicDetail`, `readPrivateDetail`, `listPublicThings`, `listPrivateThings` (Task 5); `chartLabel`, `chartLegend` (Task 7); `readPeriod`, `writePeriod`, `readChartType` (Task 8); `readSession` (Task 9 provisório / Task 12 definitivo)
- Produces: `<SensorChart points label type />`

O valor plotado é exatamente o que a API devolve. Nenhuma conversão, nenhum arredondamento — D4 do spec. Enquanto `/data/detail` não devolver o símbolo da unidade, o rótulo não o traz.

**Escolha entre endpoint público e privado.** O Django decidia lendo `id_plan.ispublic` direto do banco. O SPA não tem esse campo: nenhum serializer o expõe. A decisão passa a ser por presença — se o uuid aparece em `/things`, é público; se não aparece e há sessão, procura em `/things/private` e usa o endpoint privado. É a única informação disponível pelo contrato atual, e produz o mesmo resultado.

- [ ] **Step 1: Criar `web/src/components/SensorChart.tsx`**

Usa `chart.js` direto, sem wrapper React, para não acrescentar dependência a um único ponto de uso.

```tsx
import { useEffect, useRef } from "react";
import {
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  Legend,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from "chart.js";

import type { ChartType } from "../lib/prefs";

Chart.register(
  BarController,
  BarElement,
  CategoryScale,
  Legend,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
);

interface Point {
  legend: string;
  value: number;
}

interface Props {
  points: Point[];
  label: string;
  type: Exclude<ChartType, "table" | "display">;
}

export default function SensorChart({ points, label, type }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const chart = new Chart(canvas, {
      type,
      data: {
        labels: points.map((point) => point.legend),
        datasets: [
          {
            label,
            pointStyle: "circle",
            pointRadius: 5,
            backgroundColor: "white",
            borderColor: "red",
            data: points.map((point) => point.value),
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          x: { display: true, title: { display: true, text: label } },
          y: { display: true, title: { display: false, text: "Value" } },
        },
      },
    });

    // Chart.js keeps a canvas registry; without this a re-render throws
    // "Canvas is already in use".
    return () => chart.destroy();
  }, [points, label, type]);

  return <canvas ref={canvasRef} />;
}
```

- [ ] **Step 2: Criar `web/src/views/ThingDetail.tsx`**

```tsx
import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import type { Period } from "../api/endpoints";
import {
  listPrivateThings,
  listPublicThings,
  readPrivateDetail,
  readPublicDetail,
} from "../api/endpoints";
import { readSession } from "../auth/session";
import EmptyState from "../components/EmptyState";
import ErrorBanner from "../components/ErrorBanner";
import Loading from "../components/Loading";
import SensorChart from "../components/SensorChart";
import { chartLabel, chartLegend } from "../lib/format";
import { readChartType, readPeriod, writePeriod } from "../lib/prefs";
import { useApi } from "../lib/useApi";

const PERIOD_LABELS: Array<{ value: Period; text: string }> = [
  { value: "second", text: "Segundos" },
  { value: "minute", text: "Minutos" },
  { value: "hour", text: "Horas" },
  { value: "day", text: "Dias" },
  { value: "month", text: "Meses" },
  { value: "year", text: "Anos" },
];

function SensorPanel({
  uuid,
  sensorId,
  sensorName,
  period,
  isPublic,
}: {
  uuid: string;
  sensorId: number;
  sensorName: string;
  period: Period;
  isPublic: boolean;
}) {
  const readings = useApi(
    () =>
      (isPublic ? readPublicDetail : readPrivateDetail)({
        thing: uuid,
        sensor: sensorName,
        period,
      }),
    [uuid, sensorName, period, isPublic],
  );

  const type = readChartType(sensorId);

  const points = useMemo(
    () =>
      (readings.data ?? []).map((reading) => ({
        legend: chartLegend(period, new Date(reading.dtread)),
        value: reading.value,
      })),
    [readings.data, period],
  );

  const label = useMemo(() => {
    const last = readings.data?.at(-1);
    return last ? chartLabel(period, new Date(last.dtread)) : "";
  }, [readings.data, period]);

  return (
    <li>
      <div>
        <b>{sensorName}</b>
      </div>

      <div>
        {readings.loading && <Loading />}
        {readings.error && <ErrorBanner message={readings.error} />}
        {readings.data?.length === 0 && <EmptyState message="Não há leituras para exibir." />}

        {points.length > 0 && type === "table" && (
          <table className="table table-striped" width="100%">
            <thead>
              <tr>
                <th>Data</th>
                <th>Mensagem</th>
              </tr>
            </thead>
            <tbody>
              {readings.data?.map((reading, index) => (
                <tr key={`${reading.dtread}-${index}`}>
                  <th>{reading.dtread}</th>
                  <th>{reading.message}</th>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {points.length > 0 && type === "display" && (
          <table className="table table-striped" width="100%">
            <tbody>
              <tr>
                <th>
                  <font size="20">{points.at(-1)?.value}</font>
                </th>
              </tr>
            </tbody>
          </table>
        )}

        {points.length > 0 && type !== "table" && type !== "display" && (
          <SensorChart points={points} label={label} type={type} />
        )}
      </div>
    </li>
  );
}

export default function ThingDetail() {
  const { uuid = "" } = useParams();
  const [period, setPeriod] = useState<Period>(readPeriod());

  // The route carries only the uuid, so the sensor names come from the thing
  // listings. Which listing the uuid turns up in is also what says whether the
  // readings come from the public or the private endpoint.
  const hasSession = Boolean(readSession());
  const publicThings = useApi(() => listPublicThings(), []);
  const privateThings = useApi(
    () => (hasSession ? listPrivateThings() : Promise.resolve([])),
    [hasSession],
  );

  const publicThing = publicThings.data?.find((candidate) => candidate.uuid === uuid);
  const privateThing = privateThings.data?.find((candidate) => candidate.uuid === uuid);
  const thing = publicThing ?? privateThing;
  const isPublic = Boolean(publicThing);

  const loading = publicThings.loading || privateThings.loading;
  const error = publicThings.error ?? privateThings.error;
  const settled = Boolean(publicThings.data) && Boolean(privateThings.data);

  function choosePeriod(next: Period) {
    writePeriod(next);
    setPeriod(next);
  }

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">{thing?.thing ?? "Dispositivo"}</h1>

          <div className="home-button-list">
            <div className="home-dropdown">
              <button className="font-16px" type="button">
                Visualizar dados
              </button>
              <div className="home-dropdown-content">
                {PERIOD_LABELS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    className="font-13px underline-white"
                    onClick={() => choosePeriod(option.value)}
                  >
                    {option.text}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="charts">
        {loading && <Loading />}
        {error && <ErrorBanner message={error} />}
        {settled && !thing && <EmptyState message="Dispositivo não encontrado." />}

        {thing && (
          <ul>
            {thing.sensors.map((sensor) => (
              <SensorPanel
                key={sensor.id}
                uuid={uuid}
                sensorId={sensor.id}
                sensorName={sensor.name}
                period={period}
                isPublic={isPublic}
              />
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
```

- [ ] **Step 3: Ligar a rota em `web/src/App.tsx`**

Acrescentar dentro de `<Routes>`, antes da rota `*`:

```tsx
            <Route path="/thing/detail/:uuid" element={<ThingDetail />} />
```

E o import:

```tsx
import ThingDetail from "./views/ThingDetail";
```

- [ ] **Step 4: Verificar build e testes**

```bash
cd web && npm run build && npm test
```

Esperado: build conclui; 33 testes passam.

- [ ] **Step 5: Verificar visualmente**

```bash
cd web && npm run dev
```

Na home, clicar no nome de um dispositivo. Esperado:

1. A URL vira `/thing/detail/<uuid>` e o título mostra o nome do dispositivo.
2. Um gráfico de linha por sensor, com os pontos rotulados pelos segundos.
3. "Visualizar dados" → "Horas" muda os rótulos e recarrega as séries.
4. Recarregar a página (F5) mantém o período escolhido.
5. Comparar com a produção: os valores plotados podem diferir se o sensor tiver unidade com conversão — é a diferença esperada de D4. A forma da curva e os rótulos do eixo devem coincidir.

- [ ] **Step 6: Commit**

```bash
git add web/src/components/SensorChart.tsx web/src/views/ThingDetail.tsx web/src/App.tsx
git commit -m "feat: tela de detalhe com graficos por sensor e escolha de periodo"
```

---

## Fase 3 — Sessão e telas privadas

### Task 12: Portão de sessão

**Files:**
- Modify: `web/src/auth/session.ts` (substitui o provisório da Task 9), `web/src/App.tsx`
- Create: `web/src/auth/session.test.ts`, `web/src/auth/AuthGate.tsx`, `web/src/views/LoginPage.tsx`

**Interfaces:**
- Consumes: nada
- Produces:
  - `interface Session { username: string }`
  - `readSession(): Session | null`, `writeSession(username: string): void`, `clearSession(): void`
  - `<AuthGate>{children}</AuthGate>`
  - Consumido pelas Tasks 13, 15.

Por D2 do spec: não há senha. Isso é uma barreira de conveniência, não de segurança — qualquer pessoa altera o `localStorage` pelo DevTools, e os endpoints `/private` servem a conta fixa do `PRIVATE_ACCOUNT_USERNAME` independentemente de quem entrou.

- [ ] **Step 1: Escrever os testes que falham**

Criar `web/src/auth/session.test.ts`:

```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

import { clearSession, readSession, writeSession } from "./session";

function memoryStorage(): Storage {
  const entries = new Map<string, string>();
  return {
    get length() {
      return entries.size;
    },
    clear: () => entries.clear(),
    getItem: (key: string) => entries.get(key) ?? null,
    key: (index: number) => Array.from(entries.keys())[index] ?? null,
    removeItem: (key: string) => void entries.delete(key),
    setItem: (key: string, value: string) => void entries.set(key, value),
  } as Storage;
}

beforeEach(() => {
  vi.stubGlobal("localStorage", memoryStorage());
});

describe("session", () => {
  it("starts with no session", () => {
    expect(readSession()).toBeNull();
  });

  it("returns the session that was written", () => {
    writeSession("visitante");
    expect(readSession()).toEqual({ username: "visitante" });
  });

  it("clears the session", () => {
    writeSession("visitante");
    clearSession();
    expect(readSession()).toBeNull();
  });

  it("treats a corrupted entry as no session instead of crashing", () => {
    localStorage.setItem("sensoriando.session", "{not json");
    expect(readSession()).toBeNull();
  });

  it("treats an entry without a username as no session", () => {
    localStorage.setItem("sensoriando.session", JSON.stringify({ other: 1 }));
    expect(readSession()).toBeNull();
  });
});
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

```bash
cd web && npm test
```

Esperado: FAIL — `readSession()` do arquivo provisório devolve `null` sempre, então "returns the session that was written" falha.

- [ ] **Step 3: Substituir `web/src/auth/session.ts`**

```ts
/**
 * A convenience gate, not a security boundary.
 *
 * The app is a static bundle: there is no server here to verify anything, and
 * any password shipped in it would be readable by anyone with the URL. So there
 * is no password at all — the gate only keeps the private screens out of the
 * way until real authentication (Cognito) lands.
 *
 * It also grants no access to data: the API's /private endpoints serve the one
 * account named by PRIVATE_ACCOUNT_USERNAME regardless of who signed in here.
 */

const SESSION_KEY = "sensoriando.session";

export interface Session {
  username: string;
}

export function readSession(): Session | null {
  const stored = localStorage.getItem(SESSION_KEY);
  if (!stored) return null;

  try {
    const parsed = JSON.parse(stored) as Partial<Session>;
    return typeof parsed.username === "string" ? { username: parsed.username } : null;
  } catch {
    return null;
  }
}

export function writeSession(username: string): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify({ username }));
}

export function clearSession(): void {
  localStorage.removeItem(SESSION_KEY);
}
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

```bash
cd web && npm test
```

Esperado: PASS, 38 testes no total.

- [ ] **Step 5: Criar `web/src/auth/AuthGate.tsx`**

```tsx
import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { readSession } from "./session";

interface Props {
  children: ReactNode;
}

export default function AuthGate({ children }: Props) {
  return readSession() ? <>{children}</> : <Navigate to="/users/login" replace />;
}
```

- [ ] **Step 6: Criar `web/src/views/LoginPage.tsx`**

```tsx
import { useNavigate } from "react-router-dom";

import { writeSession } from "../auth/session";

const GUEST_USERNAME = "visitante";

export default function LoginPage() {
  const navigate = useNavigate();

  function enter() {
    writeSession(GUEST_USERNAME);
    navigate("/home/private");
  }

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">Autenticar usuário</h1>
        </div>
      </section>

      <section className="signUp">
        <p className="font-17px">
          A autenticação ainda não foi implementada. Este acesso é temporário e serve
          apenas para visualizar as telas privadas.
        </p>
        <button type="button" className="font-16px" onClick={enter}>
          <span>Entrar</span>
        </button>
      </section>
    </>
  );
}
```

- [ ] **Step 7: Ligar a rota em `web/src/App.tsx`**

Acrescentar dentro de `<Routes>`, antes da rota `*`:

```tsx
            <Route path="/users/login" element={<LoginPage />} />
```

E o import:

```tsx
import LoginPage from "./views/LoginPage";
```

- [ ] **Step 8: Verificar visualmente**

```bash
cd web && npm run dev
```

Abrir `http://localhost:5173/users/login`. Esperado: o título "Autenticar usuário", o aviso e o botão "Entrar". Clicar leva a `/home/private` (ainda a rota 404 nesta etapa) e o menu passa a mostrar "visitante" e "Sair". Clicar em "Sair" volta o menu a "Cadastrar / Entrar".

- [ ] **Step 9: Commit**

```bash
git add web/src/auth web/src/views/LoginPage.tsx web/src/App.tsx
git commit -m "feat: portao de sessao sem senha para as telas privadas"
```

---

### Task 13: Home privada

**Files:**
- Create: `web/src/components/StatsPanel.tsx`, `web/src/views/PrivateHome.tsx`
- Modify: `web/src/App.tsx`

**Interfaces:**
- Consumes: `listPrivateThings`, `readPrivateStats` (Task 5); `ThingCard`, `FilterDialog`, `useApi` (Task 10); `AuthGate` (Task 12)
- Produces: `<StatsPanel stats />`

Por D9 do spec, esta tela deixa o Bootstrap legado de `templates/home.html` e passa a usar os mesmos cards da home pública, mais o painel "Indicadores".

- [ ] **Step 1: Criar `web/src/components/StatsPanel.tsx`**

Os rótulos e a composição vêm de `templates/home.html`, incluindo o `record_unit` e o `retation_unit` que a API já devolve prontos.

```tsx
import type { Stats } from "../api/types";

interface Props {
  stats: Stats;
}

export default function StatsPanel({ stats }: Props) {
  return (
    <div className="col-pad">
      <h1 className="font-36px">Indicadores</h1>

      <div className="form-group font-17px">
        <div>
          <b>Plano:</b> {stats.plan}
        </div>
        <div>
          <b>Total de Registros:</b> {stats.records} {stats.record_unit}
        </div>
        <div>
          <b>Retenção:</b> {stats.retation_current} de {stats.retation_full}{" "}
          {stats.retation_unit}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Criar `web/src/views/PrivateHome.tsx`**

```tsx
import { useCallback, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { listPrivateThings, listSensorTags, listSensors, readPrivateStats } from "../api/endpoints";
import EmptyState from "../components/EmptyState";
import ErrorBanner from "../components/ErrorBanner";
import FilterDialog from "../components/FilterDialog";
import Loading from "../components/Loading";
import StatsPanel from "../components/StatsPanel";
import ThingCard from "../components/ThingCard";
import {
  type FilterKey,
  type Filters,
  filtersFromSearch,
  searchFromFilters,
} from "../lib/filters";
import { useApi } from "../lib/useApi";

export default function PrivateHome() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [dialogOpen, setDialogOpen] = useState(false);

  const search = searchParams.toString();
  const filters = useMemo(() => filtersFromSearch(search), [search]);

  const things = useApi(() => listPrivateThings(filters), [search]);
  const stats = useApi(() => readPrivateStats(), []);
  const sensors = useApi(() => listSensors(), []);
  const tags = useApi(() => listSensorTags(), []);

  const applyFilters = useCallback(
    (next: Filters) => {
      setSearchParams(new URLSearchParams(searchFromFilters(next)));
      setDialogOpen(false);
    },
    [setSearchParams],
  );

  const addFilter = useCallback(
    (key: FilterKey, value: string) => applyFilters({ ...filters, [key]: value }),
    [applyFilters, filters],
  );

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">Meus dispositivos</h1>
          <button className="font-16px" type="button" onClick={() => setDialogOpen(true)}>
            Filtros
          </button>
        </div>
      </section>

      <section className="cards">
        {things.loading && <Loading />}
        {things.error && <ErrorBanner message={things.error} />}
        {things.data?.length === 0 && <EmptyState />}
        {things.data && things.data.length > 0 && (
          <ul>
            {things.data.map((thing) => (
              <ThingCard key={thing.uuid} thing={thing} onFilter={addFilter} />
            ))}
          </ul>
        )}
      </section>

      <section className="home">
        {stats.error && <ErrorBanner message={stats.error} />}
        {stats.data && <StatsPanel stats={stats.data} />}
      </section>

      <FilterDialog
        open={dialogOpen}
        sensors={sensors.data ?? []}
        tags={tags.data ?? []}
        filters={filters}
        onApply={applyFilters}
        onClear={() => applyFilters({})}
        onClose={() => setDialogOpen(false)}
      />
    </>
  );
}
```

- [ ] **Step 3: Ligar a rota protegida em `web/src/App.tsx`**

Acrescentar dentro de `<Routes>`, antes da rota `*`:

```tsx
            <Route
              path="/home/private"
              element={
                <AuthGate>
                  <PrivateHome />
                </AuthGate>
              }
            />
```

E os imports:

```tsx
import AuthGate from "./auth/AuthGate";
import PrivateHome from "./views/PrivateHome";
```

- [ ] **Step 4: Verificar build e testes**

```bash
cd web && npm run build && npm test
```

Esperado: build conclui; 38 testes passam.

- [ ] **Step 5: Verificar visualmente**

```bash
cd web && npm run dev
```

1. Abrir `http://localhost:5173/home/private` sem sessão. Esperado: redireciona para `/users/login`.
2. Clicar em "Entrar" e voltar. Esperado: a lista de dispositivos da conta servida, com os mesmos cards da home pública, e o painel "Indicadores" com plano, total de registros e retenção.
3. Os filtros funcionam como na home pública.

- [ ] **Step 6: Commit**

```bash
git add web/src/components/StatsPanel.tsx web/src/views/PrivateHome.tsx web/src/App.tsx
git commit -m "feat: home privada com cards unificados e painel de indicadores"
```

---

### Task 14: Cadastro

**Files:**
- Create: `web/src/lib/locations.ts`, `web/src/views/SignUp.tsx`
- Modify: `web/src/App.tsx`

**Interfaces:**
- Consumes: `createAccount`, `PENDING_MESSAGE` (Task 5)
- Produces: `BRAZIL_STATES: Array<{ value: string; label: string }>`, `COUNTRIES: Array<{ value: string; label: string }>`

O formulário é completo e chama `POST /accounts`. Enquanto a rota não existir, a resposta é 404 e a tela mostra `Recurso ainda não disponível na API` — D6 do spec.

- [ ] **Step 1: Criar `web/src/lib/locations.ts`**

Transcrito de `base/constants.py`, que hoje oferece apenas o Brasil.

```ts
export const COUNTRIES = [{ value: "BR", label: "Brasil" }] as const;

export const BRAZIL_STATES = [
  { value: "AC", label: "Acre" },
  { value: "AL", label: "Alagoas" },
  { value: "AP", label: "Amapá" },
  { value: "AM", label: "Amazonas" },
  { value: "BA", label: "Bahia" },
  { value: "CE", label: "Ceará" },
  { value: "DF", label: "Distrito Federal" },
  { value: "ES", label: "Espírito Santo" },
  { value: "GO", label: "Goiás" },
  { value: "MA", label: "Maranhão" },
  { value: "MT", label: "Mato Grosso" },
  { value: "MS", label: "Mato Grosso do Sul" },
  { value: "MG", label: "Minas Gerais" },
  { value: "PA", label: "Pará" },
  { value: "PB", label: "Paraíba" },
  { value: "PR", label: "Paraná" },
  { value: "PE", label: "Pernambuco" },
  { value: "PI", label: "Piauí" },
  { value: "RJ", label: "Rio de Janeiro" },
  { value: "RN", label: "Rio Grande do Norte" },
  { value: "RS", label: "Rio Grande do Sul" },
  { value: "RO", label: "Rondônia" },
  { value: "RR", label: "Roraima" },
  { value: "SC", label: "Santa Catarina" },
  { value: "SP", label: "São Paulo" },
  { value: "SE", label: "Sergipe" },
  { value: "TO", label: "Tocantins" },
] as const;
```

> **Confira a transcrição** contra `base/constants.py` antes de seguir: essa lista foi copiada e um estado a menos passaria despercebido. `grep -c "('" base/constants.py` deve indicar 28 tuplas (27 estados + 1 país).

- [ ] **Step 2: Criar `web/src/views/SignUp.tsx`**

```tsx
import { type FormEvent, useState } from "react";

import { ApiError } from "../api/client";
import { createAccount } from "../api/endpoints";
import ErrorBanner from "../components/ErrorBanner";
import { BRAZIL_STATES, COUNTRIES } from "../lib/locations";

const EMPTY = {
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  password: "",
  city: "",
  state: BRAZIL_STATES[0].value,
  country: COUNTRIES[0].value,
};

export default function SignUp() {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [sending, setSending] = useState(false);

  function update(field: keyof typeof EMPTY, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSending(true);

    try {
      await createAccount(form);
      setDone(true);
    } catch (caught: unknown) {
      setError(
        caught instanceof ApiError ? caught.message : "Falha inesperada ao criar a conta",
      );
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">Cadastro</h1>
        </div>
      </section>

      <section className="signUp">
        {error && <ErrorBanner message={error} />}
        {done && <p className="font-17px">Conta criada.</p>}

        <form onSubmit={submit}>
          <p>
            <label className="font-17px" htmlFor="username">
              Usuário
            </label>
            <input
              id="username"
              value={form.username}
              onChange={(event) => update("username", event.target.value)}
              required
            />
          </p>
          <p>
            <label className="font-17px" htmlFor="first_name">
              Nome
            </label>
            <input
              id="first_name"
              value={form.first_name}
              onChange={(event) => update("first_name", event.target.value)}
              required
            />
          </p>
          <p>
            <label className="font-17px" htmlFor="last_name">
              Sobrenome
            </label>
            <input
              id="last_name"
              value={form.last_name}
              onChange={(event) => update("last_name", event.target.value)}
              required
            />
          </p>
          <p>
            <label className="font-17px" htmlFor="email">
              E-mail
            </label>
            <input
              id="email"
              type="email"
              value={form.email}
              onChange={(event) => update("email", event.target.value)}
              required
            />
          </p>
          <p>
            <label className="font-17px" htmlFor="password">
              Senha
            </label>
            <input
              id="password"
              type="password"
              value={form.password}
              onChange={(event) => update("password", event.target.value)}
              required
            />
          </p>
          <p>
            <label className="font-17px" htmlFor="city">
              Cidade
            </label>
            <input
              id="city"
              value={form.city}
              onChange={(event) => update("city", event.target.value)}
              required
            />
          </p>
          <p>
            <label className="font-17px" htmlFor="state">
              Estado
            </label>
            <select
              id="state"
              value={form.state}
              onChange={(event) => update("state", event.target.value)}
            >
              {BRAZIL_STATES.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </p>
          <p>
            <label className="font-17px" htmlFor="country">
              País
            </label>
            <select
              id="country"
              value={form.country}
              onChange={(event) => update("country", event.target.value)}
            >
              {COUNTRIES.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </p>

          <button type="submit" className="font-16px" disabled={sending}>
            <span>{sending ? "Enviando…" : "Cadastrar"}</span>
          </button>
        </form>
      </section>
    </>
  );
}
```

- [ ] **Step 3: Ligar a rota em `web/src/App.tsx`**

Acrescentar dentro de `<Routes>`, antes da rota `*`:

```tsx
            <Route path="/users/signup" element={<SignUp />} />
```

E o import:

```tsx
import SignUp from "./views/SignUp";
```

- [ ] **Step 4: Verificar build e testes**

```bash
cd web && npm run build && npm test
```

Esperado: build conclui; 38 testes passam.

- [ ] **Step 5: Verificar visualmente**

```bash
cd web && npm run dev
```

Abrir `http://localhost:5173/users/signup`. Esperado: o formulário completo, com o select de estados listando os 27. Preencher e enviar deve mostrar exatamente `Recurso ainda não disponível na API` — confirmando que a rota pendente é reportada como pendência, não como erro genérico.

- [ ] **Step 6: Commit**

```bash
git add web/src/lib/locations.ts web/src/views/SignUp.tsx web/src/App.tsx
git commit -m "feat: tela de cadastro contra a rota POST /accounts prevista"
```

---

### Task 15: Minha conta

**Files:**
- Create: `web/src/views/Account.tsx`
- Modify: `web/src/App.tsx`

**Interfaces:**
- Consumes: `readPrivateAccount`, `savePrivateAccount`, `listPrivateThings`, `linkThing`, `listSensorUnits`, `savePreferredUnit` (Task 5); `readChartType`, `writeChartType` (Task 8); `AuthGate` (Task 12); `BRAZIL_STATES`, `COUNTRIES` (Task 14)
- Produces: nada consumido adiante

Três abas, como no `templates/account.html`: Perfil, Centrais e Sensores. A aba ativa vem do parâmetro `:tab` da rota.

- [ ] **Step 1: Criar `web/src/views/Account.tsx`**

```tsx
import { type FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError } from "../api/client";
import {
  type ProfileInput,
  linkThing,
  listPrivateThings,
  listSensorUnits,
  readPrivateAccount,
  savePreferredUnit,
  savePrivateAccount,
} from "../api/endpoints";
import type { ThingSensor } from "../api/types";
import ErrorBanner from "../components/ErrorBanner";
import Loading from "../components/Loading";
import { BRAZIL_STATES, COUNTRIES } from "../lib/locations";
import { type ChartType, readChartType, writeChartType } from "../lib/prefs";
import { useApi } from "../lib/useApi";

const TABS = [
  { id: "profile", label: "Perfil" },
  { id: "things", label: "Centrais" },
  { id: "sensors", label: "Sensores" },
] as const;

const CHART_TYPES: Array<{ value: ChartType; label: string }> = [
  { value: "line", label: "Linha" },
  { value: "bar", label: "Barra" },
  { value: "table", label: "Tabela" },
  { value: "display", label: "Display" },
];

// MAX_PRECISION as the running Django code defines it in users/views.py.
// base/constants.py carries a stale 5 that no view reads.
const PRECISIONS = [0, 1, 2];

function message(caught: unknown, fallback: string): string {
  return caught instanceof ApiError ? caught.message : fallback;
}

function ProfileTab() {
  const account = useApi(() => readPrivateAccount(), []);
  const [form, setForm] = useState<ProfileInput | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (account.data) {
      const { first_name, last_name, email, city, state, country } = account.data;
      setForm({ first_name, last_name, email, city, state, country });
    }
  }, [account.data]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!form) return;

    setError(null);
    setSaved(false);
    try {
      await savePrivateAccount(form);
      setSaved(true);
    } catch (caught: unknown) {
      setError(message(caught, "Falha inesperada ao salvar o perfil"));
    }
  }

  function update(field: keyof ProfileInput, value: string) {
    setForm((current) => (current ? { ...current, [field]: value } : current));
  }

  if (account.loading) return <Loading />;
  if (account.error) return <ErrorBanner message={account.error} />;
  if (!form) return null;

  return (
    <form onSubmit={submit}>
      {error && <ErrorBanner message={error} />}
      {saved && <p className="font-17px">Perfil salvo.</p>}

      <p>
        <label className="font-16px" htmlFor="first_name">
          Nome
        </label>
        <input
          id="first_name"
          value={form.first_name}
          onChange={(event) => update("first_name", event.target.value)}
        />
      </p>
      <p>
        <label className="font-16px" htmlFor="last_name">
          Sobrenome
        </label>
        <input
          id="last_name"
          value={form.last_name}
          onChange={(event) => update("last_name", event.target.value)}
        />
      </p>
      <p>
        <label className="font-16px" htmlFor="email">
          E-mail
        </label>
        <input
          id="email"
          type="email"
          value={form.email}
          onChange={(event) => update("email", event.target.value)}
        />
      </p>
      <p>
        <label className="font-16px" htmlFor="city">
          Cidade
        </label>
        <input
          id="city"
          value={form.city}
          onChange={(event) => update("city", event.target.value)}
        />
      </p>
      <p>
        <label className="font-16px" htmlFor="state">
          Estado
        </label>
        <select
          id="state"
          value={form.state}
          onChange={(event) => update("state", event.target.value)}
        >
          {BRAZIL_STATES.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </p>
      <p>
        <label className="font-16px" htmlFor="country">
          País
        </label>
        <select
          id="country"
          value={form.country}
          onChange={(event) => update("country", event.target.value)}
        >
          {COUNTRIES.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </p>

      <button type="submit">Alterar</button>
    </form>
  );
}

function ThingsTab() {
  const things = useApi(() => listPrivateThings(), []);
  const [uuid, setUuid] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    try {
      await linkThing({ uuid });
      setUuid("");
    } catch (caught: unknown) {
      setError(message(caught, "Falha inesperada ao vincular a central"));
    }
  }

  return (
    <>
      <form onSubmit={submit}>
        {error && <ErrorBanner message={error} />}
        <p>
          <label className="font-16px" htmlFor="uuid">
            Nova central
          </label>
          <input
            id="uuid"
            value={uuid}
            onChange={(event) => setUuid(event.target.value)}
            placeholder="UUID"
            required
          />
        </p>
        <button type="submit">Adicionar</button>
      </form>

      {things.loading && <Loading />}
      {things.error && <ErrorBanner message={things.error} />}
      {things.data && (
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Central</th>
              <th>UUID</th>
            </tr>
          </thead>
          <tbody>
            {things.data.map((thing) => (
              <tr key={thing.uuid}>
                <td>{thing.thing}</td>
                <td>{thing.uuid}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}

function SensorRow({ sensor }: { sensor: ThingSensor; }) {
  const units = useApi(() => listSensorUnits(), []);
  const [error, setError] = useState<string | null>(null);
  const [unitId, setUnitId] = useState<number | null>(null);
  const [precision, setPrecision] = useState(PRECISIONS[0]);

  const sensorUnits = (units.data ?? []).filter((unit) => unit.id_sensor === sensor.id);

  // The chart type is presentation only, so it stays in localStorage. The unit
  // and the precision are moving to the database, where the API can apply them
  // before serving the value -- hence the PUT rather than a local write.
  async function persist(nextUnitId: number | null, nextPrecision: number) {
    if (nextUnitId === null) return;

    setError(null);
    try {
      await savePreferredUnit({
        id_sensor: sensor.id,
        id_unit: nextUnitId,
        precision: nextPrecision,
      });
    } catch (caught: unknown) {
      setError(message(caught, "Falha inesperada ao salvar a preferência"));
    }
  }

  return (
    <tr>
      <td>{sensor.name}</td>

      <td>
        <select
          defaultValue={readChartType(sensor.id)}
          onChange={(event) => writeChartType(sensor.id, event.target.value as ChartType)}
        >
          {CHART_TYPES.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </td>

      <td>
        {units.error ? (
          <span className="font-13px">{units.error}</span>
        ) : (
          <select
            disabled={sensorUnits.length === 0}
            value={unitId ?? ""}
            onChange={(event) => {
              const next = Number(event.target.value);
              setUnitId(next);
              void persist(next, precision);
            }}
          >
            <option value="">—</option>
            {sensorUnits.map((unit) => (
              <option key={unit.id} value={unit.id}>
                {unit.name}
              </option>
            ))}
          </select>
        )}
      </td>

      <td>
        <select
          value={precision}
          onChange={(event) => {
            const next = Number(event.target.value);
            setPrecision(next);
            void persist(unitId, next);
          }}
        >
          {PRECISIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </td>

      <td>{error && <ErrorBanner message={error} />}</td>
    </tr>
  );
}

function SensorsTab() {
  const things = useApi(() => listPrivateThings(), []);

  // One row per distinct sensor across the account's things.
  const sensors = Array.from(
    new Map(
      (things.data ?? []).flatMap((thing) =>
        thing.sensors.map((sensor) => [sensor.id, sensor] as const),
      ),
    ).values(),
  );

  return (
    <>
      {things.loading && <Loading />}
      {things.error && <ErrorBanner message={things.error} />}

      <table className="table table-striped">
        <thead>
          <tr>
            <th>Sensor</th>
            <th>Gráfico</th>
            <th>Unidade</th>
            <th>Precisão</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {sensors.map((sensor) => (
            <SensorRow key={sensor.id} sensor={sensor} />
          ))}
        </tbody>
      </table>
    </>
  );
}

export default function Account() {
  const { username = "", tab = "profile" } = useParams();
  const active = TABS.some((candidate) => candidate.id === tab) ? tab : "profile";

  return (
    <>
      <section className="home">
        <div>
          <h1 className="font-36px">Minha conta</h1>
        </div>
      </section>

      <section className="cards">
        <ul className="nav nav-tabs">
          {TABS.map((candidate) => (
            <li key={candidate.id} className={active === candidate.id ? "active" : ""}>
              <Link className="nav-link" to={`/users/account/${username}/${candidate.id}`}>
                {candidate.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="tab-content">
          {active === "profile" && <ProfileTab />}
          {active === "things" && <ThingsTab />}
          {active === "sensors" && <SensorsTab />}
        </div>
      </section>
    </>
  );
}
```

- [ ] **Step 2: Ligar a rota protegida em `web/src/App.tsx`**

Acrescentar dentro de `<Routes>`, antes da rota `*`:

```tsx
            <Route
              path="/users/account/:username/:tab"
              element={
                <AuthGate>
                  <Account />
                </AuthGate>
              }
            />
```

E o import:

```tsx
import Account from "./views/Account";
```

- [ ] **Step 3: Verificar build e testes**

```bash
cd web && npm run build && npm test
```

Esperado: build conclui; 38 testes passam.

- [ ] **Step 4: Verificar visualmente**

```bash
cd web && npm run dev
```

Entrar pelo login e abrir `/users/account/visitante/profile`. Esperado:

1. As três abas — Perfil, Centrais, Sensores — navegáveis, com a URL mudando.
2. Perfil mostra `Recurso ainda não disponível na API` (a rota `GET /accounts/private` não existe).
3. Centrais lista os dispositivos da conta; "Adicionar" mostra a mesma mensagem de pendência.
4. Sensores lista os sensores com o select de tipo de gráfico funcionando, e a coluna Unidade mostrando a mensagem de pendência.
5. Trocar a precisão de um sensor mostra a mensagem de pendência (o `PUT` não existe ainda).
6. Escolher "Barra" para um sensor e abrir o detalhe daquele dispositivo: o gráfico vem em barras.

- [ ] **Step 5: Commit**

```bash
git add web/src/views/Account.tsx web/src/App.tsx
git commit -m "feat: tela de conta com as abas de perfil, centrais e sensores"
```

---

## Fase 4 — Infraestrutura

### Task 16: Esqueleto do CDK e configurações

**Files:**
- Create: `infra/app.py`, `infra/cdk.json`, `infra/requirements.txt`, `infra/stacks/__init__.py`, `infra/stacks/settings.py`, `infra/tests/__init__.py`, `infra/tests/unit/__init__.py`, `infra/tests/unit/test_settings.py`

**Interfaces:**
- Consumes: `.env` do repositório
- Produces: `InfrastructureSettings(tenant, environment_name, aws_region, aws_account, resource_prefix, stack_prefix, config_parameter_path)` e `load_settings(app)`. Consumido pela Task 17.

- [ ] **Step 1: Criar `infra/requirements.txt`**

```
aws-cdk-lib==2.243.0
constructs==10.5.1
boto3==1.42.85
botocore==1.42.85
pytest==8.4.2
```

- [ ] **Step 2: Criar o ambiente virtual e instalar**

```bash
cd /mnt/storage/git/sensoriando_webservice/infra
python3 -m venv .venv
./.venv/bin/pip install --quiet -r requirements.txt
./.venv/bin/python -c "import aws_cdk; print(aws_cdk.__name__)"
```

Esperado: imprime `aws_cdk`.

- [ ] **Step 3: Criar os arquivos de pacote vazios**

```bash
cd /mnt/storage/git/sensoriando_webservice/infra
mkdir -p stacks tests/unit
touch stacks/__init__.py tests/__init__.py tests/unit/__init__.py
```

- [ ] **Step 4: Escrever o teste de configurações que falha**

Criar `infra/tests/unit/test_settings.py`:

```python
import pytest

from stacks.settings import read_environment_file


def test_reads_exported_variables(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "export SENSORIANDO_ENVIRONMENT=development\n"
        "export AWS_REGION=us-east-2\n",
        encoding="utf-8",
    )

    assert read_environment_file(env_file) == {
        "SENSORIANDO_ENVIRONMENT": "development",
        "AWS_REGION": "us-east-2",
    }


def test_ignores_comments_and_blank_lines(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# a comment\n\nexport AWS_REGION=us-east-2\n",
        encoding="utf-8",
    )

    assert read_environment_file(env_file) == {"AWS_REGION": "us-east-2"}


def test_strips_an_inline_comment(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("export AWS_REGION=us-east-2  # the region\n", encoding="utf-8")

    assert read_environment_file(env_file) == {"AWS_REGION": "us-east-2"}


def test_keeps_a_hash_inside_a_quoted_value(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('export TOKEN="abc#123"\n', encoding="utf-8")

    assert read_environment_file(env_file) == {"TOKEN": "abc#123"}


def test_returns_nothing_for_a_missing_file(tmp_path):
    assert read_environment_file(tmp_path / "absent") == {}
```

- [ ] **Step 5: Rodar o teste e confirmar que falha**

```bash
cd /mnt/storage/git/sensoriando_webservice/infra
./.venv/bin/python -m pytest tests/unit/test_settings.py -v
```

Esperado: FAIL — `ModuleNotFoundError: No module named 'stacks.settings'`.

- [ ] **Step 6: Implementar `infra/stacks/settings.py`**

Portado de `SENSORIANDO_API/infra/stacks/settings.py`, para que os dois repositórios derivem os nomes de recurso da mesma forma.

```python
"""Deploy-time settings, read from the repository `.env`.

Everything here is derived from the target environment, and everything derived
is a name: resource prefixes and the Parameter Store path. No configurable
value and no secret passes through this module.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

import aws_cdk as cdk

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

TENANT = "sensoriando"
ENVIRONMENT_NAME_PATTERN = re.compile(r"[a-z][a-z0-9]*")


@dataclass(frozen=True)
class InfrastructureSettings:
    tenant: str
    environment_name: str
    aws_region: str
    aws_account: str | None
    resource_prefix: str
    stack_prefix: str
    config_parameter_path: str


def read_environment_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        value = value.strip()
        # An inline comment (`KEY=value  # note`) is only a comment outside a
        # quoted value -- shell itself would not treat `#` inside quotes as one
        # either. A trailing " #" would otherwise silently join the value,
        # producing an unrecognizable AWS region instead of a clear error.
        if not value.startswith(("'", '"')) and " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        values[key.strip()] = value.strip("'\"")

    return values


def load_settings(app: cdk.App) -> InfrastructureSettings:
    file_values = read_environment_file(REPOSITORY_ROOT / ".env")

    environment_name = os.getenv("SENSORIANDO_ENVIRONMENT") or file_values.get(
        "SENSORIANDO_ENVIRONMENT"
    )
    if not environment_name or not ENVIRONMENT_NAME_PATTERN.fullmatch(environment_name):
        raise ValueError(
            "SENSORIANDO_ENVIRONMENT must be defined and contain only lowercase "
            "letters and digits, starting with a letter"
        )

    aws_region = os.getenv("AWS_REGION") or file_values.get("AWS_REGION")
    if not aws_region:
        raise ValueError("AWS_REGION must be defined in .env")

    aws_account = (
        os.getenv("AWS_ACCOUNT_ID")
        or app.node.try_get_context("aws_account")
        or os.getenv("CDK_DEFAULT_ACCOUNT")
    )

    return InfrastructureSettings(
        tenant=TENANT,
        environment_name=environment_name,
        aws_region=aws_region,
        aws_account=aws_account,
        resource_prefix=f"{TENANT}_{environment_name}",
        stack_prefix=f"{TENANT}-{environment_name}",
        config_parameter_path=f"/{TENANT}/{environment_name}/common",
    )
```

- [ ] **Step 7: Rodar o teste e confirmar que passa**

```bash
cd /mnt/storage/git/sensoriando_webservice/infra
./.venv/bin/python -m pytest tests/unit/test_settings.py -v
```

Esperado: PASS, 5 testes.

- [ ] **Step 8: Criar `infra/app.py`**

```python
#!/usr/bin/env python3
"""CDK entry point: one stack, the static site."""

import aws_cdk as cdk

from stacks.settings import load_settings
from stacks.web_stack import WebStack

app = cdk.App()
settings = load_settings(app)

WebStack(
    app,
    f"{settings.stack_prefix}-web",
    env=cdk.Environment(
        account=settings.aws_account,
        region=settings.aws_region,
    ),
    settings=settings,
)

app.synth()
```

- [ ] **Step 9: Criar `infra/cdk.json`**

```json
{
  "app": "python3 app.py",
  "watch": {
    "include": ["**"],
    "exclude": [
      "README.md",
      "cdk*.json",
      "requirements*.txt",
      "**/__init__.py",
      "**/__pycache__",
      "tests"
    ]
  },
  "context": {
    "@aws-cdk/core:target-partitions": ["aws"],
    "@aws-cdk/aws-iam:minimizePolicies": true,
    "@aws-cdk/aws-s3:createDefaultLoggingPolicy": true,
    "@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy": true,
    "@aws-cdk/aws-s3:publicAccessBlockedByDefault": true,
    "@aws-cdk/core:validateSnapshotRemovalPolicy": true,
    "@aws-cdk/core:enablePartitionLiterals": true,
    "@aws-cdk/aws-route53-patterns:useDistribution": true
  }
}
```

> `app.py` importa `stacks.web_stack`, criado na Task 17. `cdk ls` e `cdk synth` só funcionam depois dela; os testes desta task não dependem disso.

- [ ] **Step 10: Commit**

```bash
git add infra/app.py infra/cdk.json infra/requirements.txt infra/stacks infra/tests
git commit -m "feat: esqueleto do CDK com as configuracoes lidas do .env"
```

---

### Task 17: Stack do site estático

**Files:**
- Create: `infra/stacks/web_stack.py`, `infra/tests/unit/test_web_stack.py`

**Interfaces:**
- Consumes: `InfrastructureSettings` (Task 16)
- Produces: `WebStack(scope, construct_id, *, settings, web_dist_path=None, **kwargs)` com o atributo `distribution` e o output `SensoriandoWebUrl`

- [ ] **Step 1: Escrever os testes que falham**

Criar `infra/tests/unit/test_web_stack.py`:

```python
import aws_cdk as cdk
import aws_cdk.assertions as assertions

from stacks.settings import InfrastructureSettings
from stacks.web_stack import WebStack


def _settings() -> InfrastructureSettings:
    return InfrastructureSettings(
        tenant="sensoriando",
        environment_name="development",
        aws_region="us-east-2",
        aws_account="123456789012",
        resource_prefix="sensoriando_development",
        stack_prefix="sensoriando-development",
        config_parameter_path="/sensoriando/development/common",
    )


def _template(dist_path) -> assertions.Template:
    app = cdk.App()
    settings = _settings()
    stack = WebStack(
        app,
        "sensoriando-development-web",
        settings=settings,
        web_dist_path=str(dist_path),
        env=cdk.Environment(account=settings.aws_account, region=settings.aws_region),
    )
    return assertions.Template.from_stack(stack)


def _built_dist(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html>", encoding="utf-8")
    return dist


def test_provisions_a_bucket_and_a_distribution(tmp_path):
    template = _template(_built_dist(tmp_path))

    template.resource_count_is("AWS::S3::Bucket", 1)
    template.resource_count_is("AWS::CloudFront::Distribution", 1)


def test_the_bucket_blocks_every_form_of_public_access(tmp_path):
    template = _template(_built_dist(tmp_path))

    template.has_resource_properties(
        "AWS::S3::Bucket",
        {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True,
            }
        },
    )


def test_client_errors_fall_back_to_the_spa_entry_point(tmp_path):
    """A refresh on /thing/detail/<uuid> must not 403: S3 has no such key."""
    template = _template(_built_dist(tmp_path))

    distributions = template.find_resources("AWS::CloudFront::Distribution")
    (distribution,) = distributions.values()
    responses = distribution["Properties"]["DistributionConfig"]["CustomErrorResponses"]

    assert {
        (item["ErrorCode"], item["ResponseCode"], item["ResponsePagePath"])
        for item in responses
    } == {(403, 200, "/index.html"), (404, 200, "/index.html")}


def test_publishes_the_build(tmp_path):
    template = _template(_built_dist(tmp_path))

    template.resource_count_is("Custom::CDKBucketDeployment", 1)


def test_skips_the_upload_when_the_build_is_absent(tmp_path):
    template = _template(tmp_path / "absent")

    template.resource_count_is("AWS::S3::Bucket", 1)
    template.resource_count_is("AWS::CloudFront::Distribution", 1)
    template.resource_count_is("Custom::CDKBucketDeployment", 0)


def test_exports_the_site_url(tmp_path):
    template = _template(_built_dist(tmp_path))

    outputs = template.find_outputs("*")
    assert any(key.startswith("SensoriandoWebUrl") for key in outputs)
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

```bash
cd /mnt/storage/git/sensoriando_webservice/infra
./.venv/bin/python -m pytest tests/unit/test_web_stack.py -v
```

Esperado: FAIL — `ModuleNotFoundError: No module named 'stacks.web_stack'`.

- [ ] **Step 3: Implementar `infra/stacks/web_stack.py`**

```python
import sys
from pathlib import Path
from typing import Any, Optional

from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3deploy

from stacks.settings import InfrastructureSettings

# Repo-root-relative path to the built SPA (gitignored; produced by
# `npm run build` in web/).
DEFAULT_WEB_DIST = Path(__file__).resolve().parents[2] / "web" / "dist"


class WebStack(Stack):
    """The static site: a private bucket, fronted by CloudFront."""

    def __init__(
        self,
        scope: Any,
        construct_id: str,
        *,
        settings: InfrastructureSettings,
        web_dist_path: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "WebBucket",
            bucket_name=f"{settings.stack_prefix}-web-{settings.aws_account}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # The SPA owns its routes, but S3 only knows the keys it stores. Asking
        # for /thing/detail/<uuid> is a miss there, so both client errors are
        # rewritten to the entry point and the router takes over. Without this,
        # every refresh on a deep link would be a 403.
        self.distribution = cloudfront.Distribution(
            self,
            "WebDistribution",
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
            ],
        )

        # Publish the built SPA and invalidate the cache. Skipped with a warning
        # when the build output is missing, so a synth on a fresh checkout does
        # not fail. Note the blind spot: a *stale* dist/ is uploaded silently,
        # which is why `make deploy` always rebuilds first.
        dist_path = Path(web_dist_path) if web_dist_path else DEFAULT_WEB_DIST
        if dist_path.is_dir():
            s3deploy.BucketDeployment(
                self,
                "WebDeployment",
                sources=[s3deploy.Source.asset(str(dist_path))],
                destination_bucket=bucket,
                distribution=self.distribution,
                distribution_paths=["/*"],
            )
        else:
            print(
                f"[WebStack] WARNING: {dist_path} not found; skipping upload. "
                "Run `npm run build` in web/ before deploying this stack.",
                file=sys.stderr,
            )

        CfnOutput(
            self,
            "SensoriandoWebUrl",
            value=f"https://{self.distribution.distribution_domain_name}",
            export_name=f"{settings.stack_prefix}-web-url",
        )
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

```bash
cd /mnt/storage/git/sensoriando_webservice/infra
./.venv/bin/python -m pytest tests/unit -v
```

Esperado: PASS, 12 testes (5 de settings + 7 de web_stack).

- [ ] **Step 5: Verificar que o synth funciona de ponta a ponta**

```bash
cd /mnt/storage/git/sensoriando_webservice
set -a; . ./.env; set +a
cd infra && ./.venv/bin/python -c "
import sys
sys.argv = ['app.py']
exec(open('app.py').read())
" && echo "synth ok"
```

Esperado: imprime `synth ok`. Se `web/dist` não existir, imprime antes o aviso `[WebStack] WARNING: ... not found` — que é o comportamento correto.

- [ ] **Step 6: Commit**

```bash
git add infra/stacks/web_stack.py infra/tests/unit/test_web_stack.py
git commit -m "feat: stack do site estatico em S3 com CloudFront"
```

---

### Task 18: Parâmetros e automação

**Files:**
- Create: `scripts/config_parameters.py`, `Makefile`, `infra/README.md`

**Interfaces:**
- Consumes: `.env`
- Produces: `make deploy|destroy|ls|test|config-check|config-ensure`

Por D8 do spec, o manifesto `PARAMETERS` nasce vazio: as decisões anteriores não deixaram nenhum segredo para guardar. O mecanismo entra agora para que a primeira chave real seja só uma linha declarada.

- [ ] **Step 1: Criar `scripts/config_parameters.py`**

```python
#!/usr/bin/env python3
"""Publish and inspect this environment's configuration in SSM Parameter Store.

One parameter per key, under /sensoriando/<environment>/web.

Usage:
    python scripts/config_parameters.py check  [--env development]
    python scripts/config_parameters.py ensure [--env development]

The manifest below is empty on purpose. The static site holds no secret: the
API URL is discovered from CloudFormation at build time, there is no password
(the login is a passwordless gate), and there is no custom domain or
certificate yet. The mechanism exists so that the first real key -- Cognito
ids, a domain, a certificate ARN -- is one declaration rather than a new
script. See the design document, decision D8.
"""

import argparse
import os
import sys
from getpass import getpass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _dotenv import load_dotenv  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TENANT = "sensoriando"
DOMAIN = "web"

# key -> stored as SecureString
PARAMETERS: dict[str, bool] = {}


def parameter_path(environment_name: str, key: str) -> str:
    return f"/{TENANT}/{environment_name}/{DOMAIN}/{key}"


def missing_keys(existing: set[str]) -> list[str]:
    return [key for key in PARAMETERS if key not in existing]


def _client(region: str | None, profile: str | None):
    import boto3

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    return session.client("ssm", region_name=region) if region else session.client("ssm")


def _existing_keys(client, environment_name: str) -> set[str]:
    path = f"/{TENANT}/{environment_name}/{DOMAIN}"
    found: set[str] = set()

    paginator = client.get_paginator("get_parameters_by_path")
    for page in paginator.paginate(Path=path, Recursive=True, WithDecryption=False):
        for parameter in page["Parameters"]:
            found.add(parameter["Name"].rsplit("/", 1)[-1])

    return found


def _put(client, environment_name: str, key: str, value: str) -> None:
    client.put_parameter(
        Name=parameter_path(environment_name, key),
        Value=value,
        Type="SecureString" if PARAMETERS[key] else "String",
        Overwrite=True,
    )


def _ask(key: str) -> str:
    prompt = f"value for {key}: "
    return getpass(prompt) if PARAMETERS[key] else input(prompt)


def command_check(client, environment_name: str) -> int:
    missing = missing_keys(_existing_keys(client, environment_name))

    if missing:
        print(f"missing in {environment_name}: {', '.join(missing)}")
        return 1

    print(f"every key is present in {environment_name}")
    return 0


def command_ensure(client, environment_name: str) -> int:
    for key in missing_keys(_existing_keys(client, environment_name)):
        value = os.environ.get(key) or _ask(key)
        if not value:
            print(f"{key} has no value; aborting")
            return 1
        _put(client, environment_name, key, value)
        print(f"published {parameter_path(environment_name, key)}")

    return 0


COMMANDS = {"check": command_check, "ensure": command_ensure}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("--env", dest="environment_name")
    arguments = parser.parse_args()

    file_values = load_dotenv(REPOSITORY_ROOT / ".env")

    environment_name = (
        arguments.environment_name
        or os.environ.get("SENSORIANDO_ENVIRONMENT")
        or file_values.get("SENSORIANDO_ENVIRONMENT")
    )
    if not environment_name:
        sys.stderr.write("SENSORIANDO_ENVIRONMENT must be set\n")
        return 2

    # An empty manifest has nothing to read from AWS; skip the client entirely
    # so `make deploy` works without credentials until the first key exists.
    if not PARAMETERS:
        print(f"no configuration key is declared for {environment_name}")
        return 0

    region = os.environ.get("AWS_REGION") or file_values.get("AWS_REGION")
    profile = os.environ.get("AWS_PROFILE") or file_values.get("AWS_PROFILE")

    return COMMANDS[arguments.command](_client(region, profile), environment_name)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Verificar que o script roda com o manifesto vazio**

```bash
cd /mnt/storage/git/sensoriando_webservice
python3 scripts/config_parameters.py check
```

Esperado: `no configuration key is declared for development`, saída 0. Nenhuma chamada à AWS.

- [ ] **Step 3: Criar o `Makefile`**

```makefile
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
```

- [ ] **Step 4: Verificar os alvos de teste**

```bash
cd /mnt/storage/git/sensoriando_webservice && make test
```

Esperado: 38 testes de Vitest e 12 de pytest, todos passando.

- [ ] **Step 5: Criar `infra/README.md`**

````markdown
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
````

- [ ] **Step 6: Commit**

```bash
git add scripts/config_parameters.py Makefile infra/README.md
git commit -m "feat: automacao de deploy e mecanismo de parametros no SSM"
```

---

## Fase 5 — Corte

### Task 19: Remover o Django

**Files:**
- Delete: `api/`, `base/`, `core/`, `overview/`, `sensors/`, `users/`, `templates/`, `static/`, `manage.py`, `Dockerfile`, `docker-compose.yaml`, `requirements.txt`, `entrypoint.sh`, `init.sh`, `run.sh`, `.envrc`, `docs/virtualenv.md`
- Modify: `README.md`, `env.example`

**Interfaces:**
- Consumes: nada
- Produces: repositório sem Python de aplicação

- [ ] **Step 1: Confirmar que a tag existe antes de apagar qualquer coisa**

```bash
cd /mnt/storage/git/sensoriando_webservice
git rev-parse django-final
```

Esperado: um hash de commit. **Se falhar, pare** e crie a tag (Task 1, Step 1) antes de continuar — sem ela o site atual fica sem ponto de restauração óbvio.

- [ ] **Step 2: Confirmar que as imagens já foram copiadas**

```bash
ls web/public/img/background.jpeg web/public/img/bars.svg web/public/img/service-1.png web/public/img/nosensor.png
ls web/src/styles/style.css
```

Esperado: os cinco arquivos existem. São os únicos ativos de `static/` que o SPA usa; sem essa confirmação a remoção levaria junto assets ainda necessários.

- [ ] **Step 3: Remover a aplicação Django**

```bash
cd /mnt/storage/git/sensoriando_webservice
git rm -r --quiet api base core overview sensors users templates static
git rm --quiet manage.py Dockerfile docker-compose.yaml requirements.txt \
  entrypoint.sh init.sh run.sh .envrc docs/virtualenv.md
git status --short | head -20
```

- [ ] **Step 4: Reescrever o `README.md`**

````markdown
# Sensoriando Webservice

Front-end da plataforma Sensoriando: um SPA em React que apresenta os dados de
sensores lidos da [Sensoriando API](https://github.com/fdavidgithub/sensoriando_api).

Publicado como site estático em S3 + CloudFront.

## Arquitetura

```
Navegador → CloudFront → S3 (bundle estático)
    │
    └── HTTPS → API Gateway → Lambdas → PostgreSQL (Neon)
                (repositório sensoriando_api)
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
````

- [ ] **Step 5: Atualizar o `env.example`**

O arquivo atual já reflete só o que sobrou (ambiente, região, perfil). Acrescentar ao final a nota sobre o que deixou de ser necessário:

```bash
cat >> env.example <<'EOF'

# ---------------------------------------------------------------------------
# Nao ha mais variaveis de banco nem de Django aqui: este repositorio nao fala
# com o PostgreSQL. A URL da API e descoberta no build pelo output da stack
# sensoriando-<ambiente>-api no CloudFormation, e nao por variavel.
EOF
```

- [ ] **Step 6: Verificar que nada quebrou**

```bash
cd /mnt/storage/git/sensoriando_webservice && make test
```

Esperado: 38 testes de Vitest e 12 de pytest, todos passando. Nenhum deles dependia do Django.

- [ ] **Step 7: Verificar que o SPA ainda builda**

```bash
cd web && npm run build && ls dist/index.html
```

Esperado: `dist/index.html` presente — confirma que os assets copiados na Task 9 bastam.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "refactor: remover a aplicacao Django, substituida pelo SPA React

O app api/ virou duplicacao da Sensoriando API, que ja serve os mesmos
endpoints em Lambda. As telas foram reescritas em React sobre essa API.

O ultimo commit funcional do Django esta na tag django-final."
```

---

### Task 20: Atualizar as guidelines

**Files:**
- Modify: `docs/guidelines/stacks.md`, `docs/guidelines/architecture.md`, `docs/guidelines/coding-standards.md`
- Delete: `docs/guidelines/database.md`

**Interfaces:**
- Consumes: nada
- Produces: documentação coerente com a stack nova

Essas guidelines descrevem Django, DRF, JWT e Docker. Depois da Task 19 elas descrevem código que não existe mais — e uma guideline falsa é pior que nenhuma, porque é seguida.

- [ ] **Step 1: Reescrever `docs/guidelines/stacks.md`**

````markdown
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
````

- [ ] **Step 2: Reescrever `docs/guidelines/architecture.md`**

````markdown
# Arquitetura do Sistema Sensoriando Webservice

## Visão Geral

O Sensoriando Webservice é a camada de apresentação da plataforma Sensoriando
(*Hub de Sensores*). É um SPA estático: não tem servidor de aplicação, não tem
banco de dados e não guarda estado no servidor.

Todos os dados vêm da Sensoriando API, que por sua vez lê o PostgreSQL populado
pelo [Sensoriando Core](https://github.com/fdavidgithub/sensoriando_core/).

```
Navegador → CloudFront → S3 (bundle estático)
    │
    └── HTTPS → API Gateway → Lambdas → PostgreSQL (Neon)
```

---

## Módulos Principais

```
web/src/
  api/          client.ts     → única camada que conhece fetch; normaliza erro em ApiError
                endpoints.ts  → uma função por rota; marca as rotas ainda inexistentes
                types.ts      → formas dos dados da API
  auth/         session.ts    → portão de conveniência em localStorage
                AuthGate.tsx  → redireciona rotas privadas para o login
  lib/          filters.ts    → filtros ↔ query string
                prefs.ts      → período e tipo de gráfico em localStorage
                format.ts     → rótulos de gráfico por período
                country.ts    → alpha-2 → nome, via Intl.DisplayNames
                useApi.ts     → hook de carregamento/erro por view
  components/                 → apresentação; recebem dados por props, não fazem rede
  views/                      → telas; buscam dados e compõem componentes

infra/stacks/   settings.py   → nomes derivados do ambiente
                web_stack.py  → bucket privado + CloudFront + publicação do build

scripts/        resolve_api_url.py    → descobre a URL da API no CloudFormation
                config_parameters.py  → parâmetros no SSM
```

---

## Fluxo de Dados

1. No build, `vite.config.ts` chama `scripts/resolve_api_url.py`, que lê o output
   `SensoriandoApiUrl` da stack `sensoriando-<ambiente>-api` no CloudFormation e
   injeta a URL no bundle.
2. No navegador, cada view chama `useApi` com uma função de `api/endpoints.ts`.
3. `api/client.ts` faz a requisição e converte qualquer falha em `ApiError`.
4. A view renderiza um de três estados: carregando, erro ou vazio.

Rotas que a API ainda não expõe estão marcadas em `endpoints.ts`: um 404 vindo
delas vira a mensagem `Recurso ainda não disponível na API`, distinta de um erro
genérico, para que uma pendência conhecida não se confunda com um defeito.

---

## Decisões de Arquitetura

Registradas com a razão em
`docs/superpowers/specs/2026-08-12-migracao-react-cdk-design.md`.
````

- [ ] **Step 3: Reescrever `docs/guidelines/coding-standards.md`**

````markdown
# Padrões de Código — Sensoriando Webservice

## Linguagem

Todo código-fonte em **inglês**: identificadores, nomes de arquivo, comentários
e mensagens de log.

O texto visível ao usuário permanece em **português**.

---

## Convenções de Nomenclatura

| Elemento | Padrão |
|---|---|
| Componentes React | PascalCase, arquivo `PascalCase.tsx` |
| Funções e variáveis (TS) | camelCase |
| Tipos e interfaces (TS) | PascalCase |
| Constantes (TS) | UPPER_SNAKE_CASE |
| Módulos TS | `camelCase.ts` |
| Classes (Python) | PascalCase |
| Funções e variáveis (Python) | snake_case |
| Módulos Python | snake_case |

---

## Estrutura das Telas

Uma view busca dados por `useApi` e compõe componentes. Componentes de
apresentação recebem tudo por props e não fazem rede.

```tsx
export default function PublicHome() {
  const things = useApi(() => listPublicThings(filters), [search]);

  return (
    <section className="cards">
      {things.loading && <Loading />}
      {things.error && <ErrorBanner message={things.error} />}
      {things.data?.length === 0 && <EmptyState />}
      {things.data && things.data.length > 0 && (
        <ul>{things.data.map((thing) => <ThingCard key={thing.uuid} thing={thing} />)}</ul>
      )}
    </section>
  );
}
```

Nenhuma tela monta URL na mão: toda chamada passa por `api/endpoints.ts`.

---

## Tratamento de Erros

- Toda tela trata três estados: carregando, erro e vazio.
- Toda falha da API chega como `ApiError`, com `status` 0 para falha de rede.
- Um 404 de rota marcada como pendente vira a mensagem
  `Recurso ainda não disponível na API`.
- Falha de rede nunca resulta em tela branca.

---

## Configuração

- Nenhuma URL, credencial ou identificador de conta fixado em código.
- A URL da API é resolvida no build a partir do CloudFormation.
- Nomes de recurso derivam do `.env` (`SENSORIANDO_ENVIRONMENT`, `AWS_REGION`).

---

## Proibições

- Não usar `eval()` nem `new Function()`.
- Não modificar artefatos de build (`web/dist/`, `infra/cdk.out/`).
- Não introduzir bibliotecas fora de `docs/guidelines/stacks.md`.
- Não fazer rede a partir de componentes de apresentação.
- Não converter nem arredondar valores de sensor no front-end — a API é quem
  entrega o valor pronto (decisão D4 do documento de design).
- Não tratar o portão de sessão como controle de acesso: ele não protege dado
  nenhum (decisão D2).
````

- [ ] **Step 4: Remover `docs/guidelines/database.md`**

Este repositório não fala mais com o banco.

```bash
cd /mnt/storage/git/sensoriando_webservice
git rm --quiet docs/guidelines/database.md
```

- [ ] **Step 5: Conferir que nenhuma guideline ainda cita o Django**

```bash
grep -rn -i "django\|drf\|swagger\|psycopg\|docker-compose" docs/guidelines/ || echo "nenhuma referencia remanescente"
```

Esperado: `nenhuma referencia remanescente`.

- [ ] **Step 6: Commit**

```bash
git add -A docs/guidelines
git commit -m "docs: guidelines reescritas para a stack React + CDK"
```

---

## Verificação final

Depois da Task 20, antes de considerar a migração pronta:

- [ ] `make test` — 38 testes de Vitest e 12 de pytest passando
- [ ] `cd web && npm run build` — conclui e a URL da API aparece no bundle
- [ ] `make deploy` — a stack sobe e o output `SensoriandoWebUrl` é impresso
- [ ] Abrir a URL do CloudFront e percorrer: home pública → filtro → detalhe → F5 no detalhe (não pode dar 403) → login → home privada → conta
- [ ] Comparar a home pública e o detalhe com `web.sensoriando.com.br` lado a lado
- [ ] `git tag -l django-final` — a tag existe

O corte de DNS **não** faz parte desta entrega.

---

## Pendências deixadas para outros repositórios

Nada abaixo é trabalho deste repositório. Registrado para virar issue na
`SENSORIANDO_API`.

| Rota | Método | Serve |
|---|---|---|
| `/sensors/units` | GET | unidades disponíveis por sensor |
| `/accounts/private/sensors/units` | PUT | gravar unidade e precisão preferidas |
| `/accounts/private` | GET | perfil da conta servida, com e-mail |
| `/accounts/private` | PUT | editar perfil |
| `/accounts` | POST | criar conta |
| `/accounts/private/things` | POST | vincular thing à conta |

Além disso: quando `/data/detail` passar a devolver o valor já convertido,
devolver junto o símbolo da unidade, para o rótulo do gráfico voltar a exibi-lo.

E, fora de qualquer repositório: **revogar a chave de API do Google**
(`AIzaSyD-9tSr…`), que está no histórico do git deste repositório e continua
exposta mesmo após a remoção de `templates/map_world.js`.
