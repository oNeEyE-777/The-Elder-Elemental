import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
BUILDS_DIR = REPO_ROOT / "builds"


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "__error__": f"File not found: {path}"
        }
    except json.JSONDecodeError as e:
        return {
            "__error__": f"Invalid JSON in {path}: {e}"
        }


def index_by_id(items: List[dict], id_key: str = "id") -> Dict[str, dict]:
    return {item[id_key]: item for item in items if isinstance(item, dict) and id_key in item}


def validate_build_structure(build: dict) -> List[str]:
    """
    Structural checks only: bars, gear slots, cp_slotted trees and sizes.
    Matches the Global Rules doc for a single build JSON.[file:3]
    """
    errors: List[str] = []

    # Top-level keys
    required_top = ["id", "name", "bars", "gear", "cp_slotted"]
    for key in required_top:
        if key not in build:
            errors.append(f"Missing top-level key: {key}")

    # Bars
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

            required_slots = {1, 2, 3, 4, 5, "ULT"}
            if required_slots - seen_slots:
                missing = ", ".join(map(str, sorted(required_slots - seen_slots, key=str)))
                errors.append(f"Bar '{bar_name}' missing required slots: {missing}")

    # Gear
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
        mythic_count = 0

        for item in gear:
            if not isinstance(item, dict):
                errors.append(f"gear contains non-object item: {item!r}")
                continue
            slot_name = item.get("slot")
            if slot_name is None:
                errors.append("gear item missing 'slot' field")
                continue
            present_slots.add(slot_name)

            # Mythic constraint: at most one mythic set across all gear
            set_id = item.get("set_id")
            if isinstance(set_id, str) and set_id.startswith("set.") and "mythic" in (item.get("type") or ""):
                mythic_count += 1

            # Armor weight validity (for armor slots)
            if slot_name in {"head", "shoulder", "chest", "hands", "waist", "legs", "feet"}:
                weight = item.get("weight")
                if weight is not None and weight not in {"light", "medium", "heavy"}:
                    errors.append(
                        f"Gear slot '{slot_name}' has invalid weight '{weight}', "
                        "expected 'light'|'medium'|'heavy' or null"
                    )

        missing_gear = required_gear_slots - present_slots
        extra_gear = present_slots - required_gear_slots
        if missing_gear:
            missing_str = ", ".join(sorted(missing_gear))
            errors.append(f"gear missing required slots: {missing_str}")
        if extra_gear:
            extra_str = ", ".join(sorted(extra_gear))
            errors.append(f"gear has unexpected slots: {extra_str}")
        if mythic_count > 1:
            errors.append("More than one mythic set detected in gear (max 1 allowed)")

    # CP layout
    cp_slotted = build.get("cp_slotted")
    if not isinstance(cp_slotted, dict):
        errors.append("cp_slotted must be an object with warfare/fitness/craft arrays")
    else:
        required_trees = {"warfare", "fitness", "craft"}
        present_trees = set(cp_slotted.keys())
        missing_trees = required_trees - present_trees
        extra_trees = present_trees - required_trees
        if missing_trees:
            errors.append(f"cp_slotted missing trees: {', '.join(sorted(missing_trees))}")
        if extra_trees:
            errors.append(f"cp_slotted has unexpected trees: {', '.join(sorted(extra_trees))}")

        for tree in ["warfare", "fitness", "craft"]:
            stars = cp_slotted.get(tree, [])
            if not isinstance(stars, list):
                errors.append(f"cp_slotted.{tree} must be a list (up to 4 entries)")
                continue
            if len(stars) > 4:
                errors.append(f"cp_slotted.{tree} has more than 4 entries")

    return errors


def validate_references(build: dict, skills_idx: dict, sets_idx: dict, cp_idx: dict) -> List[str]:
    """
    Reference checks: skill_id, set_id, cp IDs must exist in their data tables.
    Also enforce CP slottable constraint and duplicates per tree.[file:2][file:3]
    """
    errors: List[str] = []

    # Bars -> skills
    bars = build.get("bars", {})
    for bar_name, bar_slots in bars.items():
        if not isinstance(bar_slots, list):
            continue
        for entry in bar_slots:
            if not isinstance(entry, dict):
                continue
            skill_id = entry.get("skill_id")
            if skill_id is None:
                continue
            if not isinstance(skill_id, str):
                errors.append(f"Bar '{bar_name}' slot {entry.get('slot')!r} has non-string skill_id: {skill_id!r}")
                continue
            if skill_id not in skills_idx:
                errors.append(
                    f"Bar '{bar_name}' slot {entry.get('slot')!r} references unknown skill_id: {skill_id}"
                )

    # Gear -> sets
    gear = build.get("gear", [])
    for item in gear:
        if not isinstance(item, dict):
            continue
        slot_name = item.get("slot")
        set_id = item.get("set_id")
        if set_id is None:
            continue
        if not isinstance(set_id, str):
            errors.append(f"Gear slot '{slot_name}' has non-string set_id: {set_id!r}")
            continue
        if set_id not in sets_idx:
            errors.append(f"Gear slot '{slot_name}' references unknown set_id: {set_id}")

    # CP -> cp_stars (slottable only, no duplicates per tree)
    cp_slotted = build.get("cp_slotted", {})
    for tree_name, star_ids in cp_slotted.items():
        if not isinstance(star_ids, list):
            continue
        seen_ids = set()
        for idx, star_id in enumerate(star_ids):
            if star_id is None:
                continue
            if not isinstance(star_id, str):
                errors.append(f"CP tree '{tree_name}' index {idx} has non-string id: {star_id!r}")
                continue
            star = cp_idx.get(star_id)
            if not star:
                errors.append(f"CP tree '{tree_name}' references unknown cp_star id: {star_id}")
                continue
            slot_type = star.get("slot_type")
            if slot_type != "slottable":
                errors.append(
                    f"CP tree '{tree_name}' id '{star_id}' has slot_type '{slot_type}', "
                    "only 'slottable' may appear in cp_slotted"
                )
                continue
            if star_id in seen_ids:
                errors.append(f"CP tree '{tree_name}' has duplicate slotted cp_star id: {star_id}")
            seen_ids.add(star_id)

    return errors


def validate_build(build_path: Path) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate a single build JSON file against data and global rules.[file:3][file:4]
    """
    skills_data = load_json(DATA_DIR / "skills.json")
    effects_data = load_json(DATA_DIR / "effects.json")
    sets_data = load_json(DATA_DIR / "sets.json")
    cp_data = load_json(DATA_DIR / "cp-stars.json")

    # Handle data load errors
    data_errors: List[str] = []
    for label, data in [
        ("skills.json", skills_data),
        ("effects.json", effects_data),
        ("sets.json", sets_data),
        ("cp-stars.json", cp_data),
    ]:
        if isinstance(data, dict) and "__error__" in data:
            data_errors.append(f"{label}: {data['__error__']}")

    if data_errors:
        return False, {
            "build_path": str(build_path),
            "status": "ERROR",
            "error_count": len(data_errors),
            "errors": data_errors,
        }

    skills_idx = index_by_id(skills_data.get("skills", []))
    sets_idx = index_by_id(sets_data.get("sets", []))
    cp_idx = index_by_id(cp_data.get("cp_stars", []))

    build = load_json(build_path)
    if isinstance(build, dict) and "__error__" in build:
        return False, {
            "build_path": str(build_path),
            "status": "ERROR",
            "error_count": 1,
            "errors": [build["__error__"]],
        }

    if not isinstance(build, dict):
        return False, {
            "build_path": str(build_path),
            "status": "ERROR",
            "error_count": 1,
            "errors": [f"{build_path}: expected JSON object at root"],
        }

    structure_errors = validate_build_structure(build)
    reference_errors = validate_references(build, skills_idx, sets_idx, cp_idx)

    all_errors = structure_errors + reference_errors

    result = {
        "build_id": build.get("id"),
        "build_name": build.get("name"),
        "build_path": str(build_path),
        "status": "OK" if not all_errors else "ERROR",
        "error_count": len(all_errors),
        "errors": all_errors,
    }

    return not bool(all_errors), result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate an ESO build JSON against data and global rules."
    )
    parser.add_argument(
        "build_path",
        nargs="?",
        default=str(BUILDS_DIR / "permafrost-marshal.json"),
        help="Path to build JSON (default: builds/permafrost-marshal.json)",
    )
    args = parser.parse_args()

    build_path = Path(args.build_path)

    valid, result = validate_build(build_path)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if not valid:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
