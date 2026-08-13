/**
 * The filter keys POST /things and POST /things/private accept. Anything else
 * in the query string is not a filter and is dropped, so that an unrelated
 * parameter (an analytics tag, say) never reaches the API as one.
 */
export const FILTER_KEYS = [
  "thing",
  "city",
  "state",
  "country",
  "sensor",
  "thing_tag",
  "sensor_tag",
] as const;

export type FilterKey = (typeof FILTER_KEYS)[number];

export type Filters = Partial<Record<FilterKey, string>>;

function isFilterKey(key: string): key is FilterKey {
  return (FILTER_KEYS as readonly string[]).includes(key);
}

export function filtersFromSearch(search: string): Filters {
  const parameters = new URLSearchParams(search);
  const filters: Filters = {};

  for (const key of FILTER_KEYS) {
    const value = parameters.get(key);
    if (value) {
      filters[key] = value;
    }
  }

  return filters;
}

export function searchFromFilters(filters: Filters): string {
  const parameters = new URLSearchParams();

  for (const [key, value] of Object.entries(filters)) {
    if (value && isFilterKey(key)) {
      parameters.set(key, value);
    }
  }

  const search = parameters.toString();
  return search ? `?${search}` : "";
}
