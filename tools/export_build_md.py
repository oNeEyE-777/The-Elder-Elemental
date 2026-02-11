#!/usr/bin/env python3
"""
tools/export_build_md.py

Export an ESO build JSON to a Markdown grid.

- Loads:
  - data/skills.json
  - data/sets.json
  - data/cp-stars.json
- Loads a build JSON (default: builds/permafrost-marshal.json).
- Writes a Markdown file next to the build JSON (same stem, .md extension) with:
  - Front/back bars with skill names and tooltip text.
  - Gear table with set names, weights, traits, enchants.
  - Champion Points layout with star names and tooltips.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
BUILDS_DIR = REPO_ROOT / "builds"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def index_by_id(items: List[dict], id_key: str = "id") -> Dict[str, dict]:
    return {item[id_key]: item for item in items if isinstance(item, dict) and id_key in item}


def render_bar_md(
    bar_name: str,
    bar_slots: List[dict],
    skills_idx: Dict[str, dict],
) -> str:
    # Normalize slot keys to string so we can match against "1".."5","ULT"
    slots_by_pos: Dict[Any, dict] = {
        str(entry["slot"]): entry for entry in bar_slots if isinstance(entry, dict) and "slot" in entry
    }

    ordered_slots = ["1", "2", "3", "4", "5", "ULT"]

    lines: List[str] = []
    lines.append(f"### {bar_name.capitalize()} Bar")
    lines.append("")
    lines.append("| Slot | Skill | Tooltip |")
    lines.append("| --- | --- | --- |")

    for pos in ordered_slots:
        entry = slots_by_pos.get(pos)
        skill_label = ""
        tooltip = ""

        if entry is not None:
            skill_id = entry.get("skill_id")
            if isinstance(skill_id, str):
                skill = skills_idx.get(skill_id)
                if skill:
                    skill_label = skill.get("name", skill_id)
                    tooltip = skill.get("tooltip_effect_text", "")
                else:
                    skill_label = skill_id
                    tooltip = ""
        lines.append(f"| {pos} | {skill_label} | {tooltip} |")

    lines.append("")
    return "\n".join(lines)


def render_gear_md(
    gear_items: List[dict],
    sets_idx: Dict[str, dict],
) -> str:
    gear_by_slot: Dict[str, dict] = {
        item["slot"]: item for item in gear_items if isinstance(item, dict) and "slot" in item
    }

    ordered_slots = [
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
    ]

    lines: List[str] = []
    lines.append("## Gear")
    lines.append("")
    lines.append("| Slot | Set | Weight | Trait | Enchant |")
    lines.append("| --- | --- | --- | --- | --- |")

    for slot in ordered_slots:
        item = gear_by_slot.get(slot, {})
        set_id = item.get("set_id")
        set_label = ""
        if isinstance(set_id, str):
            set_rec = sets_idx.get(set_id)
            if set_rec:
                set_label = set_rec.get("name", set_id)
            else:
                set_label = set_id

        weight = item.get("weight") or ""
        trait = item.get("trait") or ""
        enchant = item.get("enchant") or ""

        lines.append(f"| {slot} | {set_label} | {weight} | {trait} | {enchant} |")

    lines.append("")
    return "\n".join(lines)


def render_cp_md(
    cp_slotted: Dict[str, List[str]],
    cp_idx: Dict[str, dict],
) -> str:
    lines: List[str] = []
    lines.append("## Champion Points")
    lines.append("")

    for tree_name in ["warfare", "fitness", "craft"]:
        stars = cp_slotted.get(tree_name, [])
        lines.append(f"### {tree_name.capitalize()}")
        lines.append("")
        lines.append("| Slot | Star | Tooltip |")
        lines.append("| --- | --- | --- |")

        for i, star_id in enumerate(stars, start=1):
            if not isinstance(star_id, str):
                lines.append(f"| {i} |  |  |")
                continue
            star = cp_idx.get(star_id)
            if star:
                name = star.get("name", star_id)
                tooltip = star.get("tooltip_raw", "")
            else:
                name = star_id
                tooltip = ""
            lines.append(f"| {i} | {name} | {tooltip} |")
        lines.append("")

    return "\n".join(lines)


def export_build_md(build_path: Path, out_path: Path) -> None:
    skills_data = load_json(DATA_DIR / "skills.json")
    sets_data = load_json(DATA_DIR / "sets.json")
    cp_data = load_json(DATA_DIR / "cp-stars.json")

    # v1 containers
    skills_idx = index_by_id(skills_data.get("skills", skills_data))
    sets_idx = index_by_id(sets_data.get("sets", sets_data))
    if isinstance(cp_data, dict):
        cp_list = cp_data.get("cp_stars") or cp_data.get("cpstars") or []
    else:
        cp_list = cp_data
    cp_idx = index_by_id(cp_list)

    build = load_json(build_path)

    lines: List[str] = []
    lines.append(f"# {build.get('name', build.get('id', 'Build'))}")
    lines.append("")

    bars = build.get("bars", {})
    front_bar = bars.get("front", [])
    back_bar = bars.get("back", [])

    lines.append("## Bars")
    lines.append("")
    lines.append(render_bar_md("front", front_bar, skills_idx))
    lines.append(render_bar_md("back", back_bar, skills_idx))

    gear_items = build.get("gear", [])
    lines.append(render_gear_md(gear_items, sets_idx))

    cp_slotted = build.get("cp_slotted", {})
    lines.append(render_cp_md(cp_slotted, cp_idx))

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export an ESO build JSON to a Markdown grid."
    )
    parser.add_argument(
        "build_path",
        nargs="?",
        default=str(BUILDS_DIR / "permafrost-marshal.json"),
        help="Path to build JSON (default: builds/permafrost-marshal.json)",
    )
    args = parser.parse_args()

    build_path = Path(args.build_path).resolve()
    if not build_path.exists():
        raise SystemExit(f"Build file not found: {build_path}")

    out_name = build_path.stem + ".md"
    out_path = build_path.with_name(out_name)

    export_build_md(build_path, out_path)

    print(f"[INFO] Wrote Markdown to {out_path}")


if __name__ == "__main__":
    main()
