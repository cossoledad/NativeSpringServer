#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATE_FILE="${REPO_ROOT}/Config/maven-settings-template.xml"
OUTPUT_FILE="${REPO_ROOT}/Config/maven-settings.xml"
PROJECT_CONFIG_TEMPLATE="${REPO_ROOT}/Config/project-config-template.json"
PROJECT_CONFIG_FILE="${REPO_ROOT}/Config/project-config.json"
USER_M2_SETTINGS="${HOME}/.m2/settings.xml"

python3 - "${TEMPLATE_FILE}" "${OUTPUT_FILE}" "${PROJECT_CONFIG_TEMPLATE}" "${PROJECT_CONFIG_FILE}" "${USER_M2_SETTINGS}" "${REPO_ROOT}" <<'PY'
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

template_file = Path(sys.argv[1])
output_file = Path(sys.argv[2])
project_config_template = Path(sys.argv[3])
project_config_file = Path(sys.argv[4])
user_m2_settings = Path(sys.argv[5])
repo_root = Path(sys.argv[6])

if not template_file.exists():
    raise SystemExit(f"Template not found: {template_file}")


def load_config(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return {k: str(v) if v is not None else "" for k, v in data.items()}


cfg = {}
cfg.update(load_config(project_config_template))
cfg.update(load_config(project_config_file))

repo_id = cfg.get("DEFAULT_MAVEN_RELEASES_REPO_ID", "maven-releases").strip() or "maven-releases"
repo_url = cfg.get("DEFAULT_MAVEN_RELEASES_REPO_URL", "").strip()
if not repo_url:
    repo_url = "http://172.30.0.1:19091/repository/maven-releases/"
local_repo = str((repo_root / ".m2" / "repository").resolve())

username = "__RELEASES_REPO_USERNAME__"
password = "__RELEASES_REPO_PASSWORD__"

if user_m2_settings.exists():
    ns = {"m": "http://maven.apache.org/SETTINGS/1.2.0"}
    root = ET.parse(user_m2_settings).getroot()
    candidates = [repo_id, "ps-releases", "maven-releases"]
    servers = root.findall("m:servers/m:server", ns)
    selected = None
    for sid in candidates:
        selected = next((s for s in servers if (s.findtext("m:id", default="", namespaces=ns) or "").strip() == sid), None)
        if selected is not None:
            break
    if selected is None and servers:
        selected = servers[0]
    if selected is not None:
        u = (selected.findtext("m:username", default="", namespaces=ns) or "").strip()
        p = (selected.findtext("m:password", default="", namespaces=ns) or "").strip()
        if u:
            username = u
        if p:
            password = p

xml = template_file.read_text(encoding="utf-8")
xml = xml.replace("__LOCAL_REPOSITORY__", local_repo)
xml = xml.replace("__RELEASES_REPO_ID__", repo_id)
xml = xml.replace("__RELEASES_REPO_URL__", repo_url)
xml = xml.replace("__RELEASES_REPO_USERNAME__", username)
xml = xml.replace("__RELEASES_REPO_PASSWORD__", password)

output_file.write_text(xml, encoding="utf-8")
print(f"Generated: {output_file}")
PY

echo "Done. You can use: mvn -s ${OUTPUT_FILE} ..."
