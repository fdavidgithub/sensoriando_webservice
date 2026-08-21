import { describe, expect, it } from "vitest";

import { normalizePhone } from "./phone";

describe("normalizePhone", () => {
  it("prepends +55 to a number typed with no country code", () => {
    expect(normalizePhone("16999991234")).toBe("+5516999991234");
  });

  it("strips the punctuation a person naturally types", () => {
    expect(normalizePhone("(16) 99999-1234")).toBe("+5516999991234");
  });

  it("keeps an explicit country code, only cleaning the punctuation", () => {
    expect(normalizePhone("+55 16 99999-1234")).toBe("+5516999991234");
  });

  it("trusts a foreign country code someone typed on purpose", () => {
    expect(normalizePhone("+1 555 123 4567")).toBe("+15551234567");
  });

  it("leaves an empty field empty -- phone is optional", () => {
    expect(normalizePhone("")).toBe("");
    expect(normalizePhone("   ")).toBe("");
  });
});
