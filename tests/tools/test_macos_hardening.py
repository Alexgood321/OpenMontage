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


import hashlib
import zipfile
from tools.graphics.threejs_asset_catalog import _extract_archive_safely, ThreeJSAssetCatalog


def test_zip_path_traversal_rejected(tmp_path):
    z = tmp_path / "bad.zip"
    with zipfile.ZipFile(z, "w") as a:
        a.writestr("../outside.txt", "bad")
    with pytest.raises(ValueError, match="Unsafe ZIP member path"):
        _extract_archive_safely(z, tmp_path / "extract")
    assert not (tmp_path / "outside.txt").exists()


def test_zip_safe_file(tmp_path):
    z = tmp_path / "good.zip"
    with zipfile.ZipFile(z, "w") as a:
        a.writestr("models/part.gltf", "{}")
    _extract_archive_safely(z, tmp_path / "extract")
    assert (tmp_path / "extract/models/part.gltf").read_text() == "{}"


def test_catalog_install_fails_closed_without_expected_digest(tmp_path):
    result = ThreeJSAssetCatalog().execute({
        "operation": "install",
        "catalog_id": "kenney-nature-kit",
        "output_path": str(tmp_path / "assets"),
    })
    assert not result.success
    assert "expected_sha256" in result.error
