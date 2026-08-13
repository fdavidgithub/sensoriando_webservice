/**
 * A convenience gate, not a security boundary.
 *
 * The app is a static bundle: there is no server here to verify anything, and
 * any password shipped in it would be readable by anyone with the URL. So there
 * is no password at all — the gate only keeps the private screens out of the
 * way until real authentication (Cognito) lands.
 *
 * It also grants no access to data: the API's /private endpoints serve the one
 * account named by PRIVATE_ACCOUNT_USERNAME regardless of who signed in here.
 */

const SESSION_KEY = "sensoriando.session";

export interface Session {
  username: string;
}

export function readSession(): Session | null {
  const stored = localStorage.getItem(SESSION_KEY);
  if (!stored) return null;

  try {
    const parsed = JSON.parse(stored) as Partial<Session>;
    return typeof parsed.username === "string" ? { username: parsed.username } : null;
  } catch {
    return null;
  }
}

export function writeSession(username: string): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify({ username }));
}

export function clearSession(): void {
  localStorage.removeItem(SESSION_KEY);
}
