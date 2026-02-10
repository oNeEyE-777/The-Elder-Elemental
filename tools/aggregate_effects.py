#!/usr/bin/env python3
"""
tools/aggregate_effects.py

Phase 3 implementation of aggregate_effects(build, data) -> list[active_effect].

- Loads data/skills.json, data/effects.json, data/sets.json, data/cp-stars.json.
- Loads a build JSON (e.g. builds/permafrost-marshal.json).
- Aggregates raw active effects from skills, sets, and CP stars.
- Prints a JSON list of effect instances to stdout.

Each effect instance includes at least:
- effect_id
- source  (e.g. "skill.deep_fissure", "set.adept_rider", "cp.ironclad")
- timing
- target
- duration_seconds
"""

import json
import os
import sys
from typing import Any, Dict, List


# ---------- Helpers ----------


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_data(repo_root: str) -> Dict[str, Any]:
    data_dir = os.path.join(repo_root, "data")
    return {
        "skills": load_json(os.path.join(data_dir, "skills.json")),
        "effects": load_json(os.path.join(data_dir, "effects.json")),
        "sets": load_json(os.path.join(data_dir, "sets.json")),
        "cp_stars": load_json(os.path.join(data_dir, "cp-stars.json")),
    }


def index_by_id(items: List[Dict[str, Any]], id_field: str = "id") -> Dict[str, Dict[str, Any]]:
    return {item[id_field]: item for item in items if id_field in item}


# ---------- Core aggregation ----------


def aggregate_effects(build: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
    skills_index = index_by_id(data["skills"].get("skills", []))
    sets_index = index_by_id(data["sets"].get("sets", []))
    cp_index = index_by_id(data["cp_stars"].get("cp-stars", []))

    effects: List[Dict[str, Any]] = []
    effects += collect_skill_effects(build, skills_index)
    effects += collect_set_effects(build, sets_index)
    effects += collect_cp_effects(build, cp_index)
    return effects


# ---------- Skills ----------


def collect_skill_effects(
    build: Dict[str, Any],
    skills_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    bars = build.get("bars", {})

    for bar_name in ("front", "back"):
        for slot in bars.get(bar_name, []):
            # Data Model v1: "skillid" on slots.[file:18]
            skill_id = slot.get("skillid") or slot.get("skill_id")
            if not skill_id:
                continue
            skill = skills_index.get(skill_id)
            if not skill:
                continue

            for eff in skill.get("effects", []):
                effect_id = eff.get("effectid") or eff.get("effect_id")
                if not effect_id:
                    continue
                results.append(
                    {
                        "effect_id": effect_id,
                        # skill_id already encodes the prefix, e.g. "skill.deep_fissure".[file:18]
                        "source": skill_id,
                        "timing": eff.get("timing"),
                        "target": eff.get("target"),
                        "duration_seconds": eff.get("durationseconds", eff.get("duration_seconds")),
                    }
                )

    return results


# ---------- Sets ----------


def compute_set_piece_counts(build: Dict[str, Any]) -> Dict[str, int]:
    """
    build.gear is an array of items like:
      { "slot": "head", "setid": "set.nibenay", ... }.[file:18]
    """
    gear_list = build.get("gear", [])
    counts: Dict[str, int] = {}

    if not isinstance(gear_list, list):
        return counts

    for item in gear_list:
        if not isinstance(item, dict):
            continue
        set_id = item.get("setid") or item.get("set_id")
        if not set_id:
            continue
        counts[set_id] = counts.get(set_id, 0) + 1

    return counts


def collect_set_effects(
    build: Dict[str, Any],
    sets_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Data Model v1: sets[].bonuses[].effects is a list of effect ID strings.[file:18]
    """
    results: List[Dict[str, Any]] = []
    piece_counts = compute_set_piece_counts(build)

    for set_id, count in piece_counts.items():
        set_record = sets_index.get(set_id)
        if not set_record:
            continue

        for bonus in set_record.get("bonuses", []):
            pieces_required = bonus.get("pieces")
            if not isinstance(pieces_required, int) or count < pieces_required:
                continue

            for eff in bonus.get("effects", []):
                if isinstance(eff, str):
                    effect_id = eff
                    timing = bonus.get("timing")
                    duration = bonus.get("durationseconds", bonus.get("duration_seconds"))
                    target = bonus.get("target")
                elif isinstance(eff, dict):
                    effect_id = eff.get("effectid") or eff.get("effect_id")
                    timing = eff.get("timing")
                    duration = eff.get("durationseconds", eff.get("duration_seconds"))
                    target = eff.get("target")
                else:
                    continue

                if not effect_id:
                    continue

                results.append(
                    {
                        "effect_id": effect_id,
                        # set_id already encodes prefix, e.g. "set.adept_rider".[file:18]
                        "source": set_id,
                        "timing": timing,
                        "target": target,
                        "duration_seconds": duration,
                    }
                )

    return results


# ---------- CP stars ----------


def collect_cp_effects(
    build: Dict[str, Any],
    cp_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Data Model v1: build.cpslotted.{warfare,fitness,craft} holds CP IDs.[file:18]
    """
    results: List[Dict[str, Any]] = []
    cp_slotted = build.get("cpslotted", build.get("cp_slotted", {}))

    for tree_name in ("warfare", "fitness", "craft"):
        for cp_id in cp_slotted.get(tree_name, []):
            if not cp_id:
                continue
            star = cp_index.get(cp_id)
            if not star:
                continue

            for eff in star.get("effects", []):
                if isinstance(eff, str):
                    effect_id = eff
                    timing = star.get("timing")
                    duration = star.get("durationseconds", star.get("duration_seconds"))
                    target = star.get("target")
                elif isinstance(eff, dict):
                    effect_id = eff.get("effectid") or eff.get("effect_id")
                    timing = eff.get("timing")
                    duration = eff.get("durationseconds", eff.get("duration_seconds"))
                    target = eff.get("target")
                else:
                    continue

                if not effect_id:
                    continue

                results.append(
                    {
                        "effect_id": effect_id,
                        # cp_id already encodes prefix, e.g. "cp.ironclad".[file:18]
                        "source": cp_id,
                        "timing": timing,
                        "target": target,
                        "duration_seconds": duration,
                    }
                )

    return results


# ---------- CLI ----------


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print(
            "Usage: python tools/aggregate_effects.py builds/permafrost-marshal.json",
            file=sys.stderr,
        )
        return 1

    build_path = argv[1]
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    data = load_all_data(repo_root)
    build = load_json(build_path)
    effects = aggregate_effects(build, data)

    json.dump(effects, sys.stdout, indent=2, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
