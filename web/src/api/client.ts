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
