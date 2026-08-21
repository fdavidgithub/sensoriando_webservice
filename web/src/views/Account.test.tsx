import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/endpoints", () => ({
  readPrivateAccount: vi.fn(),
  savePrivateAccount: vi.fn(),
  linkThing: vi.fn(),
  listSensorUnits: vi.fn(),
  listPrivateThings: vi.fn(),
}));

import Account from "./Account";
import {
  linkThing,
  listPrivateThings,
  listSensorUnits,
  readPrivateAccount,
  savePrivateAccount,
} from "../api/endpoints";

beforeEach(() => {
  vi.mocked(readPrivateAccount).mockReset();
  vi.mocked(savePrivateAccount).mockReset();
  vi.mocked(linkThing).mockReset();
  vi.mocked(listSensorUnits).mockReset();
  vi.mocked(listPrivateThings).mockReset();
});

const ACCOUNT = {
  username: "fulano",
  name: "Fulano de Tal",
  email: "fulano@example.com",
  phone: "16999991234",
  city: "Ribeirão Preto",
  state: "SP",
  country: "BR",
};

function renderProfile() {
  return render(
    <MemoryRouter initialEntries={["/users/account/fulano/profile"]}>
      <Routes>
        <Route path="/users/account/:username/:tab" element={<Account />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("the profile tab", () => {
  it("shows one name field, because the ERP stores one name", async () => {
    vi.mocked(readPrivateAccount).mockResolvedValue(ACCOUNT);

    renderProfile();

    await waitFor(() =>
      expect((screen.getByLabelText(/^nome/i) as HTMLInputElement).value).toBe(
        "Fulano de Tal",
      ),
    );
    expect(screen.queryByLabelText(/sobrenome/i)).toBeNull();
  });

  it("does not let the e-mail be edited", async () => {
    vi.mocked(readPrivateAccount).mockResolvedValue(ACCOUNT);

    renderProfile();

    await waitFor(() =>
      expect((screen.getByLabelText(/e-mail/i) as HTMLInputElement).readOnly).toBe(true),
    );
  });

  it("saves without the fields it does not own", async () => {
    vi.mocked(readPrivateAccount).mockResolvedValue(ACCOUNT);
    vi.mocked(savePrivateAccount).mockResolvedValue(undefined);

    renderProfile();
    await waitFor(() => screen.getByLabelText(/^nome/i));
    await userEvent.click(screen.getByRole("button", { name: /salvar/i }));

    const sent = vi.mocked(savePrivateAccount).mock.calls[0][0];
    expect(sent).not.toHaveProperty("username");
    expect(sent).not.toHaveProperty("email");
  });
});

describe("the things tab", () => {
  it("turns a 409 from linking into the expected message", async () => {
    vi.mocked(listPrivateThings).mockResolvedValue([]);
    vi.mocked(linkThing).mockRejectedValue(
      Object.assign(new Error("a api respondeu 409"), { name: "ApiError", status: 409 }),
    );

    render(
      <MemoryRouter initialEntries={["/users/account/fulano/things"]}>
        <Routes>
          <Route path="/users/account/:username/:tab" element={<Account />} />
        </Routes>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText(/nova central/i), "a-b-c-d");
    await userEvent.click(screen.getByRole("button", { name: /adicionar/i }));

    await waitFor(() =>
      expect(screen.getByText(/já pertence a uma conta/i)).toBeTruthy(),
    );
  });
});
