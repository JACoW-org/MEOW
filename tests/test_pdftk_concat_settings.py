"""Parallelism and JVM options of the pdftk joins."""

import subprocess
from pathlib import Path

import pytest

from meow.app import config

REPO_ROOT = Path(__file__).resolve().parent.parent


def _cpus(monkeypatch, n):
    monkeypatch.setattr(config, "sched_getaffinity", lambda pid: set(range(n)))


@pytest.mark.parametrize("cpus, expected", [(1, 1), (4, 4), (6, 6), (8, 6), (64, 6)])
def test_default_concurrency_is_cpus_up_to_six(monkeypatch, cpus, expected):
    monkeypatch.delenv("PDFTK_CONCURRENCY", raising=False)
    _cpus(monkeypatch, cpus)
    assert config.pdftk_concurrency() == expected


@pytest.mark.parametrize("value, expected", [("2", 2), ("12", 12), ("0", 1), ("-3", 1), ("x", 8), ("", 8)])
def test_concurrency_from_environment(monkeypatch, value, expected):
    monkeypatch.setenv("PDFTK_CONCURRENCY", value)
    _cpus(monkeypatch, 16)
    # an unreadable value falls back to the default (16 CPUs -> 6)
    assert config.pdftk_concurrency() == (6 if expected == 8 else expected)


def _pdftk(*args, opts=None):
    env = {"PATH": "/usr/bin:/bin"}
    if opts is not None:
        env["PDFTK_JAVA_OPTS"] = opts
    return subprocess.run(
        [str(REPO_ROOT / "bin" / "pdftk.sh"), *args],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True,
    )


def test_pdftk_runs_without_java_options():
    assert _pdftk("--version").returncode == 0


def test_pdftk_passes_the_java_options_to_the_jvm():
    ok = _pdftk("--version", opts="-Xmx64m")
    assert ok.returncode == 0

    # an option the JVM does not know makes it fail: the variable is used
    bad = _pdftk("--version", opts="-XX:NoSuchOption")
    assert bad.returncode != 0
    assert "NoSuchOption" in bad.stderr + bad.stdout
