export interface Session {
  username: string;
}

export function readSession(): Session | null {
  return null;
}

export function clearSession(): void {}
