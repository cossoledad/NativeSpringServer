from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_CONFIG_FILE = REPO_ROOT / "Config" / "project-config.json"
PROJECT_CONFIG_TEMPLATE_FILE = REPO_ROOT / "Config" / "project-config-template.json"

_DEFAULTS = {
    "DEFAULT_CONAN_REMOTE_NAME": "conan-pr",
    "DEFAULT_CONAN_REMOTE_URL": "http://172.27.128.1:19091/repository/conan-pr/",
    "DEFAULT_MAVEN_RELEASES_REPO_ID": "maven-releases",
    "DEFAULT_MAVEN_RELEASES_REPO_URL": "http://172.27.128.1:19091/repository/maven-releases/",
    "PROJECT_MAVEN_SETTINGS": "",
}


def _read_json_config(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return {k: str(v) if v is not None else "" for k, v in data.items()}


def load_project_config() -> dict[str, str]:
    config = dict(_DEFAULTS)
    if PROJECT_CONFIG_TEMPLATE_FILE.exists():
        config.update(_read_json_config(PROJECT_CONFIG_TEMPLATE_FILE))
    if PROJECT_CONFIG_FILE.exists():
        # project-config.json overrides template values when present.
        config.update(_read_json_config(PROJECT_CONFIG_FILE))
    settings_path = config.get("PROJECT_MAVEN_SETTINGS", "").strip()
    if settings_path:
        path_obj = Path(settings_path).expanduser()
        if not path_obj.is_absolute():
            path_obj = (REPO_ROOT / path_obj).resolve()
        config["PROJECT_MAVEN_SETTINGS"] = str(path_obj)
    return config


PROJECT_CONFIG = load_project_config()
DEFAULT_CONAN_REMOTE_NAME = PROJECT_CONFIG["DEFAULT_CONAN_REMOTE_NAME"]
DEFAULT_CONAN_REMOTE_URL = PROJECT_CONFIG["DEFAULT_CONAN_REMOTE_URL"]
DEFAULT_MAVEN_RELEASES_REPO_ID = PROJECT_CONFIG["DEFAULT_MAVEN_RELEASES_REPO_ID"]
DEFAULT_MAVEN_RELEASES_REPO_URL = PROJECT_CONFIG["DEFAULT_MAVEN_RELEASES_REPO_URL"]
PROJECT_MAVEN_SETTINGS = PROJECT_CONFIG["PROJECT_MAVEN_SETTINGS"]
