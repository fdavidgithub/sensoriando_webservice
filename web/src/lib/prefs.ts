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
