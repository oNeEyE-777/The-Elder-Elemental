#!/usr/bin/env python3
"""
tools/compute_pillars.py

Phase 3 implementation of compute_pillars(build, data) -> dict.

- Loads data/skills.json, data/effects.json, data/sets.json, data/cp-stars.json.
- Loads a build JSON (e.g. builds/permafrost-marshal.json).
- Aggregates a flat list of effect instances from skills, sets, and CP
  using the same logic as tools/aggregate_effects.py.
- Splits effects into two logical states:

  - inactive_state_effects: baseline, always-on effects
    (all set.* and cp.* sources, plus selected skill effects by timing).
  - active_state_effects: full effect set available during the core window
    (all effects from aggregate_effects).

- Uses data/effects.json metadata plus build.pillars config to compute
  pillar statuses for both states: resist, health, speed, hots, shield, core_combo.

This module assumes the strict v1 Data Model:

- Builds:
  - bars.front/back[*].skill_id
  - gear[*].set_id
  - cp_slotted.{warfare,fitness,craft} = array of cp.* IDs
- Data:
  - skills.json: { "skills": [ { "id": "skill.*", "effects": [ { "effect_id": ... } ] } ] }
  - sets.json:   { "sets":   [ { "id": "set.*",   "bonuses": [ { "effects": [effect_id or object] } ] } ] }
  - cp-stars.json: { "cp_stars": [ { "id": "cp.*", "effects": [effect_id or object] } ] }
  - effects.json: { "effects": [ { "id": "buff.|debuff.|shield.|hot.", "stat": "...", ... } ] }

No legacy aliases (skillid/setid/effectid/durationseconds/etc.) are accepted.
"""

import json
import os
import sys
from typing import Any, Dict, List


# ---------- Shared loading helpers ----------


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_data(repo_root: str) -> Dict[str, Any]:
    """
    Load canonical data files from data/.
    """
    data_dir = os.path.join(repo_root, "data")
    return {
        "skills": load_json(os.path.join(data_dir, "skills.json")),
        "effects": load_json(os.path.join(data_dir, "effects.json")),
        "sets": load_json(os.path.join(data_dir, "sets.json")),
        "cp_stars": load_json(os.path.join(data_dir, "cp-stars.json")),
    }


def unwrap_containers(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize top-level containers to lists according to the v1 Data Model.

    Accepts either:
    - Bare arrays, or
    - Objects with { "skills": [...] }, { "sets": [...] }, { "cp_stars": [...] }.
    """
    skills_data = data["skills"]
    sets_data = data["sets"]
    cpstars_data = data["cp_stars"]

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

    return {
        "skills": skills,
        "sets": sets,
        "cp_stars": cp_stars,
    }


def index_by_id(items: List[Dict[str, Any]], id_field: str = "id") -> Dict[str, Dict[str, Any]]:
    return {item[id_field]: item for item in items if isinstance(item, dict) and id_field in item}


def index_effects_by_id(effects_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    items = effects_data.get("effects", [])
    return {e["id"]: e for e in items if isinstance(e, dict) and "id" in e}


# ---------- Shared aggregate_effects implementation (mirrors tools/aggregate_effects.py) ----------


def aggregate_effects(build: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Collect all active effect instances from skills, sets, and CP stars.

    This mirrors tools/aggregate_effects.py but is inlined to avoid cross-tool imports.
    """
    unwrapped = unwrap_containers(data)
    skills_index = index_by_id(unwrapped["skills"])
    sets_index = index_by_id(unwrapped["sets"])
    cp_index = index_by_id(unwrapped["cp_stars"])

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
    bars = build.get("bars", {}) or {}

    for bar_name in ("front", "back"):
        for slot in bars.get(bar_name, []):
            if not isinstance(slot, dict):
                continue
            # v1: bars.*[*].skill_id
            skill_id = slot.get("skill_id")
            if not skill_id:
                continue
            skill = skills_index.get(skill_id)
            if not skill:
                continue

            for eff in skill.get("effects", []):
                if not isinstance(eff, dict):
                    continue
                effect_id = eff.get("effect_id")
                if not effect_id:
                    continue
                results.append(
                    {
                        "effect_id": effect_id,
                        # skill_id already encodes the prefix, e.g. "skill.deep_fissure"
                        "source": skill_id,
                        "timing": eff.get("timing"),
                        "target": eff.get("target"),
                        "duration_seconds": eff.get("duration_seconds"),
                    }
                )

    return results


# ---------- Sets ----------


def compute_set_piece_counts(build: Dict[str, Any]) -> Dict[str, int]:
    """
    v1: build.gear is an array of items like:
      { "slot": "head", "set_id": "set.nibenay", ... }
    """
    gear_list = build.get("gear", [])
    counts: Dict[str, int] = {}

    if not isinstance(gear_list, list):
        return counts

    for item in gear_list:
        if not isinstance(item, dict):
            continue
        set_id = item.get("set_id")
        if not set_id:
            continue
        counts[set_id] = counts.get(set_id, 0) + 1

    return counts


def collect_set_effects(
    build: Dict[str, Any],
    sets_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    v1: sets[*].bonuses[*].effects is a list of effect IDs or richer objects.
    """
    results: List[Dict[str, Any]] = []
    piece_counts = compute_set_piece_counts(build)

    for set_id, count in piece_counts.items():
        set_record = sets_index.get(set_id)
        if not set_record:
            continue

        for bonus in set_record.get("bonuses", []):
            if not isinstance(bonus, dict):
                continue
            pieces_required = bonus.get("pieces")
            if not isinstance(pieces_required, int) or count < pieces_required:
                continue

            for eff in bonus.get("effects", []):
                if isinstance(eff, str):
                    effect_id = eff
                    timing = bonus.get("timing")
                    duration = bonus.get("duration_seconds")
                    target = bonus.get("target")
                elif isinstance(eff, dict):
                    effect_id = eff.get("effect_id")
                    timing = eff.get("timing")
                    duration = eff.get("duration_seconds")
                    target = eff.get("target")
                else:
                    continue

                if not effect_id:
                    continue

                results.append(
                    {
                        "effect_id": effect_id,
                        # set_id already encodes prefix, e.g. "set.adept_rider"
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
    v1: build.cp_slotted.{warfare,fitness,craft} holds CP IDs.
        data/cp-stars.json: cp_stars[*].effects is a list of effect IDs or richer objects.
    """
    results: List[Dict[str, Any]] = []
    cp_slotted = build.get("cp_slotted", {}) or {}

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
                    duration = star.get("duration_seconds")
                    target = star.get("target")
                elif isinstance(eff, dict):
                    effect_id = eff.get("effect_id")
                    timing = eff.get("timing")
                    duration = eff.get("duration_seconds")
                    target = eff.get("target")
                else:
                    continue

                if not effect_id:
                    continue

                results.append(
                    {
                        "effect_id": effect_id,
                        # cp_id already encodes prefix, e.g. "cp.ironclad"
                        "source": cp_id,
                        "timing": timing,
                        "target": target,
                        "duration_seconds": duration,
                    }
                )

    return results


# ---------- Effect meta helpers ----------


def _resolve_effect_meta(
    eff: Dict[str, Any],
    effects_index: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Given an effect instance (with effect_id), look up its metadata in effects_index.
    """
    effect_id = eff.get("effect_id")
    if not effect_id:
        return {}
    return effects_index.get(effect_id, {})


def _get_magnitude(meta: Dict[str, Any]) -> float:
    """
    Resolve a scalar magnitude from an effect metadata record.

    For now, we treat magnitude_value as the canonical field; if not present,
    we fall back to base_value to stay compatible with current effects.json.
    """
    if "magnitude_value" in meta and isinstance(meta["magnitude_value"], (int, float)):
        return float(meta["magnitude_value"])
    if "base_value" in meta and isinstance(meta["base_value"], (int, float)):
        return float(meta["base_value"])
    return 0.0


# ---------- Pillar evaluators ----------


def evaluate_resist_pillar(
    build: Dict[str, Any],
    active_effects: List[Dict[str, Any]],
    effects_index: Dict[str, Dict[str, Any]],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    target_resist = cfg.get("target_resist_shown")

    total_resist = 0.0
    sources: List[Dict[str, Any]] = []

    for eff in active_effects:
        meta = _resolve_effect_meta(eff, effects_index)
        if not meta:
            continue

        stat = meta.get("stat")
        if stat not in ("resistance_flat", "resist", "healthmax_resist"):
            continue

        magnitude = _get_magnitude(meta)
        if magnitude == 0:
            continue

        total_resist += magnitude
        sources.append(
            {
                "effect_id": eff["effect_id"],
                "source": eff["source"],
                "stat": stat,
                "magnitude": magnitude,
            }
        )

    meets_target = None
    if isinstance(target_resist, (int, float)):
        meets_target = total_resist >= float(target_resist)

    return {
        "meets_target": bool(meets_target) if meets_target is not None else None,
        "computed_resist_shown": total_resist,
        "target_resist_shown": target_resist,
        "sources": sources,
    }


def evaluate_health_pillar(
    build: Dict[str, Any],
    active_effects: List[Dict[str, Any]],
    effects_index: Dict[str, Dict[str, Any]],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    focus = cfg.get("focus")
    attributes = build.get("attributes", {}) or {}
    attributes_health = attributes.get("health")

    total_health_bonus = 0.0
    sources: List[Dict[str, Any]] = []

    for eff in active_effects:
        meta = _resolve_effect_meta(eff, effects_index)
        if not meta:
            continue

        stat = meta.get("stat")
        if stat not in ("maxhealth", "healthmax"):
            continue

        magnitude = _get_magnitude(meta)
        if magnitude == 0:
            continue

        total_health_bonus += magnitude
        sources.append(
            {
                "effect_id": eff["effect_id"],
                "source": eff["source"],
                "stat": stat,
                "magnitude": magnitude,
            }
        )

    meets_target = None
    # For now, health pillar is qualitative; if needed, you can add thresholds later.

    return {
        "meets_target": meets_target,
        "focus": focus,
        "attributes_health": attributes_health,
        "total_health_bonus": total_health_bonus,
        "sources": sources,
    }


def evaluate_speed_pillar(
    build: Dict[str, Any],
    active_effects: List[Dict[str, Any]],
    effects_index: Dict[str, Dict[str, Any]],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    profile = cfg.get("profile")

    speed_effects: List[Dict[str, Any]] = []
    for eff in active_effects:
        meta = _resolve_effect_meta(eff, effects_index)
        if not meta:
            continue

        stat = meta.get("stat")
        if stat not in (
            "movement_speed_scalar",
            "movement_speed_out_of_combat_scalar",
            "mounted_speed_scalar",
        ):
            continue

        magnitude = _get_magnitude(meta)
        speed_effects.append(
            {
                "effect_id": eff["effect_id"],
                "source": eff["source"],
                "stat": stat,
                "magnitude": magnitude,
            }
        )

    meets_target = None
    if profile in ("extreme_speed", "extremespeed"):
        meets_target = len(speed_effects) > 0

    profiles_matched: List[str] = []
    if meets_target:
        profiles_matched.append(profile)

    return {
        "meets_target": bool(meets_target) if meets_target is not None else None,
        "speed_effects": speed_effects,
        "profiles_matched": profiles_matched,
    }


def evaluate_hots_pillar(
    build: Dict[str, Any],
    active_effects: List[Dict[str, Any]],
    effects_index: Dict[str, Dict[str, Any]],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    min_hots = cfg.get("min_active_hots")

    hot_effects: Dict[str, Dict[str, Any]] = {}
    for eff in active_effects:
        meta = _resolve_effect_meta(eff, effects_index)
        if not meta:
            continue

        stat = meta.get("stat")
        if stat != "hot":
            continue

        if eff["effect_id"] not in hot_effects:
            hot_effects[eff["effect_id"]] = {
                "effect_id": eff["effect_id"],
                "source": eff["source"],
            }

    active_hots = len(hot_effects)
    meets_target = None
    if isinstance(min_hots, int):
        meets_target = active_hots >= min_hots

    return {
        "meets_target": bool(meets_target) if meets_target is not None else None,
        "active_hots": active_hots,
        "min_active_hots": min_hots,
        "hot_effects": list(hot_effects.values()),
    }


def evaluate_shield_pillar(
    build: Dict[str, Any],
    active_effects: List[Dict[str, Any]],
    effects_index: Dict[str, Dict[str, Any]],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    min_shields = cfg.get("min_active_shields")

    shield_effects: Dict[str, Dict[str, Any]] = {}
    for eff in active_effects:
        meta = _resolve_effect_meta(eff, effects_index)
        if not meta:
            continue

        stat = meta.get("stat")
        if stat != "shield":
            continue

        if eff["effect_id"] not in shield_effects:
            shield_effects[eff["effect_id"]] = {
                "effect_id": eff["effect_id"],
                "source": eff["source"],
            }

    active_shields = len(shield_effects)
    meets_target = None
    if isinstance(min_shields, int):
        meets_target = active_shields >= min_shields

    return {
        "meets_target": bool(meets_target) if meets_target is not None else None,
        "active_shields": active_shields,
        "min_active_shields": min_shields,
        "shield_effects": list(shield_effects.values()),
    }


def evaluate_core_combo_pillar(
    build: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    required_skills: List[str] = cfg.get("skills", []) or []

    bars = build.get("bars", {}) or {}
    slotted_skill_ids = set()
    for bar_name in ("front", "back"):
        for slot in bars.get(bar_name, []):
            if not isinstance(slot, dict):
                continue
            skill_id = slot.get("skill_id")
            if skill_id:
                slotted_skill_ids.add(skill_id)

    missing: List[str] = [s for s in required_skills if s not in slotted_skill_ids]
    all_skills_slotted = len(missing) == 0 if required_skills else None

    return {
        "meets_target": all_skills_slotted,
        "required_skills": required_skills,
        "missing_skills": missing,
        "all_skills_slotted": all_skills_slotted,
    }


# ---------- Main compute_pillars orchestration ----------


def split_active_inactive(
    all_effects: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Split a flat effect list into inactive_state_effects and active_state_effects.

    Strategy:
    - active_state_effects: all effects.
    - inactive_state_effects:
      - all set.* and cp.* sources (always-on gear/CP).
      - skill effects whose timing suggests upkeepable / always-on behaviour
        (e.g., "while_active", or similar; this can be tuned as needed).
    """
    active = list(all_effects)
    inactive: List[Dict[str, Any]] = []

    for eff in all_effects:
        source = eff.get("source", "")
        timing = eff.get("timing")

        is_gear_or_cp = source.startswith("set.") or source.startswith("cp.")
        is_upkeep_skill = timing in ("while_active", "passive", "on_block")

        if is_gear_or_cp or is_upkeep_skill:
            inactive.append(eff)

    return {
        "inactive": inactive,
        "active": active,
    }


def compute_pillars(build: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute pillar statuses for a build given canonical data.
    """
    # Aggregate effect instances using shared logic.
    all_effects = aggregate_effects(build, data)
    split = split_active_inactive(all_effects)

    inactive_effects = split["inactive"]
    active_effects = split["active"]

    effects_index = index_effects_by_id(data["effects"])

    pillars_cfg = build.get("pillars", {}) or {}

    # Inactive state pillars.
    resist_inactive = evaluate_resist_pillar(
        build, inactive_effects, effects_index, pillars_cfg.get("resist", {}) or {}
    )
    health_inactive = evaluate_health_pillar(
        build, inactive_effects, effects_index, pillars_cfg.get("health", {}) or {}
    )
    speed_inactive = evaluate_speed_pillar(
        build, inactive_effects, effects_index, pillars_cfg.get("speed", {}) or {}
    )
    hots_inactive = evaluate_hots_pillar(
        build, inactive_effects, effects_index, pillars_cfg.get("hots", {}) or {}
    )
    shield_inactive = evaluate_shield_pillar(
        build, inactive_effects, effects_index, pillars_cfg.get("shield", {}) or {}
    )
    core_combo = evaluate_core_combo_pillar(
        build, pillars_cfg.get("core_combo", {}) or {}
    )

    # Active state pillars.
    resist_active = evaluate_resist_pillar(
        build, active_effects, effects_index, pillars_cfg.get("resist", {}) or {}
    )
    health_active = evaluate_health_pillar(
        build, active_effects, effects_index, pillars_cfg.get("health", {}) or {}
    )
    speed_active = evaluate_speed_pillar(
        build, active_effects, effects_index, pillars_cfg.get("speed", {}) or {}
    )
    hots_active = evaluate_hots_pillar(
        build, active_effects, effects_index, pillars_cfg.get("hots", {}) or {}
    )
    shield_active = evaluate_shield_pillar(
        build, active_effects, effects_index, pillars_cfg.get("shield", {}) or {}
    )

    return {
        "build_id": build.get("id"),
        "pillars": {
            "resist": {
                "inactive": resist_inactive,
                "active": resist_active,
            },
            "health": {
                "inactive": health_inactive,
                "active": health_active,
            },
            "speed": {
                "inactive": speed_inactive,
                "active": speed_active,
            },
            "hots": {
                "inactive": hots_inactive,
                "active": hots_active,
            },
            "shield": {
                "inactive": shield_inactive,
                "active": shield_active,
            },
            "core_combo": core_combo,
        },
    }


# ---------- CLI ----------


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print(
            "Usage: python tools/compute_pillars.py builds/permafrost-marshal.json",
            file=sys.stderr,
        )
        return 1

    build_path = argv[1]
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    data = load_all_data(repo_root)
    build = load_json(build_path)

    result = compute_pillars(build, data)

    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
