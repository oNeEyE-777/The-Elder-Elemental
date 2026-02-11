"""
tools/import_skills_from_uesp.py

Stub importer for external ESO/UESP skill data into data/skills.json,
aligned to docs/ESO-Build-Engine-Data-Model-v1.md Appendix A: Skills
Import Mapping → data/skills.json.

This version does NOT parse real UESP exports yet. It:

- Accepts a required --snapshot-path argument (for future use).
- Writes a schema-correct data/skills.json file with an empty "skills" array.
- Documents the expected external concepts and target fields.

Once external snapshots are available and the detailed mapping spec is
finalized, the placeholder logic in build_skill_record() and the main()
loop should be replaced with real transforms.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

# Repository paths (mirrors validate_build.py layout).
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = REPO_ROOT / "docs"


def ensure_data_dir() -> None:
    """
    Ensure the data/ directory exists.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def build_empty_skills_container() -> Dict[str, Any]:
    """
    Return an empty skills container matching the v1 Data Model shape.

    See:
      - docs/ESO-Build-Engine-Data-Model-v1.md
      - Appendix A: Skills Import Mapping → data/skills.json
    """
    return {
        "skills": []
    }


def build_skill_record(external_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder transform from a single external skill row to the canonical
    skill object defined in the v1 Data Model.

    This is a stub; it documents the target fields but does not use the input.

    Expected external concepts (per Appendix A, summarized):
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

    Target fields (per v1 Data Model + Appendix A):
      - id (internal skill.* ID)
      - name
      - class_id
      - skill_line_id
      - type
      - resource
      - cost
      - cast_time
      - target
      - duration_seconds
      - radius_meters
      - ability_id
      - external_ids.uesp
      - tooltip_effect_text
      - effects[]
    """
    # NOTE: This function intentionally returns a fixed, minimal example
    # shape as a reference. Real logic will:
    # - Generate deterministic skill IDs from abilityId/internalName.
    # - Normalize classTag/skillLineTag into class_id/skill_line_id.
    # - Map mechanicType, castTimeType, targetType into enums.
    # - Copy abilityId, rawTooltipText, and sourceTag into the appropriate fields.
    return {
        "id": "skill.example_placeholder",
        "name": "Example Placeholder Skill",
        "class_id": "universal",
        "skill_line_id": "soul_magic",
        "type": "active",
        "resource": "magicka",
        "cost": None,
        "cast_time": "instant",
        "target": "self",
        "duration_seconds": None,
        "radius_meters": None,
        "ability_id": None,
        "external_ids": {
            "uesp": None
        },
        "tooltip_effect_text": (
            "Placeholder skill created by tools/import_skills_from_uesp.py stub. "
            "Replace this record once real import logic is implemented."
        ),
        "effects": []
    }


def load_external_snapshot(snapshot_path: Path) -> List[Dict[str, Any]]:
    """
    Placeholder loader for an external UESP/ESO snapshot.

    For now, this function only verifies that the path exists (if provided) and
    returns an empty list. In a future iteration, this will:

      - Read one or more CSV/TSV/JSON files from snapshot_path.
      - Map raw columns onto the conceptual external fields described in
        Appendix A (abilityId, internalName, etc.).
      - Return a list of normalized external row dicts for build_skill_record().
    """
    if not snapshot_path.exists():
        # For the stub, we do not treat this as a hard error; we simply
        # log the situation via print and proceed with an empty list.
        print(
            json.dumps(
                {
                    "status": "WARN",
                    "message": f"Snapshot path not found (stub mode): {snapshot_path}"
                }
            )
        )
        return []

    # Future implementation: parse snapshot_path contents.
    return []


def write_skills_json(skills: List[Dict[str, Any]]) -> Path:
    """
    Write data/skills.json using the canonical v1 container shape.

    This overwrites any existing data/skills.json file, in line with the
    full-file replacement rule for canonical JSON. The caller is responsible
    for running validators afterward.
    """
    ensure_data_dir()
    target_path = DATA_DIR / "skills.json"
    container = {
        "skills": skills
    }
    with target_path.open("w", encoding="utf-8") as f:
        json.dump(container, f, indent=2, ensure_ascii=False)
    return target_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Import ESO/UESP skill data into data/skills.json "
            "according to the v1 Data Model and Skills Import Mapping."
        )
    )
    parser.add_argument(
        "--snapshot-path",
        type=str,
        required=True,
        help=(
            "Path to a frozen external snapshot for skills "
            "(e.g., raw-data/eso-api-XXXX/skills/). "
            "In this stub version, it is only checked for existence."
        ),
    )
    parser.add_argument(
        "--include-placeholder-example",
        action="store_true",
        help=(
            "If set, writes a single example placeholder skill record to help "
            "verify schema wiring. Without this flag, writes an empty skills list."
        ),
    )

    args = parser.parse_args()
    snapshot_path = Path(args.snapshot_path)

    external_rows: List[Dict[str, Any]] = load_external_snapshot(snapshot_path)

    skills: List[Dict[str, Any]] = []
    if args.include_placeholder_example:
        # Add one placeholder skill to confirm shape and wiring.
        skills.append(build_skill_record({}))

    # In a future implementation, we will transform each external_rows entry:
    # for row in external_rows:
    #     skills.append(build_skill_record(row))

    target_path = write_skills_json(skills)
    print(
        json.dumps(
            {
                "status": "OK",
                "message": "Stub import completed; skills.json written.",
                "skills_count": len(skills),
                "target_path": str(target_path),
                "mode": "placeholder" if args.include_placeholder_example else "empty",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
