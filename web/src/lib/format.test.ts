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
