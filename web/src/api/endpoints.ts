import { ApiError, apiGet, apiPost, authGet, authPost, authPut } from "./client";
import type { Reading, Sensor, SensorTag, SensorUnit, Stats, Thing } from "./types";

/**
 * Shown when a route this app already calls does not exist in the API yet.
 * Distinct from a generic failure on purpose: a known gap must not read as a
 * bug. See the "Endpoints previstos" table in the design document.
 */
export const PENDING_MESSAGE = "Recurso ainda não disponível na API";

// API Gateway answers a route with no method configured with 403, not 404 --
// verified against the deployed API. A plain REST resource with nothing wired
// to it would 404, but these paths have no resource at all yet, so the
// gateway's default "Missing Authentication Token" response (403) is what a
// pending route actually returns.
const PENDING_STATUSES = new Set([403, 404]);

/**
 * Marks a call whose route is not deployed yet. The expected failure status
 * from such a route is not an error worth a stack trace; anything else passes
 * through untouched so real failures stay visible.
 */
export async function pending<T>(call: () => Promise<T>): Promise<T> {
  try {
    return await call();
  } catch (error) {
    if (error instanceof ApiError && PENDING_STATUSES.has(error.status)) {
      throw new ApiError(error.status, PENDING_MESSAGE);
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
  return authPost<Thing[]>("/things/private", filters);
}

export function readPublicDetail(query: DetailQuery): Promise<Reading[]> {
  return apiPost<Reading[]>("/data/detail", query);
}

export function readPrivateDetail(query: DetailQuery): Promise<Reading[]> {
  return authPost<Reading[]>("/data/detail/private", query);
}

export function readPrivateStats(): Promise<Stats> {
  return authGet<Stats>("/data/stats/private");
}

// --- Account and catalogue routes -------------------------------------------

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
