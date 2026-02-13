#!/usr/bin/env python3
"""
tools/import_skills_from_uesp.py

Phase 1 "real" importer for external ESO/UESP-like skill data into a preview
skills JSON under raw-imports/, aligned to
docs/ESO-Build-Engine-Data-Model-v1.md Appendix A:
Skills Import Mapping → data/skills.json.

This version still targets PREVIEW USE ONLY. It:

- Accepts a required --snapshot-path argument.
- Expects a simple JSON snapshot at that path with shape:

    {
      "skills": [
        {
          "abilityId": 12345,
          "internalName": "Deep Fissure",
          "classTag": "warden",
          "skillLineTag": "animal_companions",
          "mechanicType": "magicka",
          "baseCost": 2700,
          "castTimeType": "instant",
          "targetType": "enemy_area",
          "baseDurationSeconds": 6.0,
          "radiusMeters": 6.0,
          "isUltimate": false,
          "isPassive": false,
          "rawTooltipText": "Staggering fissure that breaches enemy resistances.",
          "sourceTag": "uesp-api"
        },
        ...
      ]
    }

- Normalizes each external row into a canonical v1 skill object with:
  - id = "skill." + normalized snake_case internalName (or abilityId-based fallback)
  - class_id, skill_line_id derived from *Tag fields
  - resource, cost, cast_time, target, duration_seconds, radius_meters
  - ability_id, external_ids.uesp, tooltip_effect_text
  - effects = [] (effects mapping will be added in a later phase)

- Writes schema-correct preview JSON to:
    raw-imports/skills.import-preview.json

- Never writes to data/skills.json.

This is intentionally conservative and does NOT attempt to derive effects[]
from tooltips yet. It gives you a realistic, multi-record preview file that
validate_data_integrity.py can sanity-check once promoted into data/skills.json.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

# Repository paths (mirrors validate_build.py layout).
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = REPO_ROOT / "docs"
RAW_IMPORTS_DIR = REPO_ROOT / "raw-imports"


# ---------- Filesystem helpers ----------


def ensure_raw_imports_dir() -> None:
    """
    Ensure the raw-imports/ directory exists.

    Per External Data Scope, import tools must write only to
    raw-imports/ during development and preview phases, never
    directly to data/*.json.
    """
    RAW_IMPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------- Container builder ----------


def build_empty_skills_container() -> Dict[str, Any]:
    """
    Return an empty skills container matching the v1 Data Model shape.

    See:
      - docs/ESO-Build-Engine-Data-Model-v1.md
      - Appendix A: Skills Import Mapping → data/skills.json
    """
    return {
        "meta": {
            "source": "tools/import_skills_from_uesp.py",
            "mode": "preview",
            "note": (
                "This file is a preview of normalized skills data. "
                "Promote to data/skills.json only after validation and review."
            ),
        },
        "skills": [],
    }


# ---------- Normalization helpers ----------


_SNAKE_RE = re.compile(r"[^a-z0-9]+")


def to_snake_case(value: str) -> str:
    """
    Convert a human-ish or CamelCase name into lowercase snake_case.

    Examples:
      "Deep Fissure" -> "deep_fissure"
      "GreenDragonBlood" -> "green_dragon_blood"
    """
    value = value.strip().lower()
    value = _SNAKE_RE.sub("_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unnamed"


def normalize_skill_id(internal_name: str, ability_id: Any) -> str:
    """
    Build a canonical skill.* ID.

    Prefer internalName when available; fall back to abilityId-based IDs for
    determinism if the name field is unusable.
    """
    if isinstance(internal_name, str) and internal_name.strip():
        base = to_snake_case(internal_name)
        return f"skill.{base}"

    # Fallback: use abilityId if present.
    if isinstance(ability_id, (int, float)) and ability_id:
        return f"skill.ability_{int(ability_id)}"

    # Final fallback: stable placeholder.
    return "skill.unnamed_placeholder"


def normalize_class_id(class_tag: Any) -> str:
    """
    Map an external classTag into a canonical class_id string.

    This stays ESO-aware only in human terms but uses generic IDs in data.
    """
    if not isinstance(class_tag, str):
        return "unclassified"

    tag = class_tag.strip().lower()
    if not tag:
        return "unclassified"

    # We keep these as simple snake_case tags.
    return to_snake_case(tag)


def normalize_skill_line_id(skill_line_tag: Any) -> str:
    """
    Map an external skillLineTag into a canonical skill_line_id string.
    """
    if not isinstance(skill_line_tag, str):
        return "unspecified"

    tag = skill_line_tag.strip().lower()
    if not tag:
        return "unspecified"

    return to_snake_case(tag)


def normalize_type(is_ultimate: Any, is_passive: Any) -> str:
    """
    Determine skill type (active/passive/ultimate) from flags.
    """
    if bool(is_ultimate):
        return "ultimate"
    if bool(is_passive):
        return "passive"
    return "active"


def normalize_resource(mechanic_type: Any) -> str:
    """
    Map mechanicType into a simple resource enum.
    """
    if not isinstance(mechanic_type, str):
        return "unknown"

    mt = mechanic_type.strip().lower()
    if mt in ("magicka", "stamina", "health"):
        return mt
    return "unknown"


def normalize_cast_time(cast_time_type: Any) -> str:
    """
    Normalize castTimeType into a small enum.
    """
    if not isinstance(cast_time_type, str):
        return "instant"

    ct = cast_time_type.strip().lower()
    if ct in ("instant", "channeled", "cast_time"):
        return ct
    return "instant"


def normalize_target(target_type: Any) -> str:
    """
    Normalize targetType into a small enum.

    We do not attempt to perfectly map ESO targeting logic here; we just
    distinguish some broad categories.
    """
    if not isinstance(target_type, str):
        return "self"

    tt = target_type.strip().lower()
    if "enemy" in tt and "area" in tt:
        return "enemy_area"
    if "enemy" in tt:
        return "enemy"
    if "self" in tt and "area" in tt:
        return "self_area"
    if "ally" in tt or "friend" in tt:
        return "ally"
    return "self"


def normalize_duration(base_duration_seconds: Any) -> Any:
    """
    Pass through numeric durations; otherwise, return None.
    """
    if isinstance(base_duration_seconds, (int, float)):
        return float(base_duration_seconds)
    return None


def normalize_radius(radius_meters: Any) -> Any:
    """
    Pass through numeric radii; otherwise, return None.
    """
    if isinstance(radius_meters, (int, float)):
        return float(radius_meters)
    return None


def normalize_cost(base_cost: Any) -> Any:
    """
    Pass through numeric costs; otherwise, return None.
    """
    if isinstance(base_cost, (int, float)):
        return int(base_cost)
    return None


# ---------- Core transform ----------


def build_skill_record(external_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a single external skill row into the canonical v1 skill object.

    Expected external fields (per the simple JSON snapshot contract):
      - abilityId
      - internalName
      - classTag
      - skillLineTag
      - mechanicType
      - baseCost
      - castTimeType
      - targetType
      - baseDurationSeconds
      - radiusMeters
      - isUltimate / isPassive
      - rawTooltipText
      - sourceTag
    """
    ability_id = external_row.get("abilityId")
    internal_name = external_row.get("internalName") or ""
    class_tag = external_row.get("classTag")
    skill_line_tag = external_row.get("skillLineTag")
    mechanic_type = external_row.get("mechanicType")
    base_cost = external_row.get("baseCost")
    cast_time_type = external_row.get("castTimeType")
    target_type = external_row.get("targetType")
    base_duration_seconds = external_row.get("baseDurationSeconds")
    radius_meters = external_row.get("radiusMeters")
    is_ultimate = external_row.get("isUltimate")
    is_passive = external_row.get("isPassive")
    raw_tooltip = external_row.get("rawTooltipText") or ""
    source_tag = external_row.get("sourceTag") or "external_snapshot"

    skill_id = normalize_skill_id(internal_name, ability_id)
    class_id = normalize_class_id(class_tag)
    skill_line_id = normalize_skill_line_id(skill_line_tag)
    skill_type = normalize_type(is_ultimate, is_passive)
    resource = normalize_resource(mechanic_type)
    cost = normalize_cost(base_cost)
    cast_time = normalize_cast_time(cast_time_type)
    target = normalize_target(target_type)
    duration_seconds = normalize_duration(base_duration_seconds)
    radius_norm = normalize_radius(radius_meters)

    return {
        "id": skill_id,
        "name": internal_name or f"Ability {ability_id}" if ability_id is not None else "Unnamed Skill",
        "class_id": class_id,
        "skill_line_id": skill_line_id,
        "type": skill_type,
        "resource": resource,
        "cost": cost,
        "cast_time": cast_time,
        "target": target,
        "duration_seconds": duration_seconds,
        "radius_meters": radius_norm,
        "ability_id": ability_id,
        "external_ids": {
            "uesp": {
                "abilityId": ability_id,
                "sourceTag": source_tag,
            }
        },
        "tooltip_effect_text": raw_tooltip,
        # Effects mapping will be introduced in a later phase; for now we keep
        # an empty list so validate_data_integrity.py can still enforce shape.
        "effects": [],
    }


# ---------- Snapshot loading ----------


def load_external_snapshot(snapshot_path: Path) -> List[Dict[str, Any]]:
    """
    Load an external ESO/UESP-like snapshot from a simple JSON file.

    Expected shape:
      { "skills": [ { ...external skill fields... }, ... ] }
    """
    if not snapshot_path.exists():
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "message": f"Snapshot path not found: {snapshot_path}",
                }
            )
        )
        return []

    try:
        with snapshot_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "message": f"Failed to read snapshot JSON: {snapshot_path}",
                    "error": str(exc),
                }
            )
        )
        return []

    skills = payload.get("skills", [])
    if not isinstance(skills, list):
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "message": "Snapshot JSON 'skills' field is not a list.",
                }
            )
        )
        return []

    normalized_rows: List[Dict[str, Any]] = []
    for row in skills:
        if isinstance(row, dict):
            normalized_rows.append(row)

    return normalized_rows


# ---------- Preview writer ----------


def write_skills_preview(skills: List[Dict[str, Any]]) -> Path:
    """
    Write a preview skills JSON under raw-imports/ using the canonical v1
    container shape, plus a small meta block.

    This DOES NOT write to data/skills.json. Promotion into data/skills.json
    must be a separate, manual step after validation.
    """
    ensure_raw_imports_dir()
    target_path = RAW_IMPORTS_DIR / "skills.import-preview.json"
    container = build_empty_skills_container()
    container["skills"] = skills

    with target_path.open("w", encoding="utf-8") as f:
        json.dump(container, f, indent=2, ensure_ascii=False)

    return target_path


# ---------- CLI ----------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Import ESO/UESP-like skill data into a preview JSON under raw-imports/, "
            "according to the v1 Data Model and Skills Import Mapping."
        )
    )
    parser.add_argument(
        "--snapshot-path",
        type=str,
        required=True,
        help=(
            "Path to a frozen external snapshot for skills "
            "(JSON file with a top-level 'skills' array)."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Optional limit on number of skills to import (for quick previews). "
            "If omitted, imports all skills in the snapshot."
        ),
    )

    args = parser.parse_args()
    snapshot_path = Path(args.snapshot_path)

    external_rows: List[Dict[str, Any]] = load_external_snapshot(snapshot_path)

    skills: List[Dict[str, Any]] = []
    for idx, row in enumerate(external_rows):
        if args.limit is not None and idx >= args.limit:
            break
        skills.append(build_skill_record(row))

    target_path = write_skills_preview(skills)
    print(
        json.dumps(
            {
                "status": "OK",
                "message": "Skills import preview generated.",
                "skills_count": len(skills),
                "target_path": str(target_path),
                "mode": "preview",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
