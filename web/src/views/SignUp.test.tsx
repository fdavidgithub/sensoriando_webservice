import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/endpoints", () => ({
  signUp: vi.fn(),
  confirmSignUp: vi.fn(),
  resendCode: vi.fn(),
}));
vi.mock("../auth/session", () => ({ writeSession: vi.fn(), setIdToken: vi.fn() }));

import SignUp from "./SignUp";
import { confirmSignUp, resendCode, signUp } from "../api/endpoints";
import { writeSession } from "../auth/session";

beforeEach(() => {
  vi.mocked(signUp).mockReset();
  vi.mocked(confirmSignUp).mockReset();
  vi.mocked(resendCode).mockReset();
  vi.mocked(writeSession).mockReset();
});

const FORM = {
  username: "fulano",
  name: "Fulano de Tal",
  email: "fulano@example.com",
  city: "Ribeirão Preto",
};

async function fillTheForm() {
  await userEvent.type(screen.getByLabelText(/^usuário/i), FORM.username);
  await userEvent.type(screen.getByLabelText(/^nome/i), FORM.name);
  await userEvent.type(screen.getByLabelText(/e-mail/i), FORM.email);
  await userEvent.type(screen.getByLabelText(/cidade/i), FORM.city);
}

describe("SignUp", () => {
  it("has no password field, because the platform has no passwords", () => {
    render(
      <MemoryRouter>
        <SignUp />
      </MemoryRouter>,
    );

    expect(screen.queryByLabelText(/senha/i)).toBeNull();
  });

  it("limits the username to what the column holds", () => {
    render(
      <MemoryRouter>
        <SignUp />
      </MemoryRouter>,
    );

    // accounts.username is VARCHAR(20).
    expect(screen.getByLabelText(/^usuário/i).getAttribute("maxLength")).toBe("20");
  });

  it("signs the user in as soon as the code is confirmed", async () => {
    vi.mocked(signUp).mockResolvedValue({ destination: "f***@e***.com" });
    vi.mocked(confirmSignUp).mockResolvedValue({
      username: "fulano",
      id_token: "id",
      refresh_token: "refresh",
      expires_in: 3600,
    });

    render(
      <MemoryRouter>
        <SignUp />
      </MemoryRouter>,
    );

    await fillTheForm();
    await userEvent.click(screen.getByRole("button", { name: /cadastrar/i }));
    await waitFor(() => screen.getByLabelText(/código/i));

    await userEvent.type(screen.getByLabelText(/código/i), "123456");
    await userEvent.click(screen.getByRole("button", { name: /confirmar/i }));

    // Confirming with the OTP already proves the e-mail, so Cognito hands back
    // a session: the user never types a second code.
    await waitFor(() => expect(writeSession).toHaveBeenCalledWith("fulano", "refresh"));
  });

  it("reports a duplicated e-mail without losing what was typed", async () => {
    vi.mocked(signUp).mockRejectedValue(
      Object.assign(new Error("este e-mail já tem conta"), { name: "ApiError", status: 409 }),
    );

    render(
      <MemoryRouter>
        <SignUp />
      </MemoryRouter>,
    );

    await fillTheForm();
    await userEvent.click(screen.getByRole("button", { name: /cadastrar/i }));

    await waitFor(() => expect(screen.getByText(/já tem conta/i)).toBeTruthy());
    expect((screen.getByLabelText(/^nome/i) as HTMLInputElement).value).toBe(FORM.name);
  });
});