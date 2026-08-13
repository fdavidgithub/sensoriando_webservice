#!/usr/bin/env python3
"""Resolve the public URL of an environment's API Gateway.

The identifier AWS assigns to the API is not predictable, so the base URL
cannot be committed to source. It is discovered from the deployed stack's
CloudFormation output instead.

Usage:
    python scripts/resolve_api_url.py [--env development] [--region us-east-2]
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _dotenv import load_dotenv  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_KEY = "SensoriandoApiUrl"


def stack_name(environment_name: str) -> str:
    return f"sensoriando-{environment_name}-api"


def resolve(environment_name: str, region: str, profile: str | None) -> str:
    import boto3

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    client = session.client("cloudformation", region_name=region)
    description = client.describe_stacks(StackName=stack_name(environment_name))

    for output in description["Stacks"][0].get("Outputs", []):
        if output["OutputKey"].startswith(OUTPUT_KEY):
            return output["OutputValue"]

    raise LookupError(f"{OUTPUT_KEY} is absent from {stack_name(environment_name)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", dest="environment_name")
    parser.add_argument("--region")
    arguments = parser.parse_args()

    file_values = load_dotenv(REPOSITORY_ROOT / ".env")

    environment_name = (
        arguments.environment_name
        or os.environ.get("SENSORIANDO_ENVIRONMENT")
        or file_values.get("SENSORIANDO_ENVIRONMENT")
    )
    region = (
        arguments.region
        or os.environ.get("AWS_REGION")
        or file_values.get("AWS_REGION")
    )
    profile = os.environ.get("AWS_PROFILE") or file_values.get("AWS_PROFILE")

    if not environment_name or not region:
        sys.stderr.write("SENSORIANDO_ENVIRONMENT and AWS_REGION must be set\n")
        return 2

    try:
        print(resolve(environment_name, region, profile))
    except Exception as error:  # noqa: BLE001 - the caller only needs the failure
        sys.stderr.write(f"could not resolve the API URL: {error}\n")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
