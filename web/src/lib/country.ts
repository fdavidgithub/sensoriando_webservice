/** The API's sentinel for a thing that belongs to no account. */
const NO_ACCOUNT = "NR";

// Intl.DisplayNames is built into the browser, which is why no country table
// and no dependency is needed here to replace Django's pycountry.
const displayNames = new Intl.DisplayNames(["pt-BR"], {
  type: "region",
  fallback: "none",
});

export function countryName(code: string | null | undefined): string {
  if (!code) return "";
  if (code === NO_ACCOUNT) return code;

  try {
    return displayNames.of(code) ?? code;
  } catch {
    // Intl throws on a structurally invalid code (not two letters).
    return code;
  }
}
