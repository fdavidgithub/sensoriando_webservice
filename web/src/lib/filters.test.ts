import { describe, expect, it } from "vitest";

import { filtersFromSearch, searchFromFilters } from "./filters";

describe("filtersFromSearch", () => {
  it("reads the keys the API accepts", () => {
    expect(filtersFromSearch("?sensor=temperatura&sensor_tag=externo")).toEqual({
      sensor: "temperatura",
      sensor_tag: "externo",
    });
  });

  it("ignores keys the API does not accept", () => {
    expect(filtersFromSearch("?sensor=temperatura&utm_source=x")).toEqual({
      sensor: "temperatura",
    });
  });

  it("drops empty values so they are never sent as filters", () => {
    expect(filtersFromSearch("?sensor=&city=Lavras")).toEqual({ city: "Lavras" });
  });

  it("returns nothing for an empty search", () => {
    expect(filtersFromSearch("")).toEqual({});
    expect(filtersFromSearch("?")).toEqual({});
  });

  it("keeps the sentinels the API uses for things without an account", () => {
    expect(filtersFromSearch("?city=n%C3%A3o%20registrado&country=NR")).toEqual({
      city: "não registrado",
      country: "NR",
    });
  });
});

describe("searchFromFilters", () => {
  it("builds a query string", () => {
    expect(searchFromFilters({ sensor: "temperatura" })).toBe("?sensor=temperatura");
  });

  it("returns an empty string when there is no filter", () => {
    expect(searchFromFilters({})).toBe("");
  });

  it("omits empty values", () => {
    expect(searchFromFilters({ sensor: "", city: "Lavras" })).toBe("?city=Lavras");
  });

  it("round-trips through filtersFromSearch", () => {
    const filters = { city: "não registrado", country: "NR", sensor: "temperatura" };
    expect(filtersFromSearch(searchFromFilters(filters))).toEqual(filters);
  });
});
