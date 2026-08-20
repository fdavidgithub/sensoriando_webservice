/**
 * The signed-in user, and the two tokens that keep them signed in.
 *
 * The ID token -- the one that opens every private route -- lives only in this
 * module's memory and dies with the tab. Persisting it would leave the
 * credential that grants immediate access sitting in storage for its whole
 * hour; keeping it here narrows that window to the page's lifetime.
 *
 * The refresh token does persist, because a session that ended on every reload
 * would be unusable. It buys nothing on its own: it has to be exchanged at
 * POST /auth/refresh before anything can be read.
 *
 * Cognito issues it for 30 days and does not rotate it, so the window does not
 * slide -- 30 days after signing in, the user does the OTP again.
 */

const SESSION_KEY = "sensoriando.session";

// A token that expires while the request is still in flight costs a round trip
// and a retry. Renewing a minute early costs nothing.
const EXPIRY_SLACK_MS = 60_000;

export interface Session {
  username: string;
}

interface StoredSession {
  username: string;
  refreshToken: string;
}

let idToken: string | null = null;
let idTokenExpiresAt = 0;

function readStored(): StoredSession | null {
  const stored = localStorage.getItem(SESSION_KEY);
  if (!stored) return null;

  try {
    const parsed = JSON.parse(stored) as Partial<StoredSession>;
    // A session written by the old convenience gate has a username and no
    // refresh token. It never authenticated anyone, so it is not a session.
    return typeof parsed.username === "string" && typeof parsed.refreshToken === "string"
      ? { username: parsed.username, refreshToken: parsed.refreshToken }
      : null;
  } catch {
    return null;
  }
}

export function readSession(): Session | null {
  const stored = readStored();
  return stored ? { username: stored.username } : null;
}

export function readRefreshToken(): string | null {
  return readStored()?.refreshToken ?? null;
}

export function writeSession(username: string, refreshToken: string): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify({ username, refreshToken }));
}

export function clearSession(): void {
  localStorage.removeItem(SESSION_KEY);
  clearIdToken();
}

export function getIdToken(): string | null {
  if (!idToken || Date.now() >= idTokenExpiresAt - EXPIRY_SLACK_MS) return null;
  return idToken;
}

export function setIdToken(token: string, expiresIn: number): void {
  idToken = token;
  idTokenExpiresAt = Date.now() + expiresIn * 1000;
}

export function clearIdToken(): void {
  idToken = null;
  idTokenExpiresAt = 0;
}