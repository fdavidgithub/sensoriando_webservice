/// <reference types="vitest/config" />
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// resolve_api_url.py needs boto3, which lives in infra/.venv (see
// infra/README.md), not in whatever bare `python3` happens to be on PATH.
// Falling back to a plain interpreter is still worth trying -- some setups
// install boto3 globally -- but the venv is the one guaranteed to have it.
function pythonInterpreter(): string {
  const venvRoot = fileURLToPath(new URL("../infra/.venv", import.meta.url));
  const candidates = [
    `${venvRoot}/bin/python`, // posix
    `${venvRoot}/Scripts/python.exe`, // windows
  ];

  const venvPython = candidates.find((candidate) => existsSync(candidate));
  return venvPython ?? "python3";
}

// The API Gateway id is assigned by AWS at deploy time, so the base URL is not
// committed. It is discovered from the deployed account at build time. A
// failure yields an empty string, which the app reports as "not configured"
// rather than silently producing a bundle that calls nothing.
function resolveApiBaseUrl(): string {
  try {
    const script = fileURLToPath(new URL("../scripts/resolve_api_url.py", import.meta.url));
    return execFileSync(pythonInterpreter(), [script], { encoding: "utf8" }).trim();
  } catch {
    return "";
  }
}

// Every path prefix the API owns. Listed explicitly so that a future prefix is
// a deliberate addition here rather than a silent dev/prod difference.
const API_PREFIXES = ["/sensors", "/accounts", "/things", "/data"];

export default defineConfig(({ command }) => {
  // Only "serve" (npm run dev) and "build" need the API URL. Resolving it
  // during `vitest` would make the unit suite depend on AWS credentials and
  // network access for no benefit -- the tests never read this value.
  const apiTarget = command === "serve" || command === "build" ? resolveApiBaseUrl() : "";

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
      environment: "jsdom",
      // Exposes the vitest hooks (afterEach, ...) as globals, which the
      // @testing-library/react auto-cleanup relies on to unmount between tests.
      globals: true,
      include: ["src/**/*.test.{ts,tsx}"],
    },
  };
});
