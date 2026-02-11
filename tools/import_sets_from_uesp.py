"""
tools/import_sets_from_uesp.py

Stub importer for external ESO/UESP set data into data/sets.json,
aligned to docs/ESO-Build-Engine-Data-Model-v1.md
Appendix B: Sets Import Mapping → data/sets.json.

This version does NOT parse real UESP exports yet. It:

- Accepts a required --snapshot-path argument (for future use).
- Writes a schema-correct data/sets.json file with either:
  - an empty "sets" array, or
  - a single placeholder set record when --include-placeholder-example is set.
- Documents the expected external concepts and target fields.

Once external snapshots are available and detailed mapping is finalized,
the placeholder logic in build_set_record() and the main() loop should
be replaced with real transforms.
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


def build_empty_sets_container() -> Dict[str, Any]:
    """
    Return an empty sets container matching the v1 Data Model shape.

    See:
      - docs/ESO-Build-Engine-Data-Model-v1.md
      - Appendix B: Sets Import Mapping → data/sets.json
    """
    return {
        "sets": []
    }


def build_set_record(external_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder transform from a single external set row to the canonical
    set object defined in the v1 Data Model.

    This is a stub; it documents the target fields but does not use the input.

    Expected external concepts (per Appendix B, summarized):
      - setId
      - setName
      - setType
      - setSource
      - setTags
      - bonusRows:
        - piecesRequired
        - bonusTooltipRaw
        - bonusEffectIdentifiers (optional)

    Target fields (per v1 Data Model + Appendix B):
      - id (internal set.* ID)
      - name
      - type
      - source
      - tags[]
      - set_id
      - external_ids.eso_sets_api
      - bonuses[] with:
        - pieces
        - tooltip_raw
        - effects[]
    """
    # NOTE: This function intentionally returns a fixed, minimal example
    # shape as a reference. Real logic will:
    # - Generate deterministic set IDs from setId/setName.
    # - Normalize setType and setSource into type/source enums.
    # - Copy setId and any external keys into set_id/external_ids.
    # - Populate bonuses[].effects with real effect IDs from data/effects.json.
    return {
        "id": "set.example_placeholder",
        "name": "Example Placeholder Set",
        "type": "armor",
        "source": "overland",
        "tags": ["example", "stub"],
        "set_id": None,
        "external_ids": {
            "eso_sets_api": None
        },
        "bonuses": [
            {
                "pieces": 5,
                "tooltip_raw": (
                    "Placeholder set bonus created by "
                    "tools/import_sets_from_uesp.py stub. "
                    "Replace this record once real import logic is implemented."
                ),
                "effects": []
            }
        ]
    }


def load_external_snapshot(snapshot_path: Path) -> List[Dict[str, Any]]:
    """
    Placeholder loader for an external UESP/ESO snapshot.

    For now, this function only verifies that the path exists (if provided) and
    returns an empty list. In a future iteration, this will:

      - Read one or more CSV/TSV/JSON files from snapshot_path.
      - Map raw columns onto the conceptual external fields described in
        Appendix B (setId, setName, setType, etc.).
      - Return a list of normalized external row dicts for build_set_record().
    """
    if not snapshot_path.exists():
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


def write_sets_json(sets: List[Dict[str, Any]]) -> Path:
    """
    Write data/sets.json using the canonical v1 container shape.

    This overwrites any existing data/sets.json file, in line with the
    full-file replacement rule for canonical JSON. The caller is responsible
    for backing up data/ and running validators afterward.
    """
    ensure_data_dir()
    target_path = DATA_DIR / "sets.json"
    container = {
        "sets": sets
    }
    with target_path.open("w", encoding="utf-8") as f:
        json.dump(container, f, indent=2, ensure_ascii=False)
    return target_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Import ESO/UESP set data into data/sets.json "
            "according to the v1 Data Model and Sets Import Mapping."
        )
    )
    parser.add_argument(
        "--snapshot-path",
        type=str,
        required=True,
        help=(
            "Path to a frozen external snapshot for sets "
            "(e.g., raw-data/eso-api-XXXX/sets/). "
            "In this stub version, it is only checked for existence."
        ),
    )
    parser.add_argument(
        "--include-placeholder-example",
        action="store_true",
        help=(
            "If set, writes a single example placeholder set record to help "
            "verify schema wiring. Without this flag, writes an empty sets list."
        ),
    )

    args = parser.parse_args()
    snapshot_path = Path(args.snapshot_path)

    external_rows: List[Dict[str, Any]] = load_external_snapshot(snapshot_path)

    sets: List[Dict[str, Any]] = []
    if args.include_placeholder_example:
        # Add one placeholder set to confirm shape and wiring.
        sets.append(build_set_record({}))

    # Future implementation:
    # for row in external_rows:
    #     sets.append(build_set_record(row))

    target_path = write_sets_json(sets)
    print(
        json.dumps(
            {
                "status": "OK",
                "message": "Stub import completed; sets.json written.",
                "sets_count": len(sets),
                "target_path": str(target_path),
                "mode": "placeholder" if args.include_placeholder_example else "empty",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
