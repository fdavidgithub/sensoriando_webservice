#!/usr/bin/env python3
"""CDK entry point: one stack, the static site."""

import aws_cdk as cdk

from stacks.settings import load_settings
from stacks.web_stack import WebStack

app = cdk.App()
settings = load_settings(app)

WebStack(
    app,
    f"{settings.stack_prefix}-web",
    env=cdk.Environment(
        account=settings.aws_account,
        region=settings.aws_region,
    ),
    settings=settings,
)

app.synth()
