import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
BUILDS_DIR = REPO_ROOT / "builds"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_ids(items: List[Dict[str, Any]], key: str) -> List[str]:
    return [item[key] for item in items if key in item]


def validate_build_structure(build: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Structural checks only, matching docs/ESO-Build-Engine-Global-Rules.md v1.
    """
    errors: List[Dict[str, Any]] = []

    # Basic identity
    if "id" not in build:
        errors.append({"field": "id", "message": "Missing build.id"})
    if "name" not in build:
        errors.append({"field": "name", "message": "Missing build.name"})

    # Bars structure
    bars = build.get("bars")
    if bars is None:
        errors.append({"field": "bars", "message": "Missing build.bars"})
    else:
        for bar_name in ("front", "back"):
            if bar_name not in bars:
                errors.append(
                    {"field": f"bars.{bar_name}", "message": f"Missing {bar_name} bar"}
                )
                continue

            bar_slots = bars[bar_name]
            if not isinstance(bar_slots, list):
                errors.append(
                    {
                        "field": f"bars.{bar_name}",
                        "message": f"Expected list of slots for bar '{bar_name}'",
                    }
                )
                continue

            # Allowed slots are "1"–"5" and "ULT" as strings.
            seen_slots = set()
            for idx, slot in enumerate(bar_slots):
                field_prefix = f"bars.{bar_name}[{idx}]"

                # Slot presence and type
                raw_slot = slot.get("slot")
                if raw_slot is None:
                    errors.append(
                        {
                            "field": f"{field_prefix}.slot",
                            "message": "Missing slot on bar entry",
                        }
                    )
                    continue

                # Normalize to string, since v1 uses string slots
                slot_str = str(raw_slot)
                if slot_str not in {"1", "2", "3", "4", "5", "ULT"}:
                    errors.append(
                        {
                            "field": f"{field_prefix}.slot",
                            "message": f"Invalid slot '{slot_str}', expected '1'-'5' or 'ULT'",
                        }
                    )
                if slot_str in seen_slots:
                    errors.append(
                        {
                            "field": f"{field_prefix}.slot",
                            "message": f"Duplicate slot '{slot_str}' on bar '{bar_name}'",
                        }
                    )
                seen_slots.add(slot_str)

                # Skill ID presence (v1: skill_id)
                if "skill_id" not in slot:
                    errors.append(
                        {
                            "field": f"{field_prefix}.skill_id",
                            "message": "Missing skill_id on bar slot",
                        }
                    )

    # Gear structure
    gear = build.get("gear")
    if gear is None:
        errors.append({"field": "gear", "message": "Missing build.gear"})
    else:
        if not isinstance(gear, list):
            errors.append(
                {"field": "gear", "message": "build.gear must be a list of items"}
            )
        else:
            required_slots = {
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
            seen_gear_slots = set()
            for idx, item in enumerate(gear):
                slot_name = item.get("slot")
                if slot_name is None:
                    errors.append(
                        {
                            "field": f"gear[{idx}].slot",
                            "message": "Missing gear.slot",
                        }
                    )
                    continue

                if slot_name not in required_slots:
                    errors.append(
                        {
                            "field": f"gear[{idx}].slot",
                            "message": f"Unexpected gear slot '{slot_name}'",
                        }
                    )

                if slot_name in seen_gear_slots:
                    errors.append(
                        {
                            "field": f"gear[{idx}].slot",
                            "message": f"Duplicate gear slot '{slot_name}'",
                        }
                    )
                seen_gear_slots.add(slot_name)

                # Armor weights only on armor slots
                if slot_name in {
                    "head",
                    "shoulder",
                    "chest",
                    "hands",
                    "waist",
                    "legs",
                    "feet",
                }:
                    weight = item.get("weight")
                    if weight not in {"light", "medium", "heavy"}:
                        errors.append(
                            {
                                "field": f"gear[{idx}].weight",
                                "message": f"Invalid armor weight '{weight}', expected 'light', 'medium', or 'heavy'",
                            }
                        )

            # Check for any missing required gear slots
            missing_slots = required_slots - seen_gear_slots
            for slot_name in sorted(missing_slots):
                errors.append(
                    {
                        "field": f"gear.{slot_name}",
                        "message": f"Missing gear item for required slot '{slot_name}'",
                    }
                )

    # CP layout (v1: cp_slotted)
    cp_slotted = build.get("cp_slotted")
    if cp_slotted is None:
        errors.append({"field": "cp_slotted", "message": "Missing build.cp_slotted"})
    else:
        for tree_name in ("warfare", "fitness", "craft"):
            stars = cp_slotted.get(tree_name)
            if stars is None:
                errors.append(
                    {
                        "field": f"cp_slotted.{tree_name}",
                        "message": f"Missing CP tree '{tree_name}'",
                    }
                )
                continue

            if not isinstance(stars, list):
                errors.append(
                    {
                        "field": f"cp_slotted.{tree_name}",
                        "message": f"Expected list of CP IDs for tree '{tree_name}'",
                        }
                )
                continue

            if len(stars) > 4:
                errors.append(
                    {
                        "field": f"cp_slotted.{tree_name}",
                        "message": "More than 4 CP stars slotted in tree",
                    }
                )

            seen_cp_ids = set()
            for idx, cp_id in enumerate(stars):
                if cp_id is None:
                    continue
                if cp_id in seen_cp_ids:
                    errors.append(
                        {
                            "field": f"cp_slotted.{tree_name}[{idx}]",
                            "message": f"Duplicate CP id '{cp_id}' in tree '{tree_name}'",
                        }
                    )
                seen_cp_ids.add(cp_id)

    return errors


def validate_references(
    build: Dict[str, Any],
    skills: List[Dict[str, Any]],
    sets: List[Dict[str, Any]],
    cp_stars: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Cross-reference checks against canonical data.
    """
    errors: List[Dict[str, Any]] = []

    skill_ids = set(collect_ids(skills, "id"))
    set_ids = set(collect_ids(sets, "id"))
    cp_ids = set(collect_ids(cp_stars, "id"))

    # Bars -> skills
    bars = build.get("bars", {})
    for bar_name in ("front", "back"):
        bar_slots = bars.get(bar_name, [])
        if not isinstance(bar_slots, list):
            continue
        for idx, slot in enumerate(bar_slots):
            skill_id = slot.get("skill_id")
            if skill_id is None:
                # Structural function already reports missing skill_id
                continue
            if skill_id not in skill_ids:
                errors.append(
                    {
                        "field": f"bars.{bar_name}[{idx}].skill_id",
                        "message": f"Unknown skill_id '{skill_id}'",
                    }
                )

    # Gear -> sets
    for idx, piece in enumerate(build.get("gear", [])):
        set_id = piece.get("set_id")
        slot_name = piece.get("slot", "?")
        if set_id is None:
            continue
        if set_id not in set_ids:
            errors.append(
                {
                    "field": f"gear[{idx}].set_id",
                    "message": f"Unknown set_id '{set_id}' on slot '{slot_name}'",
                }
            )

    # CP slotted -> cp_stars
    cp_slotted = build.get("cp_slotted", {})
    for tree_name, stars in cp_slotted.items():
        if not isinstance(stars, list):
            continue
        for idx, cp_id in enumerate(stars):
            if cp_id is None:
                continue
            if cp_id not in cp_ids:
                errors.append(
                    {
                        "field": f"cp_slotted.{tree_name}[{idx}]",
                        "message": f"Unknown CP id '{cp_id}' in tree '{tree_name}'",
                    }
                )

    return errors


def unwrap_data_containers(
    skills_data: Any, sets_data: Any, cpstars_data: Any
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Unwrap v1 containers to lists: skills, sets, cp_stars.
    """
    if isinstance(skills_data, dict):
        skills = skills_data.get("skills", [])
    else:
        skills = skills_data

    if isinstance(sets_data, dict):
        sets = sets_data.get("sets", [])
    else:
        sets = sets_data

    if isinstance(cpstars_data, dict):
        cp_stars = cpstars_data.get("cp_stars") or cpstars_data.get("cpstars") or []
    else:
        cp_stars = cpstars_data

    return skills, sets, cp_stars


def validate_build(build_path: Path) -> Dict[str, Any]:
    # Load canonical data files
    skills_data = load_json(DATA_DIR / "skills.json")
    effects_data = load_json(DATA_DIR / "effects.json")  # reserved for future rules
    sets_data = load_json(DATA_DIR / "sets.json")
    cpstars_data = load_json(DATA_DIR / "cp-stars.json")

    build = load_json(build_path)

    # Unwrap top-level containers to lists as defined in the v1 Data Model.
    skills, sets, cp_stars = unwrap_data_containers(skills_data, sets_data, cpstars_data)

    errors: List[Dict[str, Any]] = []
    errors.extend(validate_build_structure(build))
    errors.extend(validate_references(build, skills, sets, cp_stars))

    status = "OK" if not errors else "ERROR"

    result = {
        "build_id": build.get("id"),
        "build_name": build.get("name"),
        "build_path": str(build_path),
        "status": status,
        "error_count": len(errors),
        "errors": errors,
    }

    return result


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: python tools/validate_build.py builds/permafrost-marshal.json")
        return 1

    build_path = Path(argv[1])
    if not build_path.is_file():
        print(
            json.dumps(
                {"status": "ERROR", "message": f"Build file not found: {build_path}"}
            )
        )
        return 1

    result = validate_build(build_path)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
