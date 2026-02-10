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

    for barname in ("front", "back"):
        if barname not in bars:
            errors.append(
                {"field": f"bars.{barname}", "message": f"Missing {barname} bar"}
            )
            continue

        barslots = bars[barname]
        if not isinstance(barslots, list):
            errors.append(
                {
                    "field": f"bars.{barname}",
                    "message": f"Expected list of slots for bar '{barname}'",
                }
            )
            continue

        for idx, slot in enumerate(barslots):
            if "skillid" not in slot:
                errors.append(
                    {
                        "field": f"bars.{barname}[{idx}].skillid",
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
    cpstars: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []

    skill_ids = set(collect_ids(skills, "id"))
    set_ids = set(collect_ids(sets, "id"))
    cp_ids = set(collect_ids(cpstars, "id"))

    bars = build.get("bars", {})
    for barname in ("front", "back"):
        barslots = bars.get(barname, [])
        if not isinstance(barslots, list):
            continue
        for idx, slot in enumerate(barslots):
            skillid = slot.get("skillid")
            if skillid and skillid not in skill_ids:
                errors.append(
                    {
                        "field": f"bars.{barname}[{idx}].skillid",
                        "message": f"Unknown skillid '{skillid}'",
                    }
                )

    for piece in build.get("gear", []):
        setid = piece.get("setid")
        slotname = piece.get("slot", "?")
        if setid and setid not in set_ids:
            errors.append(
                {
                    "field": f"gear[{slotname}].setid",
                    "message": f"Unknown setid '{setid}'",
                }
            )

    cps = build.get("cpslotted", {})
    for treename, stars in cps.items():
        if not isinstance(stars, list):
            continue
        for idx, cpid in enumerate(stars):
            if cpid is None:
                continue
            if cpid not in cp_ids:
                errors.append(
                    {
                        "field": f"cpslotted.{treename}[{idx}]",
                        "message": f"Unknown CP id '{cpid}'",
                    }
                )

    return errors


def validate_build(build_path: Path) -> Dict[str, Any]:
    skills_data = load_json(DATA_DIR / "skills.json")
    effects_data = load_json(DATA_DIR / "effects.json")  # reserved for future rules
    sets_data = load_json(DATA_DIR / "sets.json")
    cpstars_data = load_json(DATA_DIR / "cp-stars.json")

    build = load_json(build_path)

    # Unwrap top-level containers to lists as defined in the v1 Data Model. [file:1]
    skills = skills_data.get("skills", skills_data) if isinstance(skills_data, dict) else skills_data
    sets = sets_data.get("sets", sets_data) if isinstance(sets_data, dict) else sets_data
    cpstars = cpstars_data.get("cpstars", cpstars_data) if isinstance(cpstars_data, dict) else cpstars_data

    errors: List[Dict[str, Any]] = []
    errors.extend(validate_build_structure(build))
    errors.extend(validate_references(build, skills, sets, cpstars))

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
