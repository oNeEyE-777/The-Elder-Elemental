import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
BUILDS_DIR = REPO_ROOT / "builds"


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def index_by_id(items, id_key: str = "id"):
    return {item[id_key]: item for item in items if isinstance(item, dict) and id_key in item}


def validate_build_structure(build: dict) -> list[str]:
    errors: list[str] = []

    # Top-level keys (Phase 1: minimal but consistent with v1 model)
    required_top = ["id", "name", "bars", "gear", "cp_slotted"]
    for key in required_top:
        if key not in build:
            errors.append(f"Missing top-level key: {key}")

    # Bars: front/back, slots 1–5 + ULT as array objects
    bars = build.get("bars")
    if not isinstance(bars, dict):
        errors.append("bars must be an object with 'front' and 'back' arrays")
    else:
        for bar_name in ["front", "back"]:
            if bar_name not in bars:
                errors.append(f"Missing bar: {bar_name}")
                continue

            bar_slots = bars[bar_name]
            if not isinstance(bar_slots, list):
                errors.append(f"Bar '{bar_name}' must be a list of slot objects")
                continue

            seen_slots = set()
            for entry in bar_slots:
                if not isinstance(entry, dict):
                    errors.append(f"Bar '{bar_name}' contains non-object slot entry: {entry!r}")
                    continue
                slot = entry.get("slot")
                if slot not in [1, 2, 3, 4, 5, "ULT"]:
                    errors.append(f"Bar '{bar_name}' has invalid slot value: {slot!r}")
                if slot in seen_slots:
                    errors.append(f"Bar '{bar_name}' has duplicate slot: {slot!r}")
                seen_slots.add(slot)

            # Ensure at least the canonical slots exist
            required_slots = {1, 2, 3, 4, 5, "ULT"}
            if required_slots - seen_slots:
                missing = ", ".join(map(str, sorted(required_slots - seen_slots, key=str)))
                errors.append(f"Bar '{bar_name}' missing required slots: {missing}")

    # Gear: must be a list with the 12 canonical slots
    gear = build.get("gear")
    if not isinstance(gear, list):
        errors.append("gear must be a list of gear slot records")
    else:
        required_gear_slots = {
            "head",
            "shoulder",
            "chest",
            "hands",
            "waist",
            "legs",
            "feet",
            "neck",
            "ring1",
            "ring2",
            "front_weapon",
            "back_weapon",
        }
        present_slots = set()
        for item in gear:
            if not isinstance(item, dict):
                errors.append(f"gear contains non-object item: {item!r}")
                continue
            slot_name = item.get("slot")
            if slot_name is None:
                errors.append("gear item missing 'slot' field")
                continue
            present_slots.add(slot_name)

        missing_gear = required_gear_slots - present_slots
        extra_gear = present_slots - required_gear_slots
        if missing_gear:
            missing_str = ", ".join(sorted(missing_gear))
            errors.append(f"gear missing required slots: {missing_str}")
        if extra_gear:
            extra_str = ", ".join(sorted(extra_gear))
            errors.append(f"gear has unexpected slots: {extra_str}")

    # CP layout: cp_slotted with warfare/fitness/craft arrays of up to 4 entries
    cp_slotted = build.get("cp_slotted")
    if not isinstance(cp_slotted, dict):
        errors.append("cp_slotted must be an object with warfare/fitness/craft arrays")
    else:
        for tree in ["warfare", "fitness", "craft"]:
            if tree not in cp_slotted:
                errors.append(f"cp_slotted missing tree: {tree}")
                continue
            stars = cp_slotted[tree]
            if not isinstance(stars, list):
                errors.append(f"cp_slotted.{tree} must be a list (up to 4 entries)")
                continue
            if len(stars) > 4:
                errors.append(f"cp_slotted.{tree} has more than 4 entries")

    return errors


def validate_references(build: dict, skills_idx: dict, sets_idx: dict, cp_idx: dict) -> list[str]:
    errors: list[str] = []

    # Bars -> skills
    bars = build.get("bars", {})
    for bar_name, bar_slots in bars.items():
        if not isinstance(bar_slots, list):
            continue
        for entry in bar_s
