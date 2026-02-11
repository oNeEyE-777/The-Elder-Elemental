#!/usr/bin/env python3
"""
tools/compute_pillars.py

Phase 3 implementation of compute_pillars(build, data) -> dict.

- Loads data/skills.json, data/effects.json, data/sets.json, data/cp-stars.json.
- Loads a build JSON (e.g. builds/permafrost-marshal.json).
- Computes a flat list of effect instances from skills, sets, and CP
  (mirroring tools/aggregate_effects.py).
- Splits effects into two logical states:

  - inactive_state_effects: baseline, always-on effects
    (all set.* and cp.* sources, plus selected skill effects by timing).
  - active_state_effects: full effect set available during the core window
    (all effects from aggregate_effects).

- Uses data/effects.json metadata plus build.pillars config to compute
  pillar statuses for both states: resist, health, speed, hots, shield, core_combo.
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
    data_dir = os.path.join(repo_root, "data")
    return {
        "skills": load_json(os.path.join(data_dir, "skills.json")),
        "effects": load_json(os.path.join(data_dir, "effects.json")),
        "sets": load_json(os.path.join(data_dir, "sets.json")),
        "cp_stars": load_json(os.path.join(data_dir, "cp-stars.json")),
    }


def index_by_id(items: List[Dict[str, Any]], id_field: str = "id") -> Dict[str, Dict[str, Any]]:
    return {item[id_field]: item for item in items if isinstance(item, dict) and id_field in item}


def index_effects_by_id(effects_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    items = effects_data.get("effects", [])
    return {e["id"]: e for e in items if isinstance(e, dict) and "id" in e}


# ---------- Local aggregate_effects implementation (mirrors tools/aggregate_effects.py) ----------


def aggregate_effects(build: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
    skills_index = index_by_id(data["skills"].get("skills", []))
    sets_index = index_by_id(data["sets"].get("sets", []))
    cp_index = index_by_id(data["cp_stars"].get("cp-stars", []))

    effects: List[Dict[str, Any]] = []
    effects += collect_skill_effects(build, skills_index)
    effects += collect_set_effects(build, sets_index)
    effects += collect_cp_effects(build, cp_index)
    return effects


def collect_skill_effects(
    build: Dict[str, Any],
    skills_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    bars = build.get("bars", {})

    for bar_name in ("front", "back"):
        for slot in bars.get(bar_name, []):
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
                        "source": skill_id,
                        "timing": eff.get("timing"),
                        "target": eff.get("target"),
                        "duration_seconds": eff.get("durationseconds", eff.get("duration_seconds")),
                    }
                )

    return results


def compute_set_piece_counts(build: Dict[str, Any]) -> Dict[str, int]:
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
                        "source": set_id,
                        "timing": timing,
                        "target": target,
                        "duration_seconds": duration,
                    }
                )

    return results


def collect_cp_effects(
    build: Dict[str, Any],
    cp_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    cp_slotted = build.get("cp_slotted", {})

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
                        "source": cp_id,
                        "timing": timing,
                        "target": target,
                        "duration_seconds": duration,
                    }
                )

    return results


# ---------- Effect splitting: inactive vs active states ----------


def is_inactive_state_effect(effect: Dict[str, Any]) -> bool:
    """
    Baseline definition:

    - All set.* and cp.* sources -> inactive.
    - skill.* sources -> inactive if timing suggests baseline uptime.
    """
    source = effect.get("source", "")
    timing = (effect.get("timing") or "").lower()

    if source.startswith("set."):
        return True
    if source.startswith("cp."):
        return True

    if source.startswith("skill."):
        return timing in ("slotted", "while_active")

    return False


def split_effects(active_effects: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    inactive: List[Dict[str, Any]] = []
    active: List[Dict[str, Any]] = list(active_effects)

    for eff in active_effects:
        if is_inactive_state_effect(eff):
            inactive.append(eff)

    return {"inactive": inactive, "active": active}


# ---------- Magnitude + metadata helpers ----------


def _get_magnitude(meta: Dict[str, Any]) -> float:
    """
    v1 effects.json uses base_value for magnitude. [file:374]
    """
    val = meta.get("base_value", 0)
    return float(val) if isinstance(val, (int, float)) else 0.0


# Bare ID -> canonical effect.id mapping, to avoid JSON edits. [file:374][file:385]
BARE_TO_EFFECT_ID: Dict[str, str] = {
    # Resist / Breach / Resolve
    "buff.major_resolve": "effect.buff.major_resolve",
    "debuff.major_breach": "effect.debuff.major_breach",
    "debuff.minor_breach": "effect.debuff.minor_breach",
    "buff.pariah_scaling_resist": "effect.buff.pariah_scaling",
    "buff.wield_soul_minor_buff": "effect.buff.wield_soul_minor_buff",
    # Speed-related
    "buff.celerity": "effect.buff.celerity_minor",
    "buff.movement_speed_minor": "effect.buff.celerity_minor",
    "buff.steeds_blessing": "effect.buff.steeds_blessing",
    "buff.mounted_speed_scalar": "effect.buff.warmount",
    "buff.adept_rider_speed": "effect.buff.adept_rider_speed_in_combat",
    "buff.wild_hunt_speed": "effect.buff.wild_hunt_speed",
    # HoTs
    "hot.green_dragon_blood": "effect.hot.green_dragon_blood",
    "hot.barrier": "effect.hot.barrier",
    "hot.resolving_vigor": "effect.hot.resolving_vigor",
    # Shields
    "shield.barrier": "effect.shield.barrier",
    "shield.hardened_armor": "effect.shield.hardened_armor",
    "shield.soul_burst": "effect.shield.soul_burst",
    # Damage taken / Ironclad / Ulfsild
    "buff.damage_taken_direct_minor": "effect.buff.ironclad_damage_taken",
    "buff.ulfsild_defense": "effect.buff.ulfsild_defense",
}


def _resolve_effect_meta(
    eff: Dict[str, Any],
    effects_index: Dict[str, Dict[str, Any]],
) -> Dict[str, Any] | None:
    """
    Resolve effect metadata for:
    - raw effect_id from aggregation (e.g. hot.green_dragon_blood),
    - bare -> canonical mapping via BARE_TO_EFFECT_ID,
    - already canonical IDs (effect.*). [file:374][file:385]
    """
    raw_id = eff.get("effect_id")
    if not raw_id:
        return None

    # 1) Direct lookup (already canonical).
    meta = effects_index.get(raw_id)
    if meta:
        return meta

    # 2) Bare -> canonical mapping.
    mapped = BARE_TO_EFFECT_ID.get(raw_id)
    if mapped:
        meta = effects_index.get(mapped)
        if meta:
            return meta

    # 3) Fallback: add effect. prefix.
    if not raw_id.startswith("effect."):
        meta = effects_index.get(f"effect.{raw_id}")
        if meta:
            return meta

    return None


# ---------- Pillar computation core ----------


def compute_pillars(build: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    active_effects: List[Dict[str, Any]] = aggregate_effects(build, data)
    effects_index = index_effects_by_id(data["effects"])

    split = split_effects(active_effects)
    inactive_effects = split["inactive"]
    active_state_effects = split["active"]

    pillars_cfg = build.get("pillars", {}) or {}

    resist_status = {
        "inactive": evaluate_resist_pillar(
            build, inactive_effects, effects_index, pillars_cfg.get("resist", {})
        ),
        "active": evaluate_resist_pillar(
            build, active_state_effects, effects_index, pillars_cfg.get("resist", {})
        ),
    }
    health_status = {
        "inactive": evaluate_health_pillar(
            build, inactive_effects, effects_index, pillars_cfg.get("health", {})
        ),
        "active": evaluate_health_pillar(
            build, active_state_effects, effects_index, pillars_cfg.get("health", {})
        ),
    }
    speed_status = {
        "inactive": evaluate_speed_pillar(
            build, inactive_effects, effects_index, pillars_cfg.get("speed", {})
        ),
        "active": evaluate_speed_pillar(
            build, active_state_effects, effects_index, pillars_cfg.get("speed", {})
        ),
    }
    hots_status = {
        "inactive": evaluate_hots_pillar(
            build, inactive_effects, effects_index, pillars_cfg.get("hots", {})
        ),
        "active": evaluate_hots_pillar(
            build, active_state_effects, effects_index, pillars_cfg.get("hots", {})
        ),
    }
    shield_status = {
        "inactive": evaluate_shield_pillar(
            build, inactive_effects, effects_index, pillars_cfg.get("shield", {})
        ),
        "active": evaluate_shield_pillar(
            build, active_state_effects, effects_index, pillars_cfg.get("shield", {})
        ),
    }
    core_combo_status = evaluate_core_combo_pillar(build, pillars_cfg.get("core_combo", {}))

    return {
        "build_id": build.get("id"),
        "pillars": {
            "resist": resist_status,
            "health": health_status,
            "speed": speed_status,
            "hots": hots_status,
            "shield": shield_status,
            "core_combo": core_combo_status,
        },
    }


# ---------- Resist pillar ----------


def evaluate_resist_pillar(
    build: Dict[str, Any],
    active_effects: List[Dict[str, Any]],
    effects_index: Dict[str, Dict[str, Any]],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    target = cfg.get("target_resist_shown") or cfg.get("targetresistshown")

    total_bonus = 0.0
    contributing_sources: List[Dict[str, Any]] = []

    for eff in active_effects:
        eff_meta = _resolve_effect_meta(eff, effects_index)
        if not eff_meta:
            continue

        stat = eff_meta.get("stat")
        if stat != "resist":
            continue

        magnitude = _get_magnitude(eff_meta)
        total_bonus += magnitude
        contributing_sources.append(
            {
                "effect_id": eff["effect_id"],
                "source": eff["source"],
                "magnitude": magnitude,
            }
        )

    computed_resist = int(total_bonus)
    meets_target = None
    if isinstance(target, (int, float)):
        meets_target = computed_resist >= target

    return {
        "meets_target": bool(meets_target) if meets_target is not None else None,
        "computed_resist_shown": computed_resist,
        "target_resist_shown": target,
        "sources": contributing_sources,
    }


# ---------- Health pillar ----------


def evaluate_health_pillar(
    build: Dict[str, Any],
    active_effects: List[Dict[str, Any]],
    effects_index: Dict[str, Dict[str, Any]],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    attrs = build.get("attributes", {}) or {}
    attr_health = attrs.get("health", 0)

    total_bonus = 0.0
    contributing_sources: List[Dict[str, Any]] = []

    for eff in active_effects:
        eff_meta = _resolve_effect_meta(eff, effects_index)
        if not eff_meta:
            continue

        stat = eff_meta.get("stat")
        if stat not in ("max_health", "health_max"):
            continue

        magnitude = _get_magnitude(eff_meta)
        total_bonus += magnitude
        contributing_sources.append(
            {
                "effect_id": eff["effect_id"],
                "source": eff["source"],
                "magnitude": magnitude,
            }
        )

    focus = cfg.get("focus")
    meets_target = None
    if focus in ("health_first", "healthfirst"):
        meets_target = (attr_health == 64)

    return {
        "meets_target": bool(meets_target) if meets_target is not None else None,
        "attributes_health": attr_health,
        "total_health_bonus": int(total_bonus),
        "focus": focus,
        "sources": contributing_sources,
    }


# ---------- Speed pillar ----------


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
            "movement_speed",
            "movement_speed_out_of_combat",
            "mounted_speed",
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


# ---------- HoTs pillar ----------


def evaluate_hots_pillar(
    build: Dict[str, Any],
    active_effects: List[Dict[str, Any]],
    effects_index: Dict[str, Dict[str, Any]],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    min_hots = cfg.get("min_active_hots") or cfg.get("minactivehots")

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


# ---------- Shield pillar ----------


def evaluate_shield_pillar(
    build: Dict[str, Any],
    active_effects: List[Dict[str, Any]],
    effects_index: Dict[str, Dict[str, Any]],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    min_shields = cfg.get("min_active_shields") or cfg.get("minactiveshields")

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


# ---------- Core combo pillar ----------


def evaluate_core_combo_pillar(
    build: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    required_skills: List[str] = cfg.get("skills", []) or []

    bars = build.get("bars", {}) or {}
    slotted_skill_ids = set()
    for bar_name in ("front", "back"):
        for slot in bars.get(bar_name, []):
            skill_id = slot.get("skillid") or slot.get("skill_id")
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
