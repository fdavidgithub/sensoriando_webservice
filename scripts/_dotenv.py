"""Minimal .env reader shared by the build-time resolver scripts.

Deliberately not python-dotenv: these scripts run before the project's own
dependencies are guaranteed to be installed (e.g. from `npm run build`'s
subprocess call), so this stays stdlib-only.
"""

from pathlib import Path


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")

    return values
