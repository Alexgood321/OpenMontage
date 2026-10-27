"""Regression tests: opt-in is required for high-risk runtime executors."""
from tools.graphics.math_animate import MathAnimate
from tools.video.hyperframes_compose import HyperFramesCompose
import pytest


def test_host_python_code_execution_disabled_by_default(monkeypatch):
    monkeypatch.delenv("OPENMONTAGE_ALLOW_HOST_CODE_EXEC", raising=False)
    result = MathAnimate()._render({"scene_code": "print('test')"})
    assert not result.success
    assert "Disabled by default" in result.error


@pytest.mark.parametrize("version", ["", "latest", "^1.0.0", "1.2", "1.2.3 && touch /tmp/x"])
def test_hyperframes_requires_pinned_semver(monkeypatch, version):
    monkeypatch.setenv("OPENMONTAGE_HYPERFRAMES_VERSION", version)
    assert HyperFramesCompose._pinned_npm_spec() is None


def test_hyperframes_accepts_exact_version(monkeypatch):
    monkeypatch.setenv("OPENMONTAGE_HYPERFRAMES_VERSION", "1.2.3")
    assert HyperFramesCompose._pinned_npm_spec() == "hyperframes@1.2.3"
