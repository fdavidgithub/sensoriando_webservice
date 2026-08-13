// The build injects the API base URL discovered from the deployed account.
// An empty string means the lookup failed: the app then shows a configuration
// notice instead of firing requests at a relative path that cannot answer them.
const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL as string | undefined;

export const config = {
  // In dev, a relative base sends requests through the Vite proxy (see
  // vite.config.ts), keeping the browser on a single origin. Production builds
  // call the API directly; CORS is handled server-side.
  apiBaseUrl: import.meta.env.DEV ? "" : (rawApiBaseUrl ?? ""),
  apiConfigured: import.meta.env.DEV || Boolean(rawApiBaseUrl),
  defaultPeriod: "second",
  defaultChartType: "line",
} as const;
