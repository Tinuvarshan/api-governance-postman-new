#!/usr/bin/env python3
"""Create a Spec Hub specification in Postman from specs/<name>/<name>.yaml
and register its ID in .postman/api-mappings.yaml and governance/catalogue.json.

Usage:  POSTMAN_API_KEY=... POSTMAN_WORKSPACE_ID=... \
        python scripts/create-postman-spec.py <api-name>

NOTE: calls POST https://api.postman.com/specs. If it errors, create the spec
manually in Postman (Spec Hub > Import) and paste its ID into the mappings file.
"""
import json, os, re, sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent


def fail(msg):
    sys.exit(f"ERROR: {msg}")


def main():
    if len(sys.argv) != 2:
        fail("Usage: python scripts/create-postman-spec.py <api-name>")
    name = sys.argv[1]
    key = os.environ.get("POSTMAN_API_KEY")
    workspace = os.environ.get("POSTMAN_WORKSPACE_ID")
    if not key or not workspace:
        fail("Set POSTMAN_API_KEY and POSTMAN_WORKSPACE_ID.")

    spec_file = ROOT / "specs" / name / f"{name}.yaml"
    if not spec_file.is_file():
        fail(f"Spec not found: {spec_file}")
    content = spec_file.read_text(encoding="utf-8")

    m = re.search(r"^openapi:\s*[\"']?(\d+\.\d+)", content, re.M)
    if not m:
        fail("Could not read the openapi version from the spec.")
    spec_type = f"OPENAPI:{m.group(1)}"

    body = json.dumps({
        "name": name,
        "type": spec_type,
        "files": [{"path": "index.yaml", "content": content}],
    }).encode()
    req = Request(
        f"https://api.postman.com/specs?workspaceId={workspace}",
        data=body, method="POST",
        headers={"X-Api-Key": key, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "api-governance-demo/1.0"},
    )
    try:
        with urlopen(req, timeout=30) as resp:
            spec_id = json.loads(resp.read())["id"]
    except HTTPError as exc:
        details = exc.read().decode(errors="replace")
        fail(f"Postman returned HTTP {exc.code}: {details}")

    # Register in mappings file (format parsed by detect-changed-apis.py)
    mapping = ROOT / ".postman" / "api-mappings.yaml"
    text = mapping.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    mapping.write_text(text + f"  {name}:\n    spec_id: {spec_id}\n", encoding="utf-8")

    # Record in catalogue if the API is registered there
    cat_path = ROOT / "governance" / "catalogue.json"
    cat = json.loads(cat_path.read_text(encoding="utf-8"))
    if name in cat.get("apis", {}):
        cat["apis"][name]["postman_spec_id"] = spec_id
        cat_path.write_text(json.dumps(cat, indent=2) + "\n", encoding="utf-8")

    print(f"Created Postman spec for {name}: {spec_id}")
    print("Mapping and catalogue updated. Commit both files.")


if __name__ == "__main__":
    main()