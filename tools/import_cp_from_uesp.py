"""
tools/import_cp_from_uesp.py

Stub importer for external ESO/UESP Champion Point star data into a
preview CP stars JSON under raw-imports/, aligned to
docs/ESO-Build-Engine-Data-Model-v1.md Appendix C:
CP Stars Import Mapping → data/cp-stars.json.

This version does NOT parse real UESP exports yet. It:

- Accepts a required --snapshot-path argument (for future use).
- Writes a schema-correct preview JSON file under raw-imports/
  with either:
  - an empty "cp_stars" array, or
  - a single placeholder CP star record when
    --include-placeholder-example is set.
- Never writes to data/cp-stars.json.

Once external snapshots are available and the detailed mapping
spec is finalized, the placeholder logic in build_cp_star_record()
and the main() loop should be replaced with real transforms, and
a separate promotion step should copy reviewed preview JSON into
data/cp-stars.json.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

# Repository paths (mirrors validate_build.py layout).
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = REPO_ROOT / "docs"
RAW_IMPORTS_DIR = REPO_ROOT / "raw-imports"


def ensure_raw_imports_dir() -> None:
    """
    Ensure the raw-imports/ directory exists.

    Per External Data Scope, import tools must write only to
    raw-imports/ during development and preview phases, never
    directly to data/*.json.
    """
    RAW_IMPORTS_DIR.mkdir(parents=True, exist_ok=True)


def build_empty_cp_container() -> Dict[str, Any]:
    """
    Return an empty CP stars container matching the v1 Data Model shape.

    See:
      - docs/ESO-Build-Engine-Data-Model-v1.md
      - CP stars (data/cp-stars.json) schema
      - Appendix C: CP Stars Import Mapping → data/cp-stars.json
    """
    return {
        "meta": {
            "source": "tools/import_cp_from_uesp.py",
            "mode": "preview",
            "note": (
                "This file is a preview of normalized CP star data. "
                "Promote to data/cp-stars.json only after validation and review."
            ),
        },
        "cp_stars": [],
    }


def build_cp_star_record(external_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder transform from a single external CP star row to the canonical
    CP star object defined in the v1 Data Model.

    This is a stub; it documents the target fields but does not use the input.

    Expected external concepts (per Appendix C, summarized):
      - cpId
      - cpName
      - cpTree
      - slotType
      - cpTooltipRaw
      - cpTags (optional)
      - cpEffectIdentifiers (optional)

    Target fields (per v1 Data Model + Appendix C):
      - id (internal cp.* ID)
      - name
      - tree
      - slot_type
      - tooltip_raw
      - effects[]
      - optional external_ids.*
    """
    # NOTE: This function intentionally returns a fixed, minimal example
    # shape as a reference. Real logic will:
    # - Generate deterministic CP IDs from cpId/cpName.
    # - Normalize cpTree into the warfare/fitness/craft enum.
    # - Map slotType into slot_type (e.g., "slottable").
    # - Populate effects[] with real effect IDs from data/effects.json.
    return {
        "id": "cp.example_placeholder",
        "name": "Example Placeholder CP Star",
        "tree": "warfare",
        "slot_type": "slottable",
        "tooltip_raw": (
            "Placeholder CP star created by tools/import_cp_from_uesp.py stub. "
            "Replace this record once real import logic is implemented."
        ),
        "effects": [],
        # external_ids can be added later (uesp_cp_id, etc.) when needed.
    }


def load_external_snapshot(snapshot_path: Path) -> List[Dict[str, Any]]:
    """
    Placeholder loader for an external UESP/ESO CP snapshot.

    For now, this function only verifies that the path exists (if provided) and
    returns an empty list. In a future iteration, this will:

      - Read one or more CSV/TSV/JSON files from snapshot_path.
      - Map raw columns onto the conceptual external fields described in
        Appendix C (cpId, cpName, cpTree, etc.).
      - Return a list of normalized external row dicts for build_cp_star_record().
    """
    if not snapshot_path.exists():
        print(
            json.dumps(
                {
                    "status": "WARN",
                    "message": f"Snapshot path not found (stub mode): {snapshot_path}",
                }
            )
        )
        return []

    # Future implementation: parse snapshot_path contents.
    return []


def write_cp_stars_preview(cp_stars: List[Dict[str, Any]]) -> Path:
    """
    Write a preview cp-stars JSON under raw-imports/ using the canonical v1
    container shape, plus a small meta block.

    This DOES NOT write to data/cp-stars.json. Promotion into data/cp-stars.json
    must be a separate, manual step after validation.
    """
    ensure_raw_imports_dir()
    target_path = RAW_IMPORTS_DIR / "cp-stars.import-preview.json"
    container = build_empty_cp_container()
    container["cp_stars"] = cp_stars

    with target_path.open("w", encoding="utf-8") as f:
        json.dump(container, f, indent=2, ensure_ascii=False)

    return target_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Import ESO/UESP CP star data into a preview JSON under raw-imports/, "
            "according to the v1 Data Model and CP Stars Import Mapping."
        )
    )
    parser.add_argument(
        "--snapshot-path",
        type=str,
        required=True,
        help=(
            "Path to a frozen external snapshot for CP stars "
            "(e.g., raw-data/eso-api-XXXX/cp/). "
            "In this stub version, it is only checked for existence."
        ),
    )
    parser.add_argument(
        "--include-placeholder-example",
        action="store_true",
        help=(
            "If set, writes a single example placeholder CP star record to help "
            "verify schema wiring. Without this flag, writes an empty cp_stars list."
        ),
    )

    args = parser.parse_args()
    snapshot_path = Path(args.snapshot_path)

    external_rows: List[Dict[str, Any]] = load_external_snapshot(snapshot_path)

    cp_stars: List[Dict[str, Any]] = []
    if args.include_placeholder_example:
        # Add one placeholder CP star to confirm shape and wiring.
        cp_stars.append(build_cp_star_record({}))

    # Future implementation:
    # for row in external_rows:
    #     cp_stars.append(build_cp_star_record(row))

    target_path = write_cp_stars_preview(cp_stars)
    print(
        json.dumps(
            {
                "status": "OK",
                "message": "Stub import completed; CP stars preview JSON written.",
                "cp_stars_count": len(cp_stars),
                "target_path": str(target_path),
                "mode": "placeholder" if args.include_placeholder_example else "empty",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
