import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/endpoints", () => ({ login: vi.fn(), verifyOtp: vi.fn() }));
vi.mock("../auth/session", () => ({ writeSession: vi.fn(), setIdToken: vi.fn() }));

import LoginPage from "./LoginPage";
import { login, verifyOtp } from "../api/endpoints";
import { setIdToken, writeSession } from "../auth/session";

beforeEach(() => {
  vi.mocked(login).mockReset();
  vi.mocked(verifyOtp).mockReset();
  vi.mocked(writeSession).mockReset();
});

describe("LoginPage", () => {
  it("asks for the code only after the e-mail was submitted", async () => {
    vi.mocked(login).mockResolvedValue({ session: "s", destination: "f***@e***.com" });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    expect(screen.queryByLabelText(/código/i)).toBeNull();

    await userEvent.type(screen.getByLabelText(/e-mail/i), "fulano@example.com");
    await userEvent.click(screen.getByRole("button", { name: /receber código/i }));

    await waitFor(() => expect(screen.getByLabelText(/código/i)).toBeTruthy());
    // The masked address tells the user which inbox to open.
    expect(screen.getByText(/f\*\*\*@e\*\*\*\.com/)).toBeTruthy();
  });

  it("stores the session that verifying the code returns", async () => {
    vi.mocked(login).mockResolvedValue({ session: "s", destination: "d" });
    vi.mocked(verifyOtp).mockResolvedValue({
      username: "fulano",
      id_token: "id",
      refresh_token: "refresh",
      expires_in: 3600,
    });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText(/e-mail/i), "fulano@example.com");
    await userEvent.click(screen.getByRole("button", { name: /receber código/i }));
    await waitFor(() => screen.getByLabelText(/código/i));

    await userEvent.type(screen.getByLabelText(/código/i), "123456");
    await userEvent.click(screen.getByRole("button", { name: /entrar/i }));

    await waitFor(() =>
      expect(writeSession).toHaveBeenCalledWith("fulano", "refresh"),
    );
    expect(setIdToken).toHaveBeenCalledWith("id", 3600);
  });

  it("shows the message when the code is refused", async () => {
    vi.mocked(login).mockResolvedValue({ session: "s", destination: "d" });
    vi.mocked(verifyOtp).mockRejectedValue(
      Object.assign(new Error("código inválido"), { name: "ApiError", status: 400 }),
    );

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText(/e-mail/i), "fulano@example.com");
    await userEvent.click(screen.getByRole("button", { name: /receber código/i }));
    await waitFor(() => screen.getByLabelText(/código/i));

    await userEvent.type(screen.getByLabelText(/código/i), "000000");
    await userEvent.click(screen.getByRole("button", { name: /entrar/i }));

    await waitFor(() => expect(screen.getByText(/código inválido/i)).toBeTruthy());
  });

  it("shows the reason AuthGate sent the user here", () => {
    // AuthGate hands this in location.state when a session expires mid-use;
    // otherwise the user lands here with no explanation for the redirect.
    render(
      <MemoryRouter
        initialEntries={[
          { pathname: "/users/login", state: { message: "Sua sessão expirou. Entre novamente." } },
        ]}
      >
        <Routes>
          <Route path="/users/login" element={<LoginPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("Sua sessão expirou. Entre novamente.")).toBeTruthy();
  });
});