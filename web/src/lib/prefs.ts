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
