import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import AuthGate from "./AuthGate";

vi.mock("./session", () => ({ readSession: vi.fn() }));
vi.mock("../api/client", () => ({
  ensureIdToken: vi.fn(),
  SESSION_EXPIRED: "Sua sessão expirou. Entre novamente.",
}));

import { ensureIdToken } from "../api/client";
import { readSession } from "./session";

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
        <Route path="/users/login" element={<p>tela de login</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.mocked(readSession).mockReset();
  vi.mocked(ensureIdToken).mockReset();
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
});