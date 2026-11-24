import os
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]


def run_config_check(mpesa_env):
    environment = os.environ.copy()

    if mpesa_env is None:
        environment.pop("MPESA_ENV", None)
    else:
        environment["MPESA_ENV"] = mpesa_env

    return subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from config import Config; "
                "print(Config.MPESA_ENV); "
                "print(Config.MPESA_BASE_URL)"
            )
        ],
        cwd=BACKEND_DIR,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10
    )


def test_mpesa_defaults_to_sandbox():
    result = run_config_check(None)

    assert result.returncode == 0
    assert "sandbox" in result.stdout
    assert "https://sandbox.safaricom.co.ke" in result.stdout


def test_mpesa_production_environment():
    result = run_config_check("production")

    assert result.returncode == 0
    assert "production" in result.stdout
    assert "https://api.safaricom.co.ke" in result.stdout


def test_invalid_mpesa_environment_is_rejected():
    result = run_config_check("invalid")

    assert result.returncode != 0
    assert "MPESA_ENV must be either 'sandbox' or 'production'." in result.stderr


def test_mpesa_environment_is_normalized():
    result = run_config_check(" SANDBOX ")

    assert result.returncode == 0
    assert "sandbox" in result.stdout
    assert "https://sandbox.safaricom.co.ke" in result.stdout
