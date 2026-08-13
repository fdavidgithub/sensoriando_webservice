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
    expect(countryName("XY")).toBe("XY");
  });

  it("returns an empty string for a missing value", () => {
    expect(countryName(null)).toBe("");
    expect(countryName(undefined)).toBe("");
    expect(countryName("")).toBe("");
  });
});
