import pytest

from stacks.settings import read_environment_file


def test_reads_exported_variables(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "export SENSORIANDO_ENVIRONMENT=development\n"
        "export AWS_REGION=us-east-2\n",
        encoding="utf-8",
    )

    assert read_environment_file(env_file) == {
        "SENSORIANDO_ENVIRONMENT": "development",
        "AWS_REGION": "us-east-2",
    }


def test_ignores_comments_and_blank_lines(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# a comment\n\nexport AWS_REGION=us-east-2\n",
        encoding="utf-8",
    )

    assert read_environment_file(env_file) == {"AWS_REGION": "us-east-2"}


def test_strips_an_inline_comment(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("export AWS_REGION=us-east-2  # the region\n", encoding="utf-8")

    assert read_environment_file(env_file) == {"AWS_REGION": "us-east-2"}


def test_keeps_a_hash_inside_a_quoted_value(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('export TOKEN="abc#123"\n', encoding="utf-8")

    assert read_environment_file(env_file) == {"TOKEN": "abc#123"}


def test_returns_nothing_for_a_missing_file(tmp_path):
    assert read_environment_file(tmp_path / "absent") == {}
