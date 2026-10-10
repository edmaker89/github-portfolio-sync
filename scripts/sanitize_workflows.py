#!/usr/bin/env python3
"""Create reviewable workflow copies from the five local n8n API snapshots."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workflows"
DESTINATION = SOURCE / "sanitized"


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def replace_strings(value, replacements):
    if isinstance(value, dict):
        return {key: replace_strings(child, replacements) for key, child in value.items()}
    if isinstance(value, list):
        return [replace_strings(child, replacements) for child in value]
    if isinstance(value, str):
        for original, placeholder in replacements:
            value = value.replace(original, placeholder)
    return value


def main():
    paths = sorted(SOURCE.glob("[0-9][0-9]-*.json"))
    if len(paths) != 5:
        raise SystemExit(f"Expected 5 API snapshots; found {len(paths)}")

    originals = {path.name: json.loads(path.read_text()) for path in paths}
    credentials = set()
    for workflow in originals.values():
        for obj in walk(workflow):
            refs = obj.get("credentials")
            if isinstance(refs, dict):
                for credential_type, ref in refs.items():
                    if isinstance(ref, dict):
                        credentials.add((credential_type, str(ref.get("id", "")), str(ref.get("name", ""))))

    replacements = {}
    for index, (_, credential_id, credential_name) in enumerate(sorted(credentials), start=1):
        label = f"CREDENTIAL_{index:02d}"
        if credential_id:
            replacements[credential_id] = f"REPLACE_WITH_{label}_ID"
        if credential_name:
            replacements[credential_name] = f"REPLACE_WITH_{label}_NAME"
    ordered = sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True)

    DESTINATION.mkdir(exist_ok=True)
    for name, workflow in originals.items():
        sanitized = replace_strings(workflow, ordered)
        sanitized["pinData"] = {}
        sanitized["shared"] = []
        rendered = json.dumps(sanitized, ensure_ascii=False, indent=2) + "\n"
        if any(original in rendered for original in replacements):
            raise SystemExit(f"Credential reference remains in {name}")
        (DESTINATION / name).write_text(rendered)

    print(f"Sanitized {len(paths)} workflows; replaced {len(credentials)} credential references.")


if __name__ == "__main__":
    main()
