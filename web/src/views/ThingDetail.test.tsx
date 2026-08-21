import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/endpoints", () => ({
  listPrivateThings: vi.fn(),
  listPublicThings: vi.fn(),
  readPrivateDetail: vi.fn(),
  readPublicDetail: vi.fn(),
}));
vi.mock("../auth/session", () => ({ readSession: vi.fn() }));

import {
  listPrivateThings,
  listPublicThings,
  readPublicDetail,
} from "../api/endpoints";
import { readSession } from "../auth/session";
import ThingDetail from "./ThingDetail";

const PUBLIC_THING = {
  thing: "Estufa",
  uuid: "11111111-1111-1111-1111-111111111111",
  lastupdate: "---",
  account: { username: "fulano", city: "Ribeirão Preto", state: "SP", country: "BR" },
  sensors: [{ id: 1, name: "temperatura" }],
  thingtags: [],
};

function renderPage() {
  return render(
    <MemoryRouter initialEntries={[`/thing/detail/${PUBLIC_THING.uuid}`]}>
      <Routes>
        <Route path="/thing/detail/:uuid" element={<ThingDetail />} />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.mocked(listPublicThings).mockReset();
  vi.mocked(listPrivateThings).mockReset();
  vi.mocked(readPublicDetail).mockReset().mockResolvedValue([]);
  vi.mocked(readSession).mockReset();
});

describe("a public device page visited with a stale session", () => {
  it("shows the device instead of a session-expired banner", async () => {
    // Session data is still in localStorage (readSession returns something),
    // but it is 30+ days old: the private listing rejects the way client.ts
    // rejects an unrecoverable refresh.
    vi.mocked(readSession).mockReturnValue({ username: "fulano" });
    vi.mocked(listPublicThings).mockResolvedValue([PUBLIC_THING]);
    vi.mocked(listPrivateThings).mockRejectedValue(
      Object.assign(new Error("Sua sessão expirou. Entre novamente."), {
        name: "ApiError",
        status: 401,
      }),
    );

    renderPage();

    await waitFor(() => expect(screen.getByText("Estufa")).toBeTruthy());
    // A visitor reading a public device must never see an auth error.
    expect(screen.queryByRole("alert")).toBeNull();
  });
});

describe("an anonymous visitor", () => {
  it("never calls the private listing at all", async () => {
    vi.mocked(readSession).mockReturnValue(null);
    vi.mocked(listPublicThings).mockResolvedValue([PUBLIC_THING]);

    renderPage();

    await waitFor(() => expect(screen.getByText("Estufa")).toBeTruthy());
    expect(listPrivateThings).not.toHaveBeenCalled();
  });
});

describe("a device that exists in neither listing", () => {
  it("is reported as not found once both listings have settled", async () => {
    vi.mocked(readSession).mockReturnValue(null);
    vi.mocked(listPublicThings).mockResolvedValue([]);

    renderPage();

    await waitFor(() =>
      expect(screen.getByText("Dispositivo não encontrado.")).toBeTruthy(),
    );
  });
});
