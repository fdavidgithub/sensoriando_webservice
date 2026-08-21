/**
 * Normalizes a phone number to E.164, the format Cognito's `phone_number`
 * attribute requires -- a number typed without it ("16999991234") is what
 * produced a 400 with no explanation of which field was wrong.
 *
 * The signup form only ever offers Brazil as a country (see COUNTRIES in
 * lib/locations.ts), so a number with no leading "+" is assumed Brazilian and
 * gets "+55" prepended. A number that already starts with "+" is trusted as
 * written, just cleaned of the punctuation a person naturally types.
 */
export function normalizePhone(phone: string): string {
  const trimmed = phone.trim();
  if (!trimmed) return "";

  if (trimmed.startsWith("+")) {
    return `+${trimmed.slice(1).replace(/\D/g, "")}`;
  }

  const digits = trimmed.replace(/\D/g, "");
  return digits ? `+55${digits}` : "";
}
