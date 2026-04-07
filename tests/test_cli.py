from click.testing import CliRunner

from piphi_rtl433_bridge.cli import main


def test_print_config_supports_repeatable_header_option() -> None:
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "print-config",
            "--runtime-ingest-url",
            "http://runtime.test/ingest/rtl433",
            "--header",
            "X-One=1",
            "--header",
            "X-Two=2",
        ],
    )

    assert result.exit_code == 0
    assert '"X-One": "1"' in result.output
    assert '"X-Two": "2"' in result.output


def test_run_dry_run_prints_resolved_config() -> None:
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "run",
            "--dry-run",
            "--rtl433-command",
            "rtl_433 -F json -M time:unix",
        ],
    )

    assert result.exit_code == 0
    assert '"rtl433_command": [' in result.output


def test_invalid_header_pair_returns_error() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["print-config", "--header", "missing-separator"])

    assert result.exit_code != 0
    assert "KEY=VALUE" in result.output
