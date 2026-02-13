#!/usr/bin/env python3
"""
tools/validate_import_preview.py

Lightweight validator for import preview files under raw-imports/,
primarily for skills.import-preview.json in the current phase.

Goals:
- Ensure preview files follow the v1 Data Model shapes closely enough
  that promoting them into data/*.json is safe.
- Catch obvious schema issues (bad prefixes, missing required fields,
  wrong types) early.

This does NOT mutate any files; it only reads and reports.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_IMPORTS_DIR = REPO_ROOT / "raw-imports"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_skill_record(skill: Dict[str, Any]) -> List[str]:
    """
    Validate a single skill record from a preview file against the v1 shape
    we expect for data/skills.json.

    We keep this focused on:
    - id prefix and uniqueness (uniqueness is handled at the container level).
    - presence and type of core fields.
    - not validating 'effects' contents yet (Phase 1 has effects=[]).
    """
    errors: List[str] = []

    sid = skill.get("id")
    if not isinstance(sid, str) or not sid.startswith("skill."):
        errors.append(f"skill.id missing or not prefixed with 'skill.': {sid!r}")

    name = skill.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append(f"skill.name missing or empty for id={sid!r}")

    class_id = skill.get("class_id")
    if not isinstance(class_id, str) or not class_id:
        errors.append(f"skill.class_id missing or not a string for id={sid!r}")

    skill_line_id = skill.get("skill_line_id")
    if not isinstance(skill_line_id, str) or not skill_line_id:
        errors.append(f"skill.skill_line_id missing or not a string for id={sid!r}")

    skill_type = skill.get("type")
    if skill_type not in ("active", "passive", "ultimate"):
        errors.append(
            f"skill.type must be 'active'|'passive'|'ultimate' for id={sid!r}, got {skill_type!r}"
        )

    resource = skill.get("resource")
    if not isinstance(resource, str):
        errors.append(f"skill.resource must be a string for id={sid!r}, got {resource!r}")

    # cost can be None or int
    cost = skill.get("cost")
    if cost is not None and not isinstance(cost, int):
        errors.append(f"skill.cost must be int or null for id={sid!r}, got {cost!r}")

    cast_time = skill.get("cast_time")
    if not isinstance(cast_time, str):
        errors.append(f"skill.cast_time must be a string for id={sid!r}, got {cast_time!r}")

    target = skill.get("target")
    if not isinstance(target, str):
        errors.append(f"skill.target must be a string for id={sid!r}, got {target!r}")

    duration = skill.get("duration_seconds")
    if duration is not None and not isinstance(duration, (int, float)):
        errors.append(
            f"skill.duration_seconds must be number or null for id={sid!r}, got {duration!r}"
        )

    radius = skill.get("radius_meters")
    if radius is not None and not isinstance(radius, (int, float)):
        errors.append(
            f"skill.radius_meters must be number or null for id={sid!r}, got {radius!r}"
        )

    # ability_id can be None or number
    ability_id = skill.get("ability_id")
    if ability_id is not None and not isinstance(ability_id, (int, float)):
        errors.append(
            f"skill.ability_id must be number or null for id={sid!r}, got {ability_id!r}"
        )

    # external_ids.uesp is optional but, if present, should be an object
    external_ids = skill.get("external_ids")
    if external_ids is not None and not isinstance(external_ids, dict):
        errors.append(
            f"skill.external_ids must be object or null for id={sid!r}, got {external_ids!r}"
        )

    tooltip = skill.get("tooltip_effect_text")
    if tooltip is not None and not isinstance(tooltip, str):
        errors.append(
            f"skill.tooltip_effect_text must be string or null for id={sid!r}, got {tooltip!r}"
        )

    effects = skill.get("effects")
    if effects is None:
        errors.append(f"skill.effects must be present (can be empty list) for id={sid!r}")
    elif not isinstance(effects, list):
        errors.append(f"skill.effects must be a list for id={sid!r}, got {type(effects)!r}")
    # Phase 1: we do not enforce per-entry shape within effects[] yet.

    return errors


def validate_skills_container(container: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Validate the top-level skills import-preview container.

    Returns:
      (errors, warnings)
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(container, dict):
        return (["Top-level JSON must be an object."], warnings)

    meta = container.get("meta", {})
    if not isinstance(meta, dict):
        errors.append("meta must be an object.")
    else:
        mode = meta.get("mode")
        if mode != "preview":
            warnings.append(f"meta.mode is {mode!r}, expected 'preview'.")

    skills = container.get("skills")
    if not isinstance(skills, list):
        errors.append("skills must be a list at top level.")
        return (errors, warnings)

    # ID uniqueness and per-skill validation.
    seen_ids: set[str] = set()
    for idx, skill in enumerate(skills):
        if not isinstance(skill, dict):
            errors.append(f"skills[{idx}] is not an object.")
            continue

        sid = skill.get("id")
        if isinstance(sid, str):
            if sid in seen_ids:
                errors.append(f"Duplicate skill.id found: {sid!r}")
            else:
                seen_ids.add(sid)

        per_skill_errors = validate_skill_record(skill)
        errors.extend(per_skill_errors)

    return (errors, warnings)


def validate_skills_preview(path: Path) -> Dict[str, Any]:
    """
    Validate raw-imports/skills.import-preview.json and return a status dict.
    """
    status: Dict[str, Any] = {
        "file": str(path),
        "status": "OK",
        "error_count": 0,
        "warning_count": 0,
        "errors": [],
        "warnings": [],
    }

    if not path.exists():
        status["status"] = "ERROR"
        status["error_count"] = 1
        status["errors"] = [f"File not found: {path}"]
        return status

    try:
        container = load_json(path)
    except Exception as exc:  # noqa: BLE001
        status["status"] = "ERROR"
        status["error_count"] = 1
        status["errors"] = [f"Failed to read JSON: {exc!r}"]
        return status

    errors, warnings = validate_skills_container(container)

    status["errors"] = errors
    status["warnings"] = warnings
    status["error_count"] = len(errors)
    status["warning_count"] = len(warnings)

    if errors:
        status["status"] = "ERROR"
    elif warnings:
        status["status"] = "WARN"
    else:
        status["status"] = "OK"

    return status


def main(argv: list[str]) -> int:
    # For now, we only validate skills.import-preview.json; later we can
    # extend this to sets/CP previews as needed.
    preview_path = RAW_IMPORTS_DIR / "skills.import-preview.json"
    result = validate_skills_preview(preview_path)
    json.dump(result, sys.stdout, indent=2)
    print()
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
