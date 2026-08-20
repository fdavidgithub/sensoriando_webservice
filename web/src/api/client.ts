import { config } from "../config";
import {
  clearIdToken,
  clearSession,
  getIdToken,
  notifySessionExpired,
  readRefreshToken,
  readSession,
  setIdToken,
} from "../auth/session";

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

/**
 * The message an ApiError carries when there is no way back to a session:
 * the refresh token is gone, rejected or 30 days old. The AuthGate matches on
 * it to send the user to the login screen instead of showing a failure.
 */
export const SESSION_EXPIRED = "Sua sessão expirou. Entre novamente.";

function buildUrl(path: string, baseUrl: string): string {
  if (!baseUrl) return path;
  return `${baseUrl.replace(/\/$/, "")}${path}`;
}

// The server explains its refusal in the error body ("código inválido", a 502
// provisioning message, ...). That text is what the user should see, so it is
// pulled out when present; a body that is empty or not JSON falls back to the
// status line.
async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = JSON.parse(await response.text());
    return body?.message ?? body?.detail ?? `A API respondeu ${response.status}`;
  } catch {
    return `A API respondeu ${response.status}`;
  }
}

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

  let response: Response;
  try {
    response = await fetch(buildUrl(path, baseUrl), init);
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new ApiError(0, `Falha de conexão com a API: ${detail}`);
  }

  if (!response.ok) {
    const detail = await readErrorMessage(response);
    throw new ApiError(response.status, detail);
  }

  // A 204, or any other empty body, is a valid success -- several write
  // endpoints are typed Promise<void> and never return a payload. response
  // .json() would throw SyntaxError on "" and turn a save that worked into a
  // reported failure, so an empty body short-circuits before parsing.
  const text = await response.text();
  if (!text) {
    return undefined as T;
  }

  try {
    return JSON.parse(text) as T;
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
    // again on every screen. notifySessionExpired() is what lets an AuthGate
    // that already rendered its children -- this call can run well after the
    // gate approved the screen -- learn to send the user back to login.
    clearSession();
    notifySessionExpired();
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
    try {
      return await request<T>(method, path, body, baseUrl, renewed);
    } catch (retryError) {
      if (retryError instanceof ApiError && retryError.status === 401) {
        // The fresh token was refused too: the session is gone. Clear it and
        // notify so the AuthGate already showing this screen sends the user
        // to login instead of leaving them on a dead screen.
        clearSession();
        notifySessionExpired();
        throw new ApiError(401, SESSION_EXPIRED);
      }
      throw retryError;
    }
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
