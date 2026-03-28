from functools import lru_cache
from pathlib import Path

import yaml

from app.core.config import settings


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


@lru_cache(maxsize=1)
def load_discovery_registry() -> dict:
    root = settings.resolved_config_root / "discovery"
    employers = _load_yaml(root / "employers.yaml")
    sites = _load_yaml(root / "sites.yaml")
    searches = _load_yaml(root / "searches.example.yaml")

    source_presets: list[dict] = []
    for item in employers.get("employers", []):
        source_presets.append(
            {
                "key": item["key"],
                "label": item["label"],
                "kind": item.get("kind", "workday_board"),
                "base_url": item.get("base_url", ""),
                "config": item.get("config", {}),
                "notes": item.get("notes", ""),
                "tags": item.get("tags", []),
            }
        )
    for item in sites.get("direct_sites", []):
        source_presets.append(
            {
                "key": item["key"],
                "label": item["label"],
                "kind": item.get("kind", "direct_url"),
                "base_url": item.get("base_url", ""),
                "config": item.get("config", {}),
                "notes": item.get("notes", ""),
                "tags": item.get("tags", []),
            }
        )

    return {
        "source_presets": source_presets,
        "search_templates": searches.get("search_templates", []),
        "blocked_domains": sites.get("blocked_domains", []),
    }


def get_source_preset(key: str) -> dict | None:
    registry = load_discovery_registry()
    return next((item for item in registry["source_presets"] if item["key"] == key), None)


def get_search_template(key: str) -> dict | None:
    registry = load_discovery_registry()
    return next((item for item in registry["search_templates"] if item["key"] == key), None)
