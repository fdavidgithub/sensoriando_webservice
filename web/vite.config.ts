/// <reference types="vitest/config" />
import { execFileSync } from "node:child_process";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The API Gateway id is assigned by AWS at deploy time, so the base URL is not
// committed. It is discovered from the deployed account at build time. A
// failure yields an empty string, which the app reports as "not configured"
// rather than silently producing a bundle that calls nothing.
function resolveApiBaseUrl(): string {
  try {
    const script = new URL("../scripts/resolve_api_url.py", import.meta.url).pathname;
    return execFileSync("python3", [script], { encoding: "utf8" }).trim();
  } catch {
    return "";
  }
}

// Every path prefix the API owns. Listed explicitly so that a future prefix is
// a deliberate addition here rather than a silent dev/prod difference.
const API_PREFIXES = ["/sensors", "/accounts", "/things", "/data"];

export default defineConfig(() => {
  const apiTarget = resolveApiBaseUrl();

  // Dev-only proxy: the browser talks to the Vite dev server (same origin) and
  // Vite forwards API calls, so CORS does not apply locally.
  const proxy = apiTarget
    ? Object.fromEntries(
        API_PREFIXES.map((prefix) => [
          prefix,
          { target: apiTarget, changeOrigin: true, secure: true },
        ]),
      )
    : undefined;

  return {
    plugins: [react()],
    define: {
      "import.meta.env.VITE_API_BASE_URL": JSON.stringify(apiTarget),
    },
    server: { proxy },
    test: {
      environment: "node",
      include: ["src/**/*.test.ts"],
    },
  };
});
