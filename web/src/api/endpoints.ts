import { ApiError, apiGet, apiPost, apiPut } from "./client";
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
async function pending<T>(call: () => Promise<T>): Promise<T> {
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
