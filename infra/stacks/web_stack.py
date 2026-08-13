import sys
from pathlib import Path
from typing import Any, Optional

from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3deploy

from stacks.settings import InfrastructureSettings

# Repo-root-relative path to the built SPA (gitignored; produced by
# `npm run build` in web/).
DEFAULT_WEB_DIST = Path(__file__).resolve().parents[2] / "web" / "dist"


class WebStack(Stack):
    """The static site: a private bucket, fronted by CloudFront."""

    def __init__(
        self,
        scope: Any,
        construct_id: str,
        *,
        settings: InfrastructureSettings,
        web_dist_path: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "WebBucket",
            bucket_name=f"{settings.stack_prefix}-web-{settings.aws_account}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # The SPA owns its routes, but S3 only knows the keys it stores. Asking
        # for /thing/detail/<uuid> is a miss there, so both client errors are
        # rewritten to the entry point and the router takes over. Without this,
        # every refresh on a deep link would be a 403.
        self.distribution = cloudfront.Distribution(
            self,
            "WebDistribution",
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
            ],
        )

        # Publish the built SPA and invalidate the cache. Skipped with a warning
        # when the build output is missing, so a synth on a fresh checkout does
        # not fail. Note the blind spot: a *stale* dist/ is uploaded silently,
        # which is why `make deploy` always rebuilds first.
        dist_path = Path(web_dist_path) if web_dist_path else DEFAULT_WEB_DIST
        if dist_path.is_dir():
            s3deploy.BucketDeployment(
                self,
                "WebDeployment",
                sources=[s3deploy.Source.asset(str(dist_path))],
                destination_bucket=bucket,
                distribution=self.distribution,
                distribution_paths=["/*"],
            )
        else:
            print(
                f"[WebStack] WARNING: {dist_path} not found; skipping upload. "
                "Run `npm run build` in web/ before deploying this stack.",
                file=sys.stderr,
            )

        CfnOutput(
            self,
            "SensoriandoWebUrl",
            value=f"https://{self.distribution.distribution_domain_name}",
            export_name=f"{settings.stack_prefix}-web-url",
        )
