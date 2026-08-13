import aws_cdk as cdk
import aws_cdk.assertions as assertions

from stacks.settings import InfrastructureSettings
from stacks.web_stack import WebStack


def _settings() -> InfrastructureSettings:
    return InfrastructureSettings(
        tenant="sensoriando",
        environment_name="development",
        aws_region="us-east-2",
        aws_account="123456789012",
        resource_prefix="sensoriando_development",
        stack_prefix="sensoriando-development",
        config_parameter_path="/sensoriando/development/common",
    )


def _template(dist_path) -> assertions.Template:
    app = cdk.App()
    settings = _settings()
    stack = WebStack(
        app,
        "sensoriando-development-web",
        settings=settings,
        web_dist_path=str(dist_path),
        env=cdk.Environment(account=settings.aws_account, region=settings.aws_region),
    )
    return assertions.Template.from_stack(stack)


def _built_dist(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html>", encoding="utf-8")
    return dist


def test_provisions_a_bucket_and_a_distribution(tmp_path):
    template = _template(_built_dist(tmp_path))

    template.resource_count_is("AWS::S3::Bucket", 1)
    template.resource_count_is("AWS::CloudFront::Distribution", 1)


def test_the_bucket_blocks_every_form_of_public_access(tmp_path):
    template = _template(_built_dist(tmp_path))

    template.has_resource_properties(
        "AWS::S3::Bucket",
        {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True,
            }
        },
    )


def test_client_errors_fall_back_to_the_spa_entry_point(tmp_path):
    """A refresh on /thing/detail/<uuid> must not 403: S3 has no such key."""
    template = _template(_built_dist(tmp_path))

    distributions = template.find_resources("AWS::CloudFront::Distribution")
    (distribution,) = distributions.values()
    responses = distribution["Properties"]["DistributionConfig"]["CustomErrorResponses"]

    assert {
        (item["ErrorCode"], item["ResponseCode"], item["ResponsePagePath"])
        for item in responses
    } == {(403, 200, "/index.html"), (404, 200, "/index.html")}


def test_publishes_the_build(tmp_path):
    template = _template(_built_dist(tmp_path))

    template.resource_count_is("Custom::CDKBucketDeployment", 1)


def test_skips_the_upload_when_the_build_is_absent(tmp_path):
    template = _template(tmp_path / "absent")

    template.resource_count_is("AWS::S3::Bucket", 1)
    template.resource_count_is("AWS::CloudFront::Distribution", 1)
    template.resource_count_is("Custom::CDKBucketDeployment", 0)


def test_exports_the_site_url(tmp_path):
    template = _template(_built_dist(tmp_path))

    outputs = template.find_outputs("*")
    assert any(key.startswith("SensoriandoWebUrl") for key in outputs)
