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
