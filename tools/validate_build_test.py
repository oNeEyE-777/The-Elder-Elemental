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
        for entry in bar_slots:
            if not isinstance(entry, dict):
                continue
            skill_id = entry.get("skill_id")
            if skill_id is None:
                # null is allowed; it's just an empty slot
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
            # For test-dummy, null set_id is allowed for empty slots
            continue
        if not isinstance(set_id, str):
            errors.append(f"Gear slot '{slot_name}' has non-string set_id: {set_id!r}")
            continue
        if set_id not in sets_idx:
            errors.append(f"Gear slot '{slot_name}' references unknown set_id: {set_id}")

    # CP -> cp_stars (slottable only)
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
            if star_id not in cp_idx:
                errors.append(f"CP tree '{tree_name}' references unknown cp_star id: {star_id}")
                continue
            if star_id in seen_ids:
                errors.append(f"CP tree '{tree_name}' has duplicate slotted cp_star id: {star_id}")
            seen_ids.add(star_id)

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate the test-dummy ESO build JSON against Phase 1 data files."
    )
    parser.add_argument(
        "build_path",
        nargs="?",
        default=str(BUILDS_DIR / "test-dummy.json"),
        help="Path to build JSON (default: builds/test-dummy.json)",
    )
    args = parser.parse_args()

    build_path = Path(args.build_path)

    skills_data = load_json(DATA_DIR / "skills.json")
    effects_data = load_json(DATA_DIR / "effects.json")
    sets_data = load_json(DATA_DIR / "sets.json")
    cp_data = load_json(DATA_DIR / "cp-stars.json")

    skills_idx = index_by_id(skills_data.get("skills", []))
    sets_idx = index_by_id(sets_data.get("sets", []))
    cp_idx = index_by_id(cp_data.get("cp_stars", []))

    build = load_json(build_path)

    structure_errors = validate_build_structure(build)
    reference_errors = validate_references(build, skills_idx, sets_idx, cp_idx)

    all_errors = structure_errors + reference_errors

    result = {
        "build_id": build.get("id"),
        "build_name": build.get("name"),
        "status": "OK" if not all_errors else "ERROR",
        "error_count": len(all_errors),
        "errors": all_errors,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if all_errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
