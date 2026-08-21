import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import AuthGate from "./AuthGate";

vi.mock("./session", () => ({ readSession: vi.fn(), onSessionExpired: vi.fn() }));
vi.mock("../api/client", () => ({
  ensureIdToken: vi.fn(),
  SESSION_EXPIRED: "Sua sessão expirou. Entre novamente.",
}));

import { ensureIdToken } from "../api/client";
import { onSessionExpired, readSession } from "./session";

// Reads the state a <Navigate> handed the login route, so a test can tell a
// plain denial (no message) apart from one that followed an expiry.
function LoginPlaceholder() {
  const location = useLocation();
  const message = (location.state as { message?: string } | null)?.message;
  return <p>tela de login{message ? `: ${message}` : ""}</p>;
}

function renderGate() {
  return render(
    <MemoryRouter initialEntries={["/home/private"]}>
      <Routes>
        <Route
          path="/home/private"
          element={
            <AuthGate>
              <p>conteúdo privado</p>
            </AuthGate>
          }
        />
        <Route path="/users/login" element={<LoginPlaceholder />} />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.mocked(readSession).mockReset();
  vi.mocked(ensureIdToken).mockReset();
  vi.mocked(onSessionExpired).mockReset().mockReturnValue(() => {});
});

describe("AuthGate", () => {
  it("sends an anonymous visitor to the login screen", () => {
    vi.mocked(readSession).mockReturnValue(null);

    renderGate();

    expect(screen.getByText("tela de login")).toBeTruthy();
  });

  it("renews before rendering, because the id token died with the tab", async () => {
    // Without this the first request of every private screen would be a 401.
    vi.mocked(readSession).mockReturnValue({ username: "fulano" });
    vi.mocked(ensureIdToken).mockResolvedValue("id-token");

    renderGate();

    await waitFor(() => expect(screen.getByText("conteúdo privado")).toBeTruthy());
    expect(ensureIdToken).toHaveBeenCalled();
  });

  it("sends the user to the login screen when the renewal fails", async () => {
    vi.mocked(readSession).mockReturnValue({ username: "fulano" });
    vi.mocked(ensureIdToken).mockRejectedValue(new Error("expired"));

    renderGate();

    await waitFor(() => expect(screen.getByText("tela de login")).toBeTruthy());
  });

  it("sends an already-allowed screen to login when the session expires mid-use", async () => {
    // A private screen's own request can fail long after AuthGate let it
    // through -- the refresh token can expire, or the API can reject it. This
    // is client.ts's client-side signal for that, since nothing else tells an
    // already-rendered AuthGate.
    vi.mocked(readSession).mockReturnValue({ username: "fulano" });
    vi.mocked(ensureIdToken).mockResolvedValue("id-token");
    let expiredListener: (() => void) | undefined;
    vi.mocked(onSessionExpired).mockImplementation((listener) => {
      expiredListener = listener;
      return () => {};
    });

    renderGate();
    await waitFor(() => expect(screen.getByText("conteúdo privado")).toBeTruthy());

    expiredListener?.();

    await waitFor(() =>
      expect(
        screen.getByText("tela de login: Sua sessão expirou. Entre novamente."),
      ).toBeTruthy(),
    );
  });
});