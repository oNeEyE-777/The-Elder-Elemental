import json
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
BUILDS_DIR = REPO_ROOT / "builds"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_ids(items: List[Dict[str, Any]], key: str) -> List[str]:
    return [item[key] for item in items if key in item]


def validate_build_structure(build: Dict[str, Any]) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []

    if "id" not in build:
        errors.append({"field": "id", "message": "Missing build.id"})
    if "bars" not in build:
        errors.append({"field": "bars", "message": "Missing build.bars"})
        return errors

    bars = build["bars"]
    for bar_name in ("front", "back"):
        if bar_name not in bars:
            errors.append({"field": f"bars.{bar_name}", "message": f"Missing {bar_name} bar"})
            continue
        bar_slots = bars[bar_name]
        if not isinstance(bar_slots, list):
            errors.append(
                {
                    "field": f"bars.{bar_name}",
                    "message": f"Expected list of slots for {bar_name} bar",
                }
            )
            continue
        for idx, slot in enumerate(bar_slots):
            if "skillid" not in slot:
                errors.append(
                    {
                        "field": f"bars.{bar_name}[{idx}].skillid",
                        "message": "Missing skillid on bar slot",
                    }
                )

    if "gear" not in build:
        errors.append({"field": "gear", "message": "Missing build.gear"})
    if "cpslotted" not in build:
        errors.append({"field": "cpslotted", "message": "Missing build.cpslotted"})

    return errors


def validate_references(
    build: Dict[str, Any],
    skills: List[Dict[str, Any]],
    sets: List[Dict[str, Any]],
    cp_stars: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []

    skill_ids = set(collect_ids(skills, "id"))
    set_ids = set(collect_ids(sets, "id"))
    cp_ids = set(collect_ids(cp_stars, "id"))

    bars = build.get("bars", {})
    for bar_name in ("front", "back"):
        bar_slots = bars.get(bar_name, [])
        if not isinstance(bar_slots, list):
            continue
        for idx, slot in enumerate(bar_slots):
            skill_id = slot.get("skillid")
            if skill_id and skill_id not in skill_ids:
                errors.append(
                    {
                        "field": f"bars.{bar_name}[{idx}].skillid",
                        "message": f"Unknown skillid '{skill_id}'",
                    }
                )

    for piece in build.get("gear", []):
        set_id = piece.get("setid")
        slot_name = piece.get("slot", "?")
        if set_id and set_id not in set_ids:
            errors.append(
                {
                    "field": f"gear[{slot_name}].setid",
                    "message": f"Unknown setid '{set_id}'",
                }
            )

    cps = build.get("cpslotted", {})
    for tree_name, stars in cps.items():
        if not isinstance(stars, list):
            continue
        for idx, cp_id in enumerate(stars):
            if cp_id is None:
                continue
            if cp_id not in cp_ids:
                errors.append(
                    {
                        "field": f"cpslotted.{tree_name}[{idx}]",
                        "message": f"Unknown CP id '{cp_id}'",
                    }
                )

    return errors


def validate_build(build_path: Path) -> Dict[str, Any]:
    skills_data = load_json(DATA_DIR / "skills.json")
    effects_data = load_json(DATA_DIR / "effects.json")  # reserved for future rules
    sets_data = load_json(DATA_DIR / "sets.json")
    cp_stars_data = load_json(DATA_DIR / "cp-stars.json")
    build = load_json(build_path)

    # Unwrap top-level containers to lists as defined in the v1 Data Model.
    skills = skills_data.get("skills", []) if isinstance(skills_data, dict) else skills_data
    sets = sets_data.get("sets", []) if isinstance(sets_data, dict) else sets_data
    cp_stars = (
        cp_stars_data.get("cp_stars", [])
        if isinstance(cp_stars_data, dict)
        else cp_stars_data
    )

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
        print("Usage: python tools/validate_build.py <build_json_path>")
        return 1

    build_path = Path(argv[1])
    if not build_path.is_file():
        print(json.dumps({"status": "ERROR", "message": f"Build file not found: {build_path}"}))
        return 1

    result = validate_build(build_path)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
