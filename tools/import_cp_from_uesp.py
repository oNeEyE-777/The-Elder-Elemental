#!/usr/bin/env python3
"""
tools/import_cp_from_uesp.py

Phase 1 "real" importer for external ESO/UESP-like Champion Point star data
into a preview CP stars JSON under raw-imports/, aligned to
docs/ESO-Build-Engine-Data-Model-v1.md Appendix C:
CP Stars Import Mapping → data/cp-stars.json.

This version still targets PREVIEW USE ONLY. It:

- Accepts a required --snapshot-path argument.
- Expects a simple JSON snapshot at that path with shape:

    {
      "cp_stars": [
        {
          "cpId": 1,
          "cpName": "Celerity",
          "cpTree": "fitness",
          "slotType": "slottable",
          "cpTooltipRaw": "Increases your Movement Speed by 10%.",
          "cpTags": ["speed"],
          "cpEffectIdentifiers": []
        },
        ...
      ]
    }

- Normalizes each external row into a canonical v1 CP star object with:
  - id = "cp." + normalized snake_case cpName (or cpId-based fallback)
  - name, tree (warfare/fitness/craft), slot_type, tooltip_raw
  - effects = [] (effect IDs will be added later)
  - optional external_ids.uesp_cp

- Writes schema-correct preview JSON to:
    raw-imports/cp-stars.import-preview.json

- Never writes to data/cp-stars.json.

This is intentionally conservative and does NOT attempt to derive effects[]
from tooltips yet. It gives you a realistic preview file that
validate_data_integrity.py can later validate once promoted into data/cp-stars.json.
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


# ---------- Normalization helpers ----------


_SNAKE_RE = re.compile(r"[^a-z0-9]+")


def to_snake_case(value: str) -> str:
    """
    Convert a human-ish or CamelCase name into lowercase snake_case.

    Examples:
      "Steed's Blessing" -> "steed_s_blessing"
      "GiftedRider" -> "gifted_rider"
    """
    value = value.strip().lower()
    value = _SNAKE_RE.sub("_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unnamed"


def normalize_cp_id(cp_name: str, cp_id: Any) -> str:
    """
    Build a canonical cp.* ID.

    Prefer cpName when available; fall back to cpId-based IDs for determinism.
    """
    if isinstance(cp_name, str) and cp_name.strip():
        base = to_snake_case(cp_name)
        return f"cp.{base}"

    if isinstance(cp_id, (int, float)) and cp_id:
        return f"cp.id_{int(cp_id)}"

    return "cp.unnamed_placeholder"


def normalize_tree(cp_tree: Any) -> str:
    """
    Normalize cpTree into warfare/fitness/craft (or 'unknown').
    """
    if not isinstance(cp_tree, str):
        return "unknown"

    t = cp_tree.strip().lower()
    if t in ("warfare", "fitness", "craft"):
        return t
    return "unknown"


def normalize_slot_type(slot_type: Any) -> str:
    """
    Normalize slotType into a small enum.
    """
    if not isinstance(slot_type, str):
        return "unknown"

    st = slot_type.strip().lower()
    if st in ("slottable", "passive"):
        return st
    return "unknown"


# ---------- Core transform ----------


def build_cp_star_record(external_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a single external CP star row into the canonical v1 CP star object.

    Expected external fields (simple JSON snapshot contract):
      - cpId
      - cpName
      - cpTree
      - slotType
      - cpTooltipRaw
      - cpTags (optional)
      - cpEffectIdentifiers (optional)
    """
    cp_id_external = external_row.get("cpId")
    cp_name = external_row.get("cpName") or ""
    cp_tree_raw = external_row.get("cpTree")
    slot_type_raw = external_row.get("slotType")
    tooltip_raw = external_row.get("cpTooltipRaw") or ""
    cp_tags = external_row.get("cpTags", [])

    cid = normalize_cp_id(cp_name, cp_id_external)
    tree = normalize_tree(cp_tree_raw)
    slot_type = normalize_slot_type(slot_type_raw)

    return {
        "id": cid,
        "name": cp_name or (f"CP {cp_id_external}" if cp_id_external is not None else "Unnamed CP Star"),
        "tree": tree,
        "slot_type": slot_type,
        "tooltip_raw": tooltip_raw,
        # Effects mapping will be introduced in a later phase; for now we keep
        # an empty list so validate_data_integrity.py can still enforce shape.
        "effects": [],
        "external_ids": {
            "uesp_cp": {
                "cpId": cp_id_external,
            }
        },
    }


# ---------- Snapshot loading ----------


def load_external_snapshot(snapshot_path: Path) -> List[Dict[str, Any]]:
    """
    Load an external ESO/UESP-like CP snapshot from a simple JSON file.

    Expected shape:
      { "cp_stars": [ { ...external cp fields... }, ... ] }
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

    cp_payload = payload.get("cp_stars", [])
    if not isinstance(cp_payload, list):
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "message": "Snapshot JSON 'cp_stars' field is not a list.",
                }
            )
        )
        return []

    normalized_rows: List[Dict[str, Any]] = []
    for row in cp_payload:
        if isinstance(row, dict):
            normalized_rows.append(row)

    return normalized_rows


# ---------- Preview writer ----------


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


# ---------- CLI ----------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Import ESO/UESP-like CP star data into a preview JSON under raw-imports/, "
            "according to the v1 Data Model and CP Stars Import Mapping."
        )
    )
    parser.add_argument(
        "--snapshot-path",
        type=str,
        required=True,
        help=(
            "Path to a frozen external snapshot for CP stars "
            "(JSON file with a top-level 'cp_stars' array)."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Optional limit on number of CP stars to import (for quick previews). "
            "If omitted, imports all CP stars in the snapshot."
        ),
    )

    args = parser.parse_args()
    snapshot_path = Path(args.snapshot_path)

    external_rows: List[Dict[str, Any]] = load_external_snapshot(snapshot_path)

    cp_stars: List[Dict[str, Any]] = []
    for idx, row in enumerate(external_rows):
        if args.limit is not None and idx >= args.limit:
            break
        cp_stars.append(build_cp_star_record(row))

    target_path = write_cp_stars_preview(cp_stars)
    print(
        json.dumps(
            {
                "status": "OK",
                "message": "CP stars import preview generated.",
                "cp_stars_count": len(cp_stars),
                "target_path": str(target_path),
                "mode": "preview",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
