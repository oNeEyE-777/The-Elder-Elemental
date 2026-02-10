import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
BUILDS_DIR = REPO_ROOT / "builds"


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def index_by_id(items: List[dict], id_key: str = "id") -> Dict[str, dict]:
    return {item[id_key]: item for item in items if isinstance(item, dict) and id_key in item}


def render_build_markdown(
    build: dict,
    skills_idx: Dict[str, dict],
    sets_idx: Dict[str, dict],
    cp_idx: Dict[str, dict],
) -> str:
    lines: List[str] = []

    # Header
    lines.append(f"# {build.get('name', 'Unnamed Build')}")
    lines.append("")
    lines.append(f"- ID: `{build.get('id', '')}`")
    lines.append(f"- Class core: `{build.get('class_core', '')}`")
    subclasses = build.get("subclasses") or []
    if subclasses:
        lines.append(f"- Subclasses: {', '.join(f'`{s}`' for s in subclasses)}")
    lines.append("")

    # Attributes
    attrs = build.get("attributes", {})
    lines.append("## Attributes")
    lines.append("")
    lines.append("| Stat    | Value |")
    lines.append("|---------|-------|")
    lines.append(f"| Health  | {attrs.get('health', 0)} |")
    lines.append(f"| Magicka | {attrs.get('magicka', 0)} |")
    lines.append(f"| Stamina | {attrs.get('stamina', 0)} |")
    lines.append("")

    # Bars
    lines.append("## Bars")
    lines.append("")
    bars = build.get("bars", {})
    for bar_name in ["front", "back"]:
        bar_slots = bars.get(bar_name)
        if not isinstance(bar_slots, list):
            continue

        lines.append(f"### {bar_name.title()} Bar")
        lines.append("")
        lines.append("| Slot | Skill | Skill ID |")
        lines.append("|------|-------|----------|")

        # Sort slots in canonical order
        def slot_sort_key(entry: dict):
            s = entry.get("slot")
            return (0, s) if isinstance(s, int) else (1, 6)

        for entry in sorted(bar_slots, key=slot_sort_key):
            slot = entry.get("slot")
            skill_id = entry.get("skill_id")
            if not skill_id:
                lines.append(f"| {slot} | *(empty)* | |")
                continue
            skill = skills_idx.get(skill_id)
            skill_name = skill.get("name") if skill else "(unknown)"
            lines.append(f"| {slot} | {skill_name} | `{skill_id}` |")

        lines.append("")

    # Gear
    lines.append("## Gear")
    lines.append("")
    gear = build.get("gear", [])
    lines.append("| Slot | Set | Set ID | Notes |")
    lines.append("|------|-----|--------|-------|")

    # Canonical gear slot order
    slot_order = [
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
    gear_by_slot: Dict[str, dict] = {}
    if isinstance(gear, list):
        for item in gear:
            if isinstance(item, dict) and "slot" in item:
                gear_by_slot[item["slot"]] = item

    for slot_name in slot_order:
        item = gear_by_slot.get(slot_name)
        if not item:
            lines.append(f"| {slot_name} | *(empty)* | | |")
            continue

        set_id = item.get("set_id")
        if set_id:
            set_obj = sets_idx.get(set_id)
            set_name = set_obj.get("name") if set_obj else "(unknown)"
        else:
            set_name = "*(none)*"

        notes: List[str] = []
        weight = item.get("weight")
        if weight:
            notes.append(f"weight: {weight}")
        trait = item.get("trait")
        if trait:
            notes.append(f"trait: {trait}")
        enchant = item.get("enchant")
        if enchant:
            notes.append(f"enchant: {enchant}")
        notes_str = ", ".join(notes)

        lines.append(f"| {slot_name} | {set_name} | `{set_id or ''}` | {notes_str} |")

    lines.append("")

    # Champion Points
    lines.append("## Champion Points")
    lines.append("")
    cp_slotted = build.get("cp_slotted", {})
    for tree_name in ["warfare", "fitness", "craft"]:
        stars = cp_slotted.get(tree_name, [])
        lines.append(f"### {tree_name.title()} Tree")
        lines.append("")
        if not stars:
            lines.append("_No stars selected._")
            lines.append("")
            continue

        lines.append("| Slot | Star | Star ID |")
        lines.append("|------|------|---------|")
        for idx, star_id in enumerate(stars):
            if star_id is None:
                lines.append(f"| {idx + 1} | *(empty)* | |")
                continue
            star = cp_idx.get(star_id)
            star_name = star.get("name") if star else "(unknown)"
            lines.append(f"| {idx + 1} | {star_name} | `{star_id}` |")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the test-dummy ESO build JSON to Markdown."
    )
    parser.add_argument(
        "build_path",
        nargs="?",
        default=str(BUILDS_DIR / "test-dummy.json"),
        help="Path to build JSON (default: builds/test-dummy.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(BUILDS_DIR / "test-dummy.md"),
        help="Output Markdown path (default: builds/test-dummy.md)",
    )
    args = parser.parse_args()

    build_path = Path(args.build_path)
    output_path = Path(args.output)

    skills_data = load_json(DATA_DIR / "skills.json")
    effects_data = load_json(DATA_DIR / "effects.json")
    sets_data = load_json(DATA_DIR / "sets.json")
    cp_data = load_json(DATA_DIR / "cp-stars.json")

    skills_idx = index_by_id(skills_data.get("skills", []))
    sets_idx = index_by_id(sets_data.get("sets", []))
    cp_idx = index_by_id(cp_data.get("cp_stars", []))

    build = load_json(build_path)

    md = render_build_markdown(build, skills_idx, sets_idx, cp_idx)

    output_path.write_text(md, encoding="utf-8")
    print(f"[INFO] Wrote Markdown to {output_path}")

    sys.exit(0)


if __name__ == "__main__":
    main()
