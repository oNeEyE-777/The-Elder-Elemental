#!/usr/bin/env python3
"""
tools/import_sets_from_uesp.py

Phase 1 "real" importer for external ESO/UESP-like set data into a preview
sets JSON under raw-imports/, aligned to
docs/ESO-Build-Engine-Data-Model-v1.md Appendix B:
Sets Import Mapping → data/sets.json.

This version still targets PREVIEW USE ONLY. It:

- Accepts a required --snapshot-path argument.
- Expects a simple JSON snapshot at that path with shape:

    {
      "sets": [
        {
          "setId": 1234,
          "setName": "Mark of the Pariah",
          "setType": "armor",
          "setSource": "overland",
          "setTags": ["pvp", "tank"],
          "bonusRows": [
            {
              "piecesRequired": 2,
              "bonusTooltipRaw": "Adds 1206 Maximum Health.",
              "bonusEffectIdentifiers": []
            },
            {
              "piecesRequired": 5,
              "bonusTooltipRaw": "Increases your Physical and Spell Resistance...",
              "bonusEffectIdentifiers": []
            }
          ]
        },
        ...
      ]
    }

- Normalizes each external row into a canonical v1 set object with:
  - id = "set." + normalized snake_case setName (or setId-based fallback)
  - name, type, source, tags[]
  - set_id (numeric external ID), external_ids.eso_sets_api
  - bonuses[*].pieces, bonuses[*].tooltip_raw, bonuses[*].effects = []

- Writes schema-correct preview JSON to:
    raw-imports/sets.import-preview.json

- Never writes to data/sets.json.

This is intentionally conservative and does NOT attempt to derive effects[]
from tooltips yet. It gives you a realistic, multi-record preview file that
validate_data_integrity.py can later validate once promoted into data/sets.json.
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


def build_empty_sets_container() -> Dict[str, Any]:
    """
    Return an empty sets container matching the v1 Data Model shape.

    See:
      - docs/ESO-Build-Engine-Data-Model-v1.md
      - Appendix B: Sets Import Mapping → data/sets.json
    """
    return {
        "meta": {
            "source": "tools/import_sets_from_uesp.py",
            "mode": "preview",
            "note": (
                "This file is a preview of normalized set data. "
                "Promote to data/sets.json only after validation and review."
            ),
        },
        "sets": [],
    }


# ---------- Normalization helpers ----------


_SNAKE_RE = re.compile(r"[^a-z0-9]+")


def to_snake_case(value: str) -> str:
    """
    Convert a human-ish or CamelCase name into lowercase snake_case.

    Examples:
      "Mark of the Pariah" -> "mark_of_the_pariah"
      "RingOfTheWildHunt" -> "ring_of_the_wild_hunt"
    """
    value = value.strip().lower()
    value = _SNAKE_RE.sub("_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unnamed"


def normalize_set_id(set_name: str, set_id: Any) -> str:
    """
    Build a canonical set.* ID.

    Prefer setName when available; fall back to setId-based IDs for
    determinism if the name field is unusable.
    """
    if isinstance(set_name, str) and set_name.strip():
        base = to_snake_case(set_name)
        return f"set.{base}"

    if isinstance(set_id, (int, float)) and set_id:
        return f"set.id_{int(set_id)}"

    return "set.unnamed_placeholder"


def normalize_set_type(set_type: Any) -> str:
    """
    Normalize setType into a simple enum.
    """
    if not isinstance(set_type, str):
        return "unknown"

    st = set_type.strip().lower()
    if st in ("armor", "weapon", "jewelry"):
        return st
    return "unknown"


def normalize_set_source(set_source: Any) -> str:
    """
    Normalize setSource into a simple enum-like string.
    """
    if not isinstance(set_source, str):
        return "unknown"

    ss = set_source.strip().lower()
    # Keep as snake_case text without overfitting.
    return to_snake_case(ss)


def normalize_tags(set_tags: Any) -> List[str]:
    """
    Normalize setTags into a list of simple snake_case strings.
    """
    if not isinstance(set_tags, list):
        return []

    tags: List[str] = []
    for tag in set_tags:
        if not isinstance(tag, str):
            continue
        tags.append(to_snake_case(tag))
    return tags


# ---------- Core transform ----------


def build_set_record(external_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a single external set row into the canonical v1 set object.

    Expected external fields (per the simple JSON snapshot contract):
      - setId
      - setName
      - setType
      - setSource
      - setTags (array of strings)
      - bonusRows (array of objects):
        - piecesRequired
        - bonusTooltipRaw
        - bonusEffectIdentifiers (optional, not used yet)
    """
    set_id_external = external_row.get("setId")
    set_name = external_row.get("setName") or ""
    set_type_raw = external_row.get("setType")
    set_source_raw = external_row.get("setSource")
    set_tags_raw = external_row.get("setTags", [])
    bonus_rows = external_row.get("bonusRows", [])

    cid = normalize_set_id(set_name, set_id_external)
    ctype = normalize_set_type(set_type_raw)
    csource = normalize_set_source(set_source_raw)
    ctags = normalize_tags(set_tags_raw)

    bonuses: List[Dict[str, Any]] = []
    if isinstance(bonus_rows, list):
        for row in bonus_rows:
            if not isinstance(row, dict):
                continue
            pieces_required = row.get("piecesRequired")
            tooltip_raw = row.get("bonusTooltipRaw") or ""
            # For now, we ignore bonusEffectIdentifiers; effects[] stays empty.
            if not isinstance(pieces_required, int):
                # Skip malformed rows; they would not be valid for v1 anyway.
                continue
            bonuses.append(
                {
                    "pieces": pieces_required,
                    "tooltip_raw": tooltip_raw,
                    "effects": [],
                }
            )

    return {
        "id": cid,
        "name": set_name or (f"Set {set_id_external}" if set_id_external is not None else "Unnamed Set"),
        "type": ctype,
        "source": csource,
        "tags": ctags,
        # External numeric ID, kept for traceability.
        "set_id": set_id_external,
        "external_ids": {
            "eso_sets_api": {
                "setId": set_id_external,
            }
        },
        "bonuses": bonuses,
    }


# ---------- Snapshot loading ----------


def load_external_snapshot(snapshot_path: Path) -> List[Dict[str, Any]]:
    """
    Load an external ESO/UESP-like snapshot from a simple JSON file.

    Expected shape:
      { "sets": [ { ...external set fields... }, ... ] }
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

    sets_payload = payload.get("sets", [])
    if not isinstance(sets_payload, list):
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "message": "Snapshot JSON 'sets' field is not a list.",
                }
            )
        )
        return []

    normalized_rows: List[Dict[str, Any]] = []
    for row in sets_payload:
        if isinstance(row, dict):
            normalized_rows.append(row)

    return normalized_rows


# ---------- Preview writer ----------


def write_sets_preview(sets: List[Dict[str, Any]]) -> Path:
    """
    Write a preview sets JSON under raw-imports/ using the canonical v1
    container shape, plus a small meta block.

    This DOES NOT write to data/sets.json. Promotion into data/sets.json
    must be a separate, manual step after validation.
    """
    ensure_raw_imports_dir()
    target_path = RAW_IMPORTS_DIR / "sets.import-preview.json"
    container = build_empty_sets_container()
    container["sets"] = sets

    with target_path.open("w", encoding="utf-8") as f:
        json.dump(container, f, indent=2, ensure_ascii=False)

    return target_path


# ---------- CLI ----------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Import ESO/UESP-like set data into a preview JSON under raw-imports/, "
            "according to the v1 Data Model and Sets Import Mapping."
        )
    )
    parser.add_argument(
        "--snapshot-path",
        type=str,
        required=True,
        help=(
            "Path to a frozen external snapshot for sets "
            "(JSON file with a top-level 'sets' array)."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Optional limit on number of sets to import (for quick previews). "
            "If omitted, imports all sets in the snapshot."
        ),
    )

    args = parser.parse_args()
    snapshot_path = Path(args.snapshot_path)

    external_rows: List[Dict[str, Any]] = load_external_snapshot(snapshot_path)

    sets: List[Dict[str, Any]] = []
    for idx, row in enumerate(external_rows):
        if args.limit is not None and idx >= args.limit:
            break
        sets.append(build_set_record(row))

    target_path = write_sets_preview(sets)
    print(
        json.dumps(
            {
                "status": "OK",
                "message": "Sets import preview generated.",
                "sets_count": len(sets),
                "target_path": str(target_path),
                "mode": "preview",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
