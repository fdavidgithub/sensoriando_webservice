"""Deploy-time settings, read from the repository `.env`.

Everything here is derived from the target environment, and everything derived
is a name: resource prefixes and the Parameter Store path. No configurable
value and no secret passes through this module.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

import aws_cdk as cdk

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

TENANT = "sensoriando"
ENVIRONMENT_NAME_PATTERN = re.compile(r"[a-z][a-z0-9]*")


@dataclass(frozen=True)
class InfrastructureSettings:
    tenant: str
    environment_name: str
    aws_region: str
    aws_account: str | None
    resource_prefix: str
    stack_prefix: str
    config_parameter_path: str


def read_environment_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        value = value.strip()
        # An inline comment (`KEY=value  # note`) is only a comment outside a
        # quoted value -- shell itself would not treat `#` inside quotes as one
        # either. A trailing " #" would otherwise silently join the value,
        # producing an unrecognizable AWS region instead of a clear error.
        if not value.startswith(("'", '"')) and " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        values[key.strip()] = value.strip("'\"")

    return values


def load_settings(app: cdk.App) -> InfrastructureSettings:
    file_values = read_environment_file(REPOSITORY_ROOT / ".env")

    environment_name = os.getenv("SENSORIANDO_ENVIRONMENT") or file_values.get(
        "SENSORIANDO_ENVIRONMENT"
    )
    if not environment_name or not ENVIRONMENT_NAME_PATTERN.fullmatch(environment_name):
        raise ValueError(
            "SENSORIANDO_ENVIRONMENT must be defined and contain only lowercase "
            "letters and digits, starting with a letter"
        )

    aws_region = os.getenv("AWS_REGION") or file_values.get("AWS_REGION")
    if not aws_region:
        raise ValueError("AWS_REGION must be defined in .env")

    aws_account = (
        os.getenv("AWS_ACCOUNT_ID")
        or app.node.try_get_context("aws_account")
        or os.getenv("CDK_DEFAULT_ACCOUNT")
    )

    return InfrastructureSettings(
        tenant=TENANT,
        environment_name=environment_name,
        aws_region=aws_region,
        aws_account=aws_account,
        resource_prefix=f"{TENANT}_{environment_name}",
        stack_prefix=f"{TENANT}-{environment_name}",
        config_parameter_path=f"/{TENANT}/{environment_name}/common",
    )
