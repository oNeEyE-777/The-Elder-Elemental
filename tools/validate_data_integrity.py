#!/usr/bin/env python3
"""
tools/validate_data_integrity.py

Data-wide integrity checks for the ESO Build Engine v1 Data Center.

- Loads:
  - data/skills.json
  - data/effects.json
  - data/sets.json
  - data/cp-stars.json

- Checks:
  - ID uniqueness within each file.
  - ID namespace sanity (skill./buff./debuff./set./cp.).
  - Cross-file references:
    - Skill.effects[*].effectid must exist in effects.id.
    - Set.bonuses[*].effects[*] (strings) must exist in effects.id.
    - CP star.effects[*] (strings) must exist in effects.id.

Output (to stdout):

{
  "status": "OK" | "ERROR",
  "error_count": N,
  "errors": [
    { "field": "...", "message": "..." },
    ...
  ]
}
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_ids(items: List[Dict[str, Any]], id_field: str = "id") -> List[str]:
    return [item[id_field] for item in items if isinstance(item, dict) and id_field in item]


def check_unique_ids(ids: List[str], field_prefix: str) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for idx, _id in enumerate(ids):
        if _id in seen:
            errors.append(
                {
                    "field": f"{field_prefix}[{idx}].id",
                    "message": f"Duplicate id '{_id}'",
                }
            )
        else:
            seen.add(_id)
    return errors


def check_namespace_prefix(ids: List[str], allowed_prefixes: List[str], field_prefix: str) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []
    for idx, _id in enumerate(ids):
        if not any(_id.startswith(p) for p in allowed_prefixes):
            errors.append(
                {
                    "field": f"{field_prefix}[{idx}].id",
                    "message": f"ID '{_id}' does not start with any allowed prefix {allowed_prefixes}",
                }
            )
    return errors


def validate_skills(
    skills: List[Dict[str, Any]],
    effect_ids: Set[str],
) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []

    skill_ids = collect_ids(skills, "id")
    errors.extend(check_unique_ids(skill_ids, "skills"))
    errors.extend(check_namespace_prefix(skill_ids, ["skill."], "skills"))

    for s_idx, skill in enumerate(skills):
        for e_idx, eff in enumerate(skill.get("effects", [])):
            effect_id = eff.get("effectid") or eff.get("effect_id")
            if not effect_id:
                continue
            if effect_id not in effect_ids:
                errors.append(
                    {
                        "field": f"skills[{s_idx}].effects[{e_idx}].effectid",
                        "message": f"Unknown effectid '{effect_id}' (not found in effects.json)",
                    }
                )

    return errors


def validate_effects(effects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []

    effect_ids = collect_ids(effects, "id")
    errors.extend(check_unique_ids(effect_ids, "effects"))
    errors.extend(
        check_namespace_prefix(
            effect_ids,
            ["buff.", "debuff.", "shield.", "hot."],
            "effects",
        )
    )

    return errors


def validate_sets(
    sets: List[Dict[str, Any]],
    effect_ids: Set[str],
) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []

    set_ids = collect_ids(sets, "id")
    errors.extend(check_unique_ids(set_ids, "sets"))
    errors.extend(check_namespace_prefix(set_ids, ["set."], "sets"))

    for s_idx, set_rec in enumerate(sets):
        for b_idx, bonus in enumerate(set_rec.get("bonuses", [])):
            for e_idx, eff in enumerate(bonus.get("effects", [])):
                if isinstance(eff, str):
                    effect_id = eff
                elif isinstance(eff, dict):
                    effect_id = eff.get("effectid") or eff.get("effect_id")
                else:
                    continue

                if not effect_id:
                    continue

                if effect_id not in effect_ids:
                    errors.append(
                        {
                            "field": f"sets[{s_idx}].bonuses[{b_idx}].effects[{e_idx}]",
                            "message": f"Unknown effectid '{effect_id}' (not found in effects.json)",
                        }
                    )

    return errors


def validate_cpstars(
    cpstars: List[Dict[str, Any]],
    effect_ids: Set[str],
) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []

    cp_ids = collect_ids(cpstars, "id")
    errors.extend(check_unique_ids(cp_ids, "cpstars"))
    errors.extend(check_namespace_prefix(cp_ids, ["cp."], "cpstars"))

    for c_idx, star in enumerate(cpstars):
        for e_idx, eff in enumerate(star.get("effects", [])):
            if isinstance(eff, str):
                effect_id = eff
            elif isinstance(eff, dict):
                effect_id = eff.get("effectid") or eff.get("effect_id")
            else:
                continue

            if not effect_id:
                continue

            if effect_id not in effect_ids:
                errors.append(
                    {
                        "field": f"cpstars[{c_idx}].effects[{e_idx}]",
                        "message": f"Unknown effectid '{effect_id}' (not found in effects.json)",
                    }
                )

    return errors


def validate_data_integrity() -> Dict[str, Any]:
    skills_data = load_json(DATA_DIR / "skills.json")
    effects_data = load_json(DATA_DIR / "effects.json")
    sets_data = load_json(DATA_DIR / "sets.json")
    cpstars_data = load_json(DATA_DIR / "cp-stars.json")

    # Unwrap v1 containers.
    skills = skills_data.get("skills", skills_data) if isinstance(skills_data, dict) else skills_data
    effects = effects_data.get("effects", effects_data) if isinstance(effects_data, dict) else effects_data
    sets = sets_data.get("sets", sets_data) if isinstance(sets_data, dict) else sets_data
    cpstars = cpstars_data.get("cpstars", cpstars_data) if isinstance(cpstars_data, dict) else cpstars_data

    effect_ids_set = set(collect_ids(effects, "id"))

    errors: List[Dict[str, Any]] = []
    errors.extend(validate_skills(skills, effect_ids_set))
    errors.extend(validate_effects(effects))
    errors.extend(validate_sets(sets, effect_ids_set))
    errors.extend(validate_cpstars(cpstars, effect_ids_set))

    status = "OK" if not errors else "ERROR"

    return {
        "status": status,
        "error_count": len(errors),
        "errors": errors,
    }


def main(argv: List[str]) -> int:
    if len(argv) != 1:
        print("Usage: python tools/validate_data_integrity.py", file=sys.stderr)
        return 1

    result = validate_data_integrity()
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
