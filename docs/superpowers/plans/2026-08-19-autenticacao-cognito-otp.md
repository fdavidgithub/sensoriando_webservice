# Autenticação via Cognito com OTP — Plano de Implementação (sensoriando_webservice)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trocar o portão de sessão falso por autenticação real sem senha, e ligar as telas privadas às rotas de conta da API.

**Architecture:** O SPA continua um bundle estático que só consome a API — não fala com o Cognito, não carrega biblioteca de autenticação e não conhece pool id nem client id. O ID token vive apenas em memória; o refresh token fica no `localStorage` e é trocado por um novo ID token pelo próprio `client.ts` quando uma chamada volta 401.

**Tech Stack:** TypeScript 5.9, React 18, react-router-dom 7, Vite 8, vitest 4. **Nenhuma dependência nova.**

**Spec:** `docs/superpowers/specs/2026-08-19-autenticacao-cognito-otp-design.md`

## Global Constraints

- **Idioma:** todo código-fonte, nomes e comentários em **inglês**. Documentação em `docs/` em **português brasileiro**. (`AGENTS.md`)
- **Não commitar em `main` nem em `develop`.** O trabalho vive em `feat/autenticacao-cognito-otp`. (`AGENTS.md`)
- **TDD obrigatório:** Red → Green → Refactor.
- **Nenhuma biblioteca nova.** `docs/guidelines/stacks.md` lista o que é permitido: `react`, `react-dom`, `react-router-dom`, `chart.js`. Nada de gerenciador de estado global, nada de framework de CSS, nada de `eval()`/`new Function()`.
- **Componentes não fazem rede.** `components/` recebe dados por props; quem busca é `views/`. (`docs/guidelines/architecture.md`)
- **`api/client.ts` é a única camada que conhece `fetch`.**
- **Comando de teste:** `cd web && npm test` (ou `make test-web` na raiz).
- **Estilo:** o `style.css` portado. Nenhuma classe nova sem necessidade; reaproveite `font-17px`, `font-16px`, `signUp`, `home`.

---

# Fase 1 — Autenticação

---

### Task 1: `auth/session.ts` reescrito

**Files:**
- Modify: `web/src/auth/session.ts`
- Test: `web/src/auth/session.test.ts`

**Interfaces:**
- Produces:
  - `readSession(): Session | null` — `Session` é `{ username: string }`
  - `writeSession(username: string, refreshToken: string): void`
  - `clearSession(): void`
  - `readRefreshToken(): string | null`
  - `getIdToken(): string | null`
  - `setIdToken(token: string, expiresIn: number): void`
  - `clearIdToken(): void`

- [ ] **Step 1: Write the failing tests**

Substitua `web/src/auth/session.test.ts` por (mantendo o helper `memoryStorage` que já está lá):

```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  clearIdToken,
  clearSession,
  getIdToken,
  readRefreshToken,
  readSession,
  setIdToken,
  writeSession,
} from "./session";

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
  clearIdToken();
});

describe("session", () => {
  it("starts with no session", () => {
    expect(readSession()).toBeNull();
  });

  it("returns the session that was written", () => {
    writeSession("fulano", "refresh-token");
    expect(readSession()).toEqual({ username: "fulano" });
    expect(readRefreshToken()).toBe("refresh-token");
  });

  it("clears both the session and the token in memory", () => {
    writeSession("fulano", "refresh-token");
    setIdToken("id-token", 3600);

    clearSession();

    expect(readSession()).toBeNull();
    expect(getIdToken()).toBeNull();
  });

  it("treats a corrupted entry as no session instead of crashing", () => {
    localStorage.setItem("sensoriando.session", "{not json");
    expect(readSession()).toBeNull();
  });

  it("rejects a session left by the old convenience gate", () => {
    // It carried a username and no refresh token: it never authenticated
    // anyone, so it must not be honoured as a session now.
    localStorage.setItem("sensoriando.session", JSON.stringify({ username: "visitante" }));
    expect(readSession()).toBeNull();
  });
});

describe("the id token", () => {
  it("never reaches localStorage", () => {
    writeSession("fulano", "refresh-token");
    setIdToken("id-token", 3600);

    const stored = localStorage.getItem("sensoriando.session") ?? "";
    expect(stored).not.toContain("id-token");
    expect(getIdToken()).toBe("id-token");
  });

  it("is treated as absent once it is close to expiring", () => {
    setIdToken("id-token", 30);
    expect(getIdToken()).toBeNull();
  });

  it("is dropped by clearIdToken", () => {
    setIdToken("id-token", 3600);
    clearIdToken();
    expect(getIdToken()).toBeNull();
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd web && npx vitest run src/auth/session.test.ts`
Expected: FAIL — `setIdToken` não existe.

- [ ] **Step 3: Implement**

```ts
/**
 * The signed-in user, and the two tokens that keep them signed in.
 *
 * The ID token -- the one that opens every private route -- lives only in this
 * module's memory and dies with the tab. Persisting it would leave the
 * credential that grants immediate access sitting in storage for its whole
 * hour; keeping it here narrows that window to the page's lifetime.
 *
 * The refresh token does persist, because a session that ended on every reload
 * would be unusable. It buys nothing on its own: it has to be exchanged at
 * POST /auth/refresh before anything can be read.
 *
 * Cognito issues it for 30 days and does not rotate it, so the window does not
 * slide -- 30 days after signing in, the user does the OTP again.
 */

const SESSION_KEY = "sensoriando.session";

// A token that expires while the request is still in flight costs a round trip
// and a retry. Renewing a minute early costs nothing.
const EXPIRY_SLACK_MS = 60_000;

export interface Session {
  username: string;
}

interface StoredSession {
  username: string;
  refreshToken: string;
}

let idToken: string | null = null;
let idTokenExpiresAt = 0;

function readStored(): StoredSession | null {
  const stored = localStorage.getItem(SESSION_KEY);
  if (!stored) return null;

  try {
    const parsed = JSON.parse(stored) as Partial<StoredSession>;
    // A session written by the old convenience gate has a username and no
    // refresh token. It never authenticated anyone, so it is not a session.
    return typeof parsed.username === "string" && typeof parsed.refreshToken === "string"
      ? { username: parsed.username, refreshToken: parsed.refreshToken }
      : null;
  } catch {
    return null;
  }
}

export function readSession(): Session | null {
  const stored = readStored();
  return stored ? { username: stored.username } : null;
}

export function readRefreshToken(): string | null {
  return readStored()?.refreshToken ?? null;
}

export function writeSession(username: string, refreshToken: string): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify({ username, refreshToken }));
}

export function clearSession(): void {
  localStorage.removeItem(SESSION_KEY);
  clearIdToken();
}

export function getIdToken(): string | null {
  if (!idToken || Date.now() >= idTokenExpiresAt - EXPIRY_SLACK_MS) return null;
  return idToken;
}

export function setIdToken(token: string, expiresIn: number): void {
  idToken = token;
  idTokenExpiresAt = Date.now() + expiresIn * 1000;
}

export function clearIdToken(): void {
  idToken = null;
  idTokenExpiresAt = 0;
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd web && npx vitest run src/auth/session.test.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/auth/session.ts web/src/auth/session.test.ts
git commit -m "feat: sessao com refresh token persistido e id token em memoria"
```

---

### Task 2: `api/client.ts` autentica e renova

**Files:**
- Modify: `web/src/api/client.ts`
- Test: `web/src/api/client.test.ts`

**Interfaces:**
- Consumes: `readSession`, `readRefreshToken`, `getIdToken`, `setIdToken`, `clearIdToken`, `clearSession` (Task 1).
- Produces: `authGet<T>`, `authPost<T>`, `authPut<T>` com as mesmas assinaturas dos `api*` existentes; `ensureIdToken(baseUrl?): Promise<string>`; `SESSION_EXPIRED` (a mensagem do `ApiError` de sessão perdida). `apiGet`/`apiPost`/`apiPut` ficam inalterados.

- [ ] **Step 1: Write the failing tests**

Acrescente a `web/src/api/client.test.ts`:

```ts
import { ApiError, SESSION_EXPIRED, apiGet, apiPost, authGet, ensureIdToken } from "./client";
import { clearIdToken, readSession, setIdToken, writeSession } from "../auth/session";

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

describe("authenticated requests", () => {
  beforeEach(() => {
    vi.stubGlobal("localStorage", memoryStorage());
    clearIdToken();
    writeSession("fulano", "refresh-token");
  });

  it("sends the id token as a bearer credential", async () => {
    setIdToken("id-token", 3600);
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ username: "fulano" }));
    vi.stubGlobal("fetch", fetchMock);

    await authGet("/accounts/private");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe("Bearer id-token");
  });

  it("does not send a token on a public request", async () => {
    setIdToken("id-token", 3600);
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    await apiGet("/sensors");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers?.Authorization).toBeUndefined();
  });

  it("renews before the first call when only the refresh token survives", async () => {
    // The state right after a page reload: the id token died with the tab.
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ id_token: "novo", expires_in: 3600 }))
      .mockResolvedValueOnce(jsonResponse({ username: "fulano" }));
    vi.stubGlobal("fetch", fetchMock);

    await authGet("/accounts/private");

    expect(fetchMock.mock.calls[0][0]).toBe("/auth/refresh");
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({
      refresh_token: "refresh-token",
      username: "fulano",
    });
    expect(fetchMock.mock.calls[1][1].headers.Authorization).toBe("Bearer novo");
  });

  it("renews once and retries when a call comes back 401", async () => {
    setIdToken("velho", 3600);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({}, 401))
      .mockResolvedValueOnce(jsonResponse({ id_token: "novo", expires_in: 3600 }))
      .mockResolvedValueOnce(jsonResponse({ username: "fulano" }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(authGet("/accounts/private")).resolves.toEqual({ username: "fulano" });
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("gives up and clears the session when the refresh itself is rejected", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}, 401));
    vi.stubGlobal("fetch", fetchMock);

    await expect(authGet("/accounts/private")).rejects.toMatchObject({
      status: 401,
      message: SESSION_EXPIRED,
    });
    // 30 days elapsed: there is nothing left to renew with.
    expect(readSession()).toBeNull();
  });

  it("renews only once for concurrent callers", async () => {
    // Several views mount at the same time. Without a shared promise this
    // would fire one refresh per view.
    const fetchMock = vi.fn().mockImplementation((url: string) => {
      if (url === "/auth/refresh") {
        return Promise.resolve(jsonResponse({ id_token: "novo", expires_in: 3600 }));
      }
      return Promise.resolve(jsonResponse([]));
    });
    vi.stubGlobal("fetch", fetchMock);

    await Promise.all([
      authGet("/accounts/private"),
      authPost("/things/private", {}),
      authGet("/data/stats/private"),
    ]);

    const refreshes = fetchMock.mock.calls.filter(([url]) => url === "/auth/refresh");
    expect(refreshes).toHaveLength(1);
  });
});
```

Importe `authPost` junto de `authGet`.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd web && npx vitest run src/api/client.test.ts`
Expected: FAIL — `authGet` não é exportado.

- [ ] **Step 3: Implement**

Em `web/src/api/client.ts`, acrescente o import da sessão e reescreva `request` para aceitar um token, mantendo intactos o `ApiError`, o `buildUrl` e os três `api*`:

```ts
import {
  clearIdToken,
  clearSession,
  getIdToken,
  readRefreshToken,
  readSession,
  setIdToken,
} from "../auth/session";

/**
 * The message an ApiError carries when there is no way back to a session:
 * the refresh token is gone, rejected or 30 days old. The AuthGate matches on
 * it to send the user to the login screen instead of showing a failure.
 */
export const SESSION_EXPIRED = "Sua sessão expirou. Entre novamente.";
```

`request` ganha um parâmetro:

```ts
async function request<T>(
  method: "GET" | "POST" | "PUT",
  path: string,
  body: unknown,
  baseUrl: string,
  idToken?: string,
): Promise<T> {
  const init: RequestInit = { method };
  const headers: Record<string, string> = {};

  if (body !== undefined) {
    init.body = JSON.stringify(body);
    headers["Content-Type"] = "application/json";
  }
  if (idToken) {
    headers.Authorization = `Bearer ${idToken}`;
  }
  if (Object.keys(headers).length > 0) {
    init.headers = headers;
  }

  // ... o restante do corpo permanece exatamente como está
}
```

E ao final do arquivo:

```ts
// One renewal serves every caller waiting on it. Five views mounting together
// would otherwise fire five refreshes for the same token.
let pendingRefresh: Promise<string> | null = null;

async function renew(baseUrl: string): Promise<string> {
  const session = readSession();
  const refreshToken = readRefreshToken();

  if (!session || !refreshToken) {
    throw new ApiError(401, SESSION_EXPIRED);
  }

  let response: Response;
  try {
    response = await fetch(buildUrl("/auth/refresh", baseUrl), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken, username: session.username }),
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new ApiError(0, `Falha de conexão com a API: ${detail}`);
  }

  if (!response.ok) {
    // The refresh token is spent, revoked or past its 30 days. Nothing here
    // can recover the session, so it is cleared rather than left to fail
    // again on every screen.
    clearSession();
    throw new ApiError(401, SESSION_EXPIRED);
  }

  const { id_token, expires_in } = (await response.json()) as {
    id_token: string;
    expires_in: number;
  };
  setIdToken(id_token, expires_in);

  return id_token;
}

export function ensureIdToken(baseUrl: string = config.apiBaseUrl): Promise<string> {
  const current = getIdToken();
  if (current) return Promise.resolve(current);

  pendingRefresh ??= renew(baseUrl).finally(() => {
    pendingRefresh = null;
  });

  return pendingRefresh;
}

async function authenticated<T>(
  method: "GET" | "POST" | "PUT",
  path: string,
  body: unknown,
  baseUrl: string,
): Promise<T> {
  const token = await ensureIdToken(baseUrl);

  try {
    return await request<T>(method, path, body, baseUrl, token);
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 401) throw error;

    // The token was refused mid-session. Exactly one retry with a fresh one:
    // a second 401 means the problem is the session, not the token.
    clearIdToken();
    const renewed = await ensureIdToken(baseUrl);
    return request<T>(method, path, body, baseUrl, renewed);
  }
}

export function authGet<T>(path: string, baseUrl: string = config.apiBaseUrl): Promise<T> {
  return authenticated<T>("GET", path, undefined, baseUrl);
}

export function authPost<T>(
  path: string,
  body?: unknown,
  baseUrl: string = config.apiBaseUrl,
): Promise<T> {
  return authenticated<T>("POST", path, body, baseUrl);
}

export function authPut<T>(
  path: string,
  body?: unknown,
  baseUrl: string = config.apiBaseUrl,
): Promise<T> {
  return authenticated<T>("PUT", path, body, baseUrl);
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd web && npm test`
Expected: PASS, incluindo todos os testes que já existiam de `apiGet`/`apiPost`.

- [ ] **Step 5: Commit**

```bash
git add web/src/api/client.ts web/src/api/client.test.ts
git commit -m "feat: header de autenticacao e renovacao compartilhada no client"
```

---

### Task 3: `api/endpoints.ts`

**Files:**
- Modify: `web/src/api/endpoints.ts`
- Test: `web/src/api/endpoints.test.ts`

**Interfaces:**
- Consumes: `authGet`, `authPost`, `authPut`, `apiPost` (Task 2).
- Produces:
  - `AuthTokens` = `{ username: string; id_token: string; refresh_token: string; expires_in: number }`
  - `signUp(input: AccountInput): Promise<{ destination: string }>`
  - `confirmSignUp(input: { username: string; code: string }): Promise<AuthTokens>`
  - `resendCode(input: { username: string }): Promise<{ destination: string }>`
  - `login(input: { email: string }): Promise<{ session: string; destination: string }>`
  - `verifyOtp(input: { email: string; code: string; session: string }): Promise<AuthTokens>`
  - `AccountInput` = `{ username, name, email, phone?, city, state, country }`
  - `ProfileInput` = `{ name, phone?, city, state, country }`
  - `PrivateAccount` = `ProfileInput & { username, email }`

- [ ] **Step 1: Write the failing tests**

Acrescente a `web/src/api/endpoints.test.ts`, seguindo o padrão de stub de `fetch` já usado ali:

```ts
it("posts the registration without a password", async () => {
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ destination: "f***@e***.com" }));
  vi.stubGlobal("fetch", fetchMock);

  await signUp({
    username: "fulano",
    name: "Fulano de Tal",
    email: "fulano@example.com",
    city: "Ribeirão Preto",
    state: "SP",
    country: "BR",
  });

  const [url, init] = fetchMock.mock.calls[0];
  expect(url).toBe("/accounts");
  expect(init.method).toBe("POST");
  expect(JSON.parse(init.body)).not.toHaveProperty("password");
});

it("confirms the registration by username and code", async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    jsonResponse({ username: "fulano", id_token: "id", refresh_token: "r", expires_in: 3600 }),
  );
  vi.stubGlobal("fetch", fetchMock);

  await expect(confirmSignUp({ username: "fulano", code: "123456" })).resolves.toMatchObject({
    id_token: "id",
  });
  expect(fetchMock.mock.calls[0][0]).toBe("/accounts/confirm");
});

it("starts a sign-in with the e-mail alone", async () => {
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ session: "s", destination: "d" }));
  vi.stubGlobal("fetch", fetchMock);

  await login({ email: "fulano@example.com" });

  expect(fetchMock.mock.calls[0][0]).toBe("/auth/login");
  expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({
    email: "fulano@example.com",
  });
});

it("answers the challenge with the code and the session", async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    jsonResponse({ username: "fulano", id_token: "id", refresh_token: "r", expires_in: 3600 }),
  );
  vi.stubGlobal("fetch", fetchMock);

  await verifyOtp({ email: "fulano@example.com", code: "123456", session: "s" });

  expect(fetchMock.mock.calls[0][0]).toBe("/auth/verify");
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd web && npx vitest run src/api/endpoints.test.ts`
Expected: FAIL — `signUp` não é exportado.

- [ ] **Step 3: Implement**

Em `web/src/api/endpoints.ts`:

1. Importe `authGet, authPost, authPut` além dos `api*`.
2. Troque os tipos:

```ts
export interface AccountInput {
  username: string;
  name: string;
  email: string;
  phone?: string;
  city: string;
  state: string;
  country: string;
}

export interface ProfileInput {
  name: string;
  phone?: string;
  city: string;
  state: string;
  country: string;
}

export interface PrivateAccount extends ProfileInput {
  username: string;
  email: string;
}

export interface AuthTokens {
  username: string;
  id_token: string;
  refresh_token: string;
  expires_in: number;
}
```

3. **Remova** `PreferredUnitInput` e `savePreferredUnit`. A preferência de unidade não tem tabela no schema e passa a viver em `lib/prefs.ts` (Task 8).

4. Acrescente a seção de identidade:

```ts
// --- Identity ---------------------------------------------------------------
//
// The browser never talks to Cognito: every one of these is an endpoint of the
// API, which brokers the conversation. That is why this app carries no
// authentication library and the build injects no pool or client id.

export function signUp(input: AccountInput): Promise<{ destination: string }> {
  return apiPost<{ destination: string }>("/accounts", input);
}

// Takes the username, not the e-mail: the user has just chosen it in the form,
// and the API does not have to resolve an alias to confirm the account.
export function confirmSignUp(input: {
  username: string;
  code: string;
}): Promise<AuthTokens> {
  return apiPost<AuthTokens>("/accounts/confirm", input);
}

export function resendCode(input: { username: string }): Promise<{ destination: string }> {
  return apiPost<{ destination: string }>("/accounts/code", input);
}

// The answer looks the same whether or not the address is registered: the pool
// runs with PreventUserExistenceErrors so this cannot be used to find out who
// has an account. An unknown address only fails at verifyOtp.
export function login(input: {
  email: string;
}): Promise<{ session: string; destination: string }> {
  return apiPost<{ session: string; destination: string }>("/auth/login", input);
}

export function verifyOtp(input: {
  email: string;
  code: string;
  session: string;
}): Promise<AuthTokens> {
  return apiPost<AuthTokens>("/auth/verify", input);
}
```

5. Mova as rotas privadas para fora de `pending()` e para os verbos autenticados:

```ts
export function listPrivateThings(filters: ThingFilters = {}): Promise<Thing[]> {
  return authPost<Thing[]>("/things/private", filters);
}

export function readPrivateDetail(query: DetailQuery): Promise<Reading[]> {
  return authPost<Reading[]>("/data/detail/private", query);
}

export function readPrivateStats(): Promise<Stats> {
  return authGet<Stats>("/data/stats/private");
}

export function listSensorUnits(): Promise<SensorUnit[]> {
  return apiGet<SensorUnit[]>("/sensors/units");
}

export function readPrivateAccount(): Promise<PrivateAccount> {
  return authGet<PrivateAccount>("/accounts/private");
}

export function savePrivateAccount(input: ProfileInput): Promise<void> {
  return authPut<void>("/accounts/private", input);
}

export function linkThing(input: { uuid: string }): Promise<void> {
  return authPost<void>("/accounts/private/things", input);
}
```

6. Remova `createAccount`. **Mantenha** `PENDING_MESSAGE`, `PENDING_STATUSES` e `pending()` com seus comentários: continuam úteis para a próxima rota que a API ainda não expuser.

Se `pending()` ficar sem chamador e o lint reclamar, mantenha-a exportada — está documentada como parte do contrato do módulo.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd web && npm test`
Expected: FAIL de compilação em `SignUp.tsx` e `Account.tsx`, que ainda usam os tipos antigos. Isso é esperado e será resolvido nas Tasks 5, 6 e 9. Os testes de `endpoints.test.ts` devem passar.

- [ ] **Step 5: Commit**

```bash
git add web/src/api/endpoints.ts web/src/api/endpoints.test.ts
git commit -m "feat: endpoints de identidade e rotas privadas autenticadas"
```

---

### Task 4: `auth/AuthGate.tsx` com estado de carregamento

**Files:**
- Modify: `web/src/auth/AuthGate.tsx`
- Create: `web/src/auth/AuthGate.test.tsx`

**Interfaces:**
- Consumes: `readSession` (Task 1), `ensureIdToken`, `SESSION_EXPIRED` (Task 2).

- [ ] **Step 1: Write the failing test**

```tsx
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import AuthGate from "./AuthGate";

vi.mock("./session", () => ({ readSession: vi.fn() }));
vi.mock("../api/client", () => ({
  ensureIdToken: vi.fn(),
  SESSION_EXPIRED: "Sua sessão expirou. Entre novamente.",
}));

import { ensureIdToken } from "../api/client";
import { readSession } from "./session";

function renderGate() {
  return render(
    <MemoryRouter initialEntries={["/home/private"]}>
      <Routes>
        <Route
          path="/home/private"
          element={
            <AuthGate>
              <p>conteúdo privado</p>
            </AuthGate>
          }
        />
        <Route path="/users/login" element={<p>tela de login</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.mocked(readSession).mockReset();
  vi.mocked(ensureIdToken).mockReset();
});

describe("AuthGate", () => {
  it("sends an anonymous visitor to the login screen", () => {
    vi.mocked(readSession).mockReturnValue(null);

    renderGate();

    expect(screen.getByText("tela de login")).toBeTruthy();
  });

  it("renews before rendering, because the id token died with the tab", async () => {
    // Without this the first request of every private screen would be a 401.
    vi.mocked(readSession).mockReturnValue({ username: "fulano" });
    vi.mocked(ensureIdToken).mockResolvedValue("id-token");

    renderGate();

    await waitFor(() => expect(screen.getByText("conteúdo privado")).toBeTruthy());
    expect(ensureIdToken).toHaveBeenCalled();
  });

  it("sends the user to the login screen when the renewal fails", async () => {
    vi.mocked(readSession).mockReturnValue({ username: "fulano" });
    vi.mocked(ensureIdToken).mockRejectedValue(new Error("expired"));

    renderGate();

    await waitFor(() => expect(screen.getByText("tela de login")).toBeTruthy());
  });
});
```

Este é o primeiro teste de componente do repositório. Ele precisa de `@testing-library/react`, `@testing-library/jest-dom` e `jsdom` como **devDependencies**, e de `test: { environment: "jsdom" }` em `vite.config.ts`. Instale com versão fixada e **registre em `docs/guidelines/stacks.md` na seção de Desenvolvimento** — a restrição do projeto é sobre bibliotecas de runtime, e o `stacks.md` já lista `vitest` e `@types/*` ali:

```bash
cd web && npm install --save-exact --save-dev @testing-library/react @testing-library/dom jsdom
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd web && npx vitest run src/auth/AuthGate.test.tsx`
Expected: FAIL — o gate ainda é síncrono e nunca chama `ensureIdToken`.

- [ ] **Step 3: Implement**

```tsx
import { type ReactNode, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import Loading from "../components/Loading";
import { ensureIdToken } from "../api/client";
import { readSession } from "./session";

interface Props {
  children: ReactNode;
}

type Status = "checking" | "allowed" | "denied";

/**
 * The gate in front of every private screen.
 *
 * It cannot decide synchronously any more. The id token lives in memory, so a
 * reload leaves a valid session with no token at all -- and rendering the
 * children in that state would make the first request of every screen a 401.
 * The gate renews first and only then lets them through.
 */
export default function AuthGate({ children }: Props) {
  const [status, setStatus] = useState<Status>(() =>
    readSession() ? "checking" : "denied",
  );

  useEffect(() => {
    if (status !== "checking") return;

    let active = true;
    ensureIdToken()
      .then(() => {
        if (active) setStatus("allowed");
      })
      .catch(() => {
        // The refresh token is gone or past its 30 days. clearSession has
        // already run inside the client; there is nothing to do but ask for
        // the OTP again.
        if (active) setStatus("denied");
      });

    return () => {
      active = false;
    };
  }, [status]);

  if (status === "checking") return <Loading />;
  if (status === "denied") return <Navigate to="/users/login" replace />;

  return <>{children}</>;
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd web && npx vitest run src/auth/AuthGate.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/auth/AuthGate.tsx web/src/auth/AuthGate.test.tsx web/package.json web/package-lock.json web/vite.config.ts docs/guidelines/stacks.md
git commit -m "feat: portao privado renova a sessao antes de renderizar"
```

---

### Task 5: `views/LoginPage.tsx` em duas etapas

**Files:**
- Modify: `web/src/views/LoginPage.tsx`
- Create: `web/src/views/LoginPage.test.tsx`

**Interfaces:**
- Consumes: `login`, `verifyOtp` (Task 3); `writeSession`, `setIdToken` (Task 1).

- [ ] **Step 1: Write the failing test**

```tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/endpoints", () => ({ login: vi.fn(), verifyOtp: vi.fn() }));
vi.mock("../auth/session", () => ({ writeSession: vi.fn(), setIdToken: vi.fn() }));

import LoginPage from "./LoginPage";
import { login, verifyOtp } from "../api/endpoints";
import { setIdToken, writeSession } from "../auth/session";

beforeEach(() => {
  vi.mocked(login).mockReset();
  vi.mocked(verifyOtp).mockReset();
  vi.mocked(writeSession).mockReset();
});

describe("LoginPage", () => {
  it("asks for the code only after the e-mail was submitted", async () => {
    vi.mocked(login).mockResolvedValue({ session: "s", destination: "f***@e***.com" });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    expect(screen.queryByLabelText(/código/i)).toBeNull();

    await userEvent.type(screen.getByLabelText(/e-mail/i), "fulano@example.com");
    await userEvent.click(screen.getByRole("button", { name: /receber código/i }));

    await waitFor(() => expect(screen.getByLabelText(/código/i)).toBeTruthy());
    // The masked address tells the user which inbox to open.
    expect(screen.getByText(/f\*\*\*@e\*\*\*\.com/)).toBeTruthy();
  });

  it("stores the session that verifying the code returns", async () => {
    vi.mocked(login).mockResolvedValue({ session: "s", destination: "d" });
    vi.mocked(verifyOtp).mockResolvedValue({
      username: "fulano",
      id_token: "id",
      refresh_token: "refresh",
      expires_in: 3600,
    });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText(/e-mail/i), "fulano@example.com");
    await userEvent.click(screen.getByRole("button", { name: /receber código/i }));
    await waitFor(() => screen.getByLabelText(/código/i));

    await userEvent.type(screen.getByLabelText(/código/i), "123456");
    await userEvent.click(screen.getByRole("button", { name: /entrar/i }));

    await waitFor(() =>
      expect(writeSession).toHaveBeenCalledWith("fulano", "refresh"),
    );
    expect(setIdToken).toHaveBeenCalledWith("id", 3600);
  });

  it("shows the message when the code is refused", async () => {
    vi.mocked(login).mockResolvedValue({ session: "s", destination: "d" });
    vi.mocked(verifyOtp).mockRejectedValue(
      Object.assign(new Error("código inválido"), { name: "ApiError", status: 400 }),
    );

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText(/e-mail/i), "fulano@example.com");
    await userEvent.click(screen.getByRole("button", { name: /receber código/i }));
    await waitFor(() => screen.getByLabelText(/código/i));

    await userEvent.type(screen.getByLabelText(/código/i), "000000");
    await userEvent.click(screen.getByRole("button", { name: /entrar/i }));

    await waitFor(() => expect(screen.getByText(/código inválido/i)).toBeTruthy());
  });
});
```

Instale `@testing-library/user-event` com `--save-exact --save-dev` e registre no `stacks.md`.

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd web && npx vitest run src/views/LoginPage.test.tsx`
Expected: FAIL — a tela ainda tem só o botão "Entrar" do portão falso.

- [ ] **Step 3: Implement**

Reescreva `web/src/views/LoginPage.tsx` com estado `"email" | "code"`, usando `ErrorBanner` para o erro e o mesmo markup (`section.home`, `section.signUp`, `font-36px`, `font-17px`, `font-16px`) que a tela já usa. Requisitos que os testes fixam:

- etapa 1: `<label htmlFor="email">E-mail</label>` e botão "Receber código";
- etapa 2: `<label htmlFor="code">Código</label>`, o `destination` visível no texto, botão "Entrar" e um botão "Reenviar código" que volta à etapa 1;
- sucesso: `writeSession(username, refresh_token)`, `setIdToken(id_token, expires_in)`, `navigate("/home/private")`;
- erro: mensagem do `ApiError`, ou `"Falha inesperada ao entrar"`.

Inclua na etapa 1 o aviso, em `font-17px`:

> Enviaremos um código de acesso para o seu e-mail. Não há senha. A sessão dura 30 dias.

E o comentário de módulo:

```tsx
/**
 * Sign-in in two steps: an address, then the code that arrives in it.
 *
 * The first step always advances, even for an address with no account: the API
 * answers the same either way, on purpose, so that this screen cannot be used
 * to find out who is registered. An unknown address only fails at the code.
 */
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd web && npx vitest run src/views/LoginPage.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/views/LoginPage.tsx web/src/views/LoginPage.test.tsx web/package.json web/package-lock.json docs/guidelines/stacks.md
git commit -m "feat: login em duas etapas com codigo por e-mail"
```

---

### Task 6: `views/SignUp.tsx` em duas etapas

**Files:**
- Modify: `web/src/views/SignUp.tsx`
- Create: `web/src/views/SignUp.test.tsx`

**Interfaces:**
- Consumes: `signUp`, `confirmSignUp`, `resendCode` (Task 3); `writeSession`, `setIdToken` (Task 1).

- [ ] **Step 1: Write the failing test**

```tsx
vi.mock("../api/endpoints", () => ({
  signUp: vi.fn(),
  confirmSignUp: vi.fn(),
  resendCode: vi.fn(),
}));
vi.mock("../auth/session", () => ({ writeSession: vi.fn(), setIdToken: vi.fn() }));

// ... imports as in LoginPage.test.tsx

const FORM = {
  username: "fulano",
  name: "Fulano de Tal",
  email: "fulano@example.com",
  city: "Ribeirão Preto",
};

async function fillTheForm() {
  await userEvent.type(screen.getByLabelText(/^usuário/i), FORM.username);
  await userEvent.type(screen.getByLabelText(/^nome/i), FORM.name);
  await userEvent.type(screen.getByLabelText(/e-mail/i), FORM.email);
  await userEvent.type(screen.getByLabelText(/cidade/i), FORM.city);
}

describe("SignUp", () => {
  it("has no password field, because the platform has no passwords", () => {
    render(<MemoryRouter><SignUp /></MemoryRouter>);

    expect(screen.queryByLabelText(/senha/i)).toBeNull();
  });

  it("limits the username to what the column holds", () => {
    render(<MemoryRouter><SignUp /></MemoryRouter>);

    // accounts.username is VARCHAR(20).
    expect(screen.getByLabelText(/^usuário/i).getAttribute("maxLength")).toBe("20");
  });

  it("signs the user in as soon as the code is confirmed", async () => {
    vi.mocked(signUp).mockResolvedValue({ destination: "f***@e***.com" });
    vi.mocked(confirmSignUp).mockResolvedValue({
      username: "fulano",
      id_token: "id",
      refresh_token: "refresh",
      expires_in: 3600,
    });

    render(<MemoryRouter><SignUp /></MemoryRouter>);

    await fillTheForm();
    await userEvent.click(screen.getByRole("button", { name: /cadastrar/i }));
    await waitFor(() => screen.getByLabelText(/código/i));

    await userEvent.type(screen.getByLabelText(/código/i), "123456");
    await userEvent.click(screen.getByRole("button", { name: /confirmar/i }));

    // Confirming with the OTP already proves the e-mail, so Cognito hands back
    // a session: the user never types a second code.
    await waitFor(() => expect(writeSession).toHaveBeenCalledWith("fulano", "refresh"));
  });

  it("reports a duplicated e-mail without losing what was typed", async () => {
    vi.mocked(signUp).mockRejectedValue(
      Object.assign(new Error("este e-mail já tem conta"), { name: "ApiError", status: 409 }),
    );

    render(<MemoryRouter><SignUp /></MemoryRouter>);

    await fillTheForm();
    await userEvent.click(screen.getByRole("button", { name: /cadastrar/i }));

    await waitFor(() => expect(screen.getByText(/já tem conta/i)).toBeTruthy());
    expect((screen.getByLabelText(/^nome/i) as HTMLInputElement).value).toBe(FORM.name);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd web && npx vitest run src/views/SignUp.test.tsx`
Expected: FAIL — o campo de senha ainda existe.

- [ ] **Step 3: Implement**

Reescreva `web/src/views/SignUp.tsx`:

- `EMPTY` vira `{ username: "", name: "", email: "", phone: "", city: "", state: BRAZIL_STATES[0].value, country: COUNTRIES[0].value }`. **Sem `password`, sem `first_name`, sem `last_name`.**
- Campos: Usuário (`maxLength={20}`, `required`), Nome (`required`), E-mail (`type="email"`, `required`), Telefone (**sem** `required`), Cidade (`required`), Estado (`select`), País (`select`).
- Estado `"form" | "code"`; `submit` chama `signUp(form)` e guarda `destination`.
- Etapa do código: `<label htmlFor="code">Código</label>`, botão "Confirmar", botão "Reenviar código" chamando `resendCode({ username: form.username })`.
- Sucesso: `writeSession(...)`, `setIdToken(...)`, `navigate("/home/private")`.
- Um `502` (`caught.status === 502`) mostra a mensagem da API e um link para `/users/login` — a conta existe, e o primeiro login refaz o provisionamento.
- O estado do formulário **não é limpo** em caso de erro.

Comentário de módulo:

```tsx
/**
 * Registration in two steps, with no password anywhere.
 *
 * The first step only creates the Cognito user: name, phone and address wait
 * as attributes on it, and nothing reaches the ERP until the address is
 * proven. The second step confirms the code -- which both verifies the e-mail
 * and signs the user in, so they land logged in rather than at the login
 * screen.
 */
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd web && npm test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/views/SignUp.tsx web/src/views/SignUp.test.tsx
git commit -m "feat: cadastro sem senha com confirmacao por codigo"
```

---

### Task 7: `components/Header.tsx`

**Files:**
- Modify: `web/src/components/Header.tsx`

`clearSession()` já limpa o ID token desde a Task 1, então o "Sair" está correto por construção. Esta task só confirma isso e ajusta o comentário.

- [ ] **Step 1: Read and verify**

Run: `cd web && cat src/components/Header.tsx`

Confirme que o `onClick` de "Sair" chama `clearSession()` e depois navega/recarrega, e que nada mais lê o token diretamente:

Run: `grep -rn "getIdToken\|setIdToken" web/src --include=*.tsx`
Expected: nenhum resultado fora de `auth/` e `api/`.

- [ ] **Step 2: Update the comment**

O comentário atual explica que `clearSession` só mexe no `localStorage`, que React não observa. Ele agora está incompleto: acrescente que a limpeza também descarta o token em memória.

```tsx
  // clearSession only touches localStorage and a module-level variable, and
  // React observes neither. The reload is what makes every screen see that the
  // session is gone.
```

- [ ] **Step 3: Run the suite**

Run: `cd web && npm test`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add web/src/components/Header.tsx
git commit -m "docs: comentario do logout cobre o token em memoria"
```

---

# Fase 3 — Conta

A fase 2 não tem trabalho neste repositório: é o deploy do authorizer no lado da API. **Publique esta fase somente depois disso.**

---

### Task 8: unidade preferida em `lib/prefs.ts`

**Files:**
- Modify: `web/src/lib/prefs.ts`
- Test: `web/src/lib/prefs.test.ts`

**Interfaces:**
- Produces: `readPreferredUnit(sensorId: number): number | null`, `writePreferredUnit(sensorId: number, unitId: number): void`.

- [ ] **Step 1: Write the failing tests**

```ts
describe("preferred unit", () => {
  it("has none until one is chosen", () => {
    expect(readPreferredUnit(3)).toBeNull();
  });

  it("returns the unit that was chosen for that sensor", () => {
    writePreferredUnit(3, 7);
    writePreferredUnit(4, 9);

    expect(readPreferredUnit(3)).toBe(7);
    expect(readPreferredUnit(4)).toBe(9);
  });

  it("treats a corrupted entry as no preference", () => {
    localStorage.setItem("unit3", "nem numero");
    expect(readPreferredUnit(3)).toBeNull();
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd web && npx vitest run src/lib/prefs.test.ts`
Expected: FAIL — `readPreferredUnit` não existe.

- [ ] **Step 3: Implement**

```ts
const preferredUnitKey = (sensorId: number) => `unit${sensorId}`;

/**
 * Which unit this browser shows for a sensor.
 *
 * It is a browser preference, not an account setting: the schema has no table
 * linking an account to a unit -- `sensorsunits` is a catalogue with a global
 * `isdefault` -- and adding one would mean changing the Core's database. So it
 * sits beside the period and the chart type, which are stored the same way.
 */
export function readPreferredUnit(sensorId: number): number | null {
  const stored = localStorage.getItem(preferredUnitKey(sensorId));
  if (stored === null) return null;

  const parsed = Number(stored);
  return Number.isInteger(parsed) ? parsed : null;
}

export function writePreferredUnit(sensorId: number, unitId: number): void {
  localStorage.setItem(preferredUnitKey(sensorId), String(unitId));
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd web && npx vitest run src/lib/prefs.test.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/lib/prefs.ts web/src/lib/prefs.test.ts
git commit -m "feat: unidade preferida por sensor no armazenamento local"
```

---

### Task 9: `views/Account.tsx` nas três abas

**Files:**
- Modify: `web/src/views/Account.tsx`
- Create: `web/src/views/Account.test.tsx`

**Interfaces:**
- Consumes: `readPrivateAccount`, `savePrivateAccount`, `linkThing`, `listSensorUnits` (Task 3); `readPreferredUnit`, `writePreferredUnit` (Task 8).

- [ ] **Step 1: Write the failing tests**

```tsx
vi.mock("../api/endpoints", () => ({
  readPrivateAccount: vi.fn(),
  savePrivateAccount: vi.fn(),
  linkThing: vi.fn(),
  listSensorUnits: vi.fn(),
  listPrivateThings: vi.fn(),
}));

const ACCOUNT = {
  username: "fulano",
  name: "Fulano de Tal",
  email: "fulano@example.com",
  phone: "16999991234",
  city: "Ribeirão Preto",
  state: "SP",
  country: "BR",
};

function renderProfile() {
  return render(
    <MemoryRouter initialEntries={["/users/account/fulano/profile"]}>
      <Routes>
        <Route path="/users/account/:username/:tab" element={<Account />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("the profile tab", () => {
  it("shows one name field, because the ERP stores one name", async () => {
    vi.mocked(readPrivateAccount).mockResolvedValue(ACCOUNT);

    renderProfile();

    await waitFor(() =>
      expect((screen.getByLabelText(/^nome/i) as HTMLInputElement).value).toBe(
        "Fulano de Tal",
      ),
    );
    expect(screen.queryByLabelText(/sobrenome/i)).toBeNull();
  });

  it("does not let the e-mail be edited", async () => {
    vi.mocked(readPrivateAccount).mockResolvedValue(ACCOUNT);

    renderProfile();

    // It is what authenticates: changing it here would not change the login.
    await waitFor(() =>
      expect((screen.getByLabelText(/e-mail/i) as HTMLInputElement).readOnly).toBe(true),
    );
  });

  it("saves without the fields it does not own", async () => {
    vi.mocked(readPrivateAccount).mockResolvedValue(ACCOUNT);
    vi.mocked(savePrivateAccount).mockResolvedValue(undefined);

    renderProfile();
    await waitFor(() => screen.getByLabelText(/^nome/i));
    await userEvent.click(screen.getByRole("button", { name: /salvar/i }));

    const sent = vi.mocked(savePrivateAccount).mock.calls[0][0];
    expect(sent).not.toHaveProperty("username");
    expect(sent).not.toHaveProperty("email");
  });
});
```

Acrescente um teste da aba de centrais verificando que um `409` de `linkThing` vira a mensagem "esta central já pertence a uma conta".

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd web && npx vitest run src/views/Account.test.tsx`
Expected: FAIL — a aba ainda usa `first_name`/`last_name`.

- [ ] **Step 3: Implement**

Em `web/src/views/Account.tsx`:

- **`ProfileTab`**: o `useEffect` passa a montar `{ name, phone, city, state, country }` a partir de `account.data`. O campo E-mail vira `readOnly` e não entra no `ProfileInput` enviado. Trate `409` (conta não provisionada) com uma mensagem própria: "Conta ainda não registrada. Entre novamente para concluir o cadastro."
- **`ThingsTab`**: `linkThing` sai de `pending()`. Mapeie `404` → "Central não encontrada." e `409` → "Esta central já pertence a uma conta."
- **`SensorsTab`**: remova o import e o uso de `savePreferredUnit`; a escolha de unidade passa a chamar `writePreferredUnit(sensorId, unitId)` e o valor inicial vem de `readPreferredUnit(sensorId)`, exatamente como `readChartType`/`writeChartType` já fazem ao lado. Remova o array `PRECISIONS` e o comentário sobre `MAX_PRECISION` se a precisão deixar de ser editável — ela vem do catálogo em `listSensorUnits()`.

Acrescente ao topo da aba de sensores:

```tsx
// The unit is a browser preference, not an account setting: there is no table
// in the schema linking an account to a unit. See lib/prefs.ts.
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd web && npm test && npm run build`
Expected: PASS, e o `tsc -b` do build sem erro — é aqui que os tipos trocados na Task 3 terminam de fechar.

- [ ] **Step 5: Commit**

```bash
git add web/src/views/Account.tsx web/src/views/Account.test.tsx
git commit -m "feat: telas de perfil, centrais e sensores contra a API real"
```

---

### Task 10: Guidelines atualizadas

**Files:**
- Modify: `docs/guidelines/architecture.md`
- Modify: `docs/guidelines/stacks.md`

- [ ] **Step 1: Update `architecture.md`**

- No diagrama, acrescente o Cognito **atrás da API**, não ao lado do navegador:

```
Navegador → CloudFront → S3 (bundle estático)
    │
    └── HTTPS → API Gateway → Lambdas → PostgreSQL (Neon)
                     │            └────→ Cognito (identidade)
                     └── authorizer valida o ID token
```

- Em "Módulos Principais", reescreva a linha de `auth/`:

```
  auth/         session.ts    → refresh token no localStorage, ID token em memória
                AuthGate.tsx  → renova antes de renderizar; redireciona quem não tem sessão
```

- Em "Fluxo de Dados", acrescente um item explicando que `client.ts` injeta o ID token nas rotas privadas e renova uma vez no 401, com renovação compartilhada entre chamadas concorrentes.

- [ ] **Step 2: Update `stacks.md`**

- Em "Serviços de Nuvem Utilizados", acrescente:

```
- **Cognito** — identidade dos usuários. Alcançado **pela API**, nunca pelo
  navegador: o SPA não conhece pool id nem client id.
```

- Em "Bibliotecas Permitidas → Desenvolvimento", acrescente as instaladas nas Tasks 4 e 5 (`@testing-library/react`, `@testing-library/dom`, `@testing-library/user-event`, `jsdom`) com as versões fixadas.

- Na seção do SPA, acrescente:

```
Nenhuma biblioteca de autenticação. Como a API intermedia o Cognito, o SPA não
precisa de `oidc-client-ts` nem `amazon-cognito-identity-js`.
```

- [ ] **Step 3: Verify**

Run: `grep -rn "portão de conveniência\|convenience gate" docs/ web/src`
Expected: nenhum resultado — a expressão descrevia o que foi removido.

- [ ] **Step 4: Commit**

```bash
git add docs/guidelines
git commit -m "docs: guidelines refletem a autenticacao real"
```

---

## Deploy

**Publicação única, ao fim de tudo.** As fases são marcos de desenvolvimento,
não publicações separadas.

A API vai **sempre antes** deste repositório, por uma razão que já existe hoje e
não tem a ver com autenticação: o `vite.config.ts` chama
`scripts/resolve_api_url.py` **durante o build**, que lê o output
`SensoriandoApiUrl` do CloudFormation. Sem a API no ar, o bundle sai com URL
vazia e o app renderiza "Aplicação sem configuração".

```bash
cd SENSORIANDO_API        && make deploy
cd sensoriando_webservice && make deploy
```

Entre os dois comandos o bundle antigo leva 401 nas rotas privadas — alguns
minutos, sem usuário real afetado, e o `distribution_paths=["/*"]` do
`web_stack.py` invalida o CloudFront assim que o bundle novo sobe.

### Antes de escrever a Fase 3

A Fase 1 da API tem uma **verificação obrigatória** contra a AWS de verdade
(cadastro e login ponta a ponta), descrita no plano dela. Duas das três coisas
que ela valida decidem o formato de módulos deste repositório:

- se `POST /accounts/confirm` **não** devolver tokens, o `SignUp.tsx` da Task 6
  precisa mandar o usuário ao login em vez de entrar direto;
- se o `SECRET_HASH` sobre o e-mail **não** for aceito, `login()` e
  `verifyOtp()` na Task 3 mudam de assinatura, e a tela da Task 5 junto.

Confirme o resultado dessa verificação antes de começar as Tasks 3, 5 e 6.
