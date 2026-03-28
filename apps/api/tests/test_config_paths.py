from pathlib import Path

from app.core.config import _resolve_existing_path


def test_resolve_existing_path_supports_repo_layout_from_nested_module(tmp_path: Path) -> None:
    repo_root = tmp_path / "applyforge"
    config_root = repo_root / "packages" / "config"
    config_root.mkdir(parents=True)
    anchor = repo_root / "apps" / "api" / "app" / "core" / "config.py"

    resolved = _resolve_existing_path("packages/config", anchor=anchor, cwd=repo_root)

    assert resolved == config_root.resolve()


def test_resolve_existing_path_supports_shallow_container_layout(tmp_path: Path) -> None:
    container_root = tmp_path / "container-app"
    packages_root = container_root / "packages" / "prompts"
    packages_root.mkdir(parents=True)
    anchor = container_root / "app" / "core" / "config.py"
    cwd = container_root

    resolved = _resolve_existing_path("packages/prompts", anchor=anchor, cwd=cwd)

    assert resolved == packages_root.resolve()
