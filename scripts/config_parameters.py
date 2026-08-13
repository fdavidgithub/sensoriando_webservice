#!/usr/bin/env python3
"""Publish and inspect this environment's configuration in SSM Parameter Store.

One parameter per key, under /sensoriando/<environment>/web.

Usage:
    python scripts/config_parameters.py check  [--env development]
    python scripts/config_parameters.py ensure [--env development]

The manifest below is empty on purpose. The static site holds no secret: the
API URL is discovered from CloudFormation at build time, there is no password
(the login is a passwordless gate), and there is no custom domain or
certificate yet. The mechanism exists so that the first real key -- Cognito
ids, a domain, a certificate ARN -- is one declaration rather than a new
script. See the design document, decision D8.
"""

import argparse
import os
import sys
from getpass import getpass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _dotenv import load_dotenv  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TENANT = "sensoriando"
DOMAIN = "web"

# key -> stored as SecureString
PARAMETERS: dict[str, bool] = {}


def parameter_path(environment_name: str, key: str) -> str:
    return f"/{TENANT}/{environment_name}/{DOMAIN}/{key}"


def missing_keys(existing: set[str]) -> list[str]:
    return [key for key in PARAMETERS if key not in existing]


def _client(region: str | None, profile: str | None):
    import boto3

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    return session.client("ssm", region_name=region) if region else session.client("ssm")


def _existing_keys(client, environment_name: str) -> set[str]:
    path = f"/{TENANT}/{environment_name}/{DOMAIN}"
    found: set[str] = set()

    paginator = client.get_paginator("get_parameters_by_path")
    for page in paginator.paginate(Path=path, Recursive=True, WithDecryption=False):
        for parameter in page["Parameters"]:
            found.add(parameter["Name"].rsplit("/", 1)[-1])

    return found


def _put(client, environment_name: str, key: str, value: str) -> None:
    client.put_parameter(
        Name=parameter_path(environment_name, key),
        Value=value,
        Type="SecureString" if PARAMETERS[key] else "String",
        Overwrite=True,
    )


def _ask(key: str) -> str:
    prompt = f"value for {key}: "
    return getpass(prompt) if PARAMETERS[key] else input(prompt)


def command_check(client, environment_name: str) -> int:
    missing = missing_keys(_existing_keys(client, environment_name))

    if missing:
        print(f"missing in {environment_name}: {', '.join(missing)}")
        return 1

    print(f"every key is present in {environment_name}")
    return 0


def command_ensure(client, environment_name: str) -> int:
    for key in missing_keys(_existing_keys(client, environment_name)):
        value = os.environ.get(key) or _ask(key)
        if not value:
            print(f"{key} has no value; aborting")
            return 1
        _put(client, environment_name, key, value)
        print(f"published {parameter_path(environment_name, key)}")

    return 0


COMMANDS = {"check": command_check, "ensure": command_ensure}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("--env", dest="environment_name")
    arguments = parser.parse_args()

    file_values = load_dotenv(REPOSITORY_ROOT / ".env")

    environment_name = (
        arguments.environment_name
        or os.environ.get("SENSORIANDO_ENVIRONMENT")
        or file_values.get("SENSORIANDO_ENVIRONMENT")
    )
    if not environment_name:
        sys.stderr.write("SENSORIANDO_ENVIRONMENT must be set\n")
        return 2

    # An empty manifest has nothing to read from AWS; skip the client entirely
    # so `make deploy` works without credentials until the first key exists.
    if not PARAMETERS:
        print(f"no configuration key is declared for {environment_name}")
        return 0

    region = os.environ.get("AWS_REGION") or file_values.get("AWS_REGION")
    profile = os.environ.get("AWS_PROFILE") or file_values.get("AWS_PROFILE")

    return COMMANDS[arguments.command](_client(region, profile), environment_name)


if __name__ == "__main__":
    raise SystemExit(main())
