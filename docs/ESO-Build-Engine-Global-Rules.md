# ESO Build Engine – Global Rules & Validation Checklist **docs/ESO-Build-Engine-Global-Rules.md**

## Purpose

Define the **structural and stacking rules** that apply to any build JSON (starting with Permafrost Marshal), and the Python contracts that validators and math tools under `tools/` must follow.​[file:3][file:4]

These rules are the normative source for build structure, CP layout, gear constraints, and effect stacking behavior; all tools and UIs must conform to them.​[file:1][file:3][file:4]

---

## 1. Bars & skills

- Exactly 2 bars: `front` and `back`.​[file:2][file:3]

- Each bar has:

  - 5 normal slots: `1`, `2`, `3`, `4`, `5`
  - 1 ultimate slot: `"ULT"`​[file:2][file:3]

**Constraints**

- At most 1 skill per `(bar, slot)` pair.
- A given `skill_id` may appear on both bars, but not more than once per bar.
- All `skill_id` values must exist in `data/skills.json`.​[file:2][file:3]
- Bars must be present as `build["bars"]["front"]` and `build["bars"]["back"]`, each an array of slot objects with `slot` and `skill_id` fields.​[file:2][file:3]

---

## 2. Gear layout & sets

**Required gear slots (12)**

- `head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`, `neck`, `ring1`, `ring2`, `front_weapon`, `back_weapon`.​[file:2][file:3]

**Constraints**

- Exactly 1 gear item per required slot.
- At most **1 mythic set** equipped across all gear slots.
- Armor slots (`head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`) must have `weight` ∈ `{ "light", "medium", "heavy" }`.
- All `set_id` values must exist in `data/sets.json`.​[file:2][file:3]
- Gear records reference `sets.id` by `set_id` only; no inline ESO math or tooltip text in gear.​[file:2][file:3]

**Soft checks**

- Number of pieces per `set_id` should align with ESO set rules (for example, no 7 pieces of a 5‑piece set).
- Soft checks produce warnings, not hard validation failures.​[file:3]

---

## 3. CP layout

- CP trees: exactly `warfare`, `fitness`, `craft`.​[file:2][file:3]

**Each tree**

- Up to 4 slotted stars.
- No duplicated `cp_id` within a tree.
- Only stars with `slot_type: "slottable"` may appear in `cp_slotted`.
- All `cp_id` values must exist in `data/cp-stars.json`.​[file:2][file:3]
- CP layout is stored as `build["cp_slotted"][tree] = [cp_id_or_null, ...]` with up to 4 entries per tree.​[file:2][file:3]

---

## 4. Effect stacking rules (buffs/debuffs)

Effect semantics come from `data/effects.json`. The engine applies **Major/Minor uniqueness** per stat:​[file:2][file:3]

- For a given `stat`, at most:

  - One effective `type: "major"` effect.
  - One effective `type: "minor"` effect.

**Exceptions**

- An effect may list other effect IDs in `stacks_with` to allow stacking (for example, unique + Major, or multiple unique effects).​[file:2][file:3]

**Goals**

- Avoid double‑counting the same Major/Minor buff on a stat.
- Provide a canonical, normalized effect set for all math calculations (resist, damage taken, speed, etc.).​[file:2][file:3]

The exact math (what `stat` means and how its value applies) is defined in `data/effects.json` and shared across skills, sets, and CP.​[file:2][file:3]

**Logic‑driven terminology and functions**

- Effect fields, enums, and math helpers must use logic‑driven, system‑neutral terms, not ESO slang or tooltip text.
- Names must describe what they represent (`movement_speed_scalar`, `resist_shown`, `state_active`) instead of in‑game labels like “buffed”, “unbuffed”, “Major Breach”, or “Major Resolve”.
- ESO‑specific wording belongs only in human‑facing `name`/`description` fields in JSON, never as primary keys, enum values, or function names, so that effect math and stacking rules remain stable even if ESO terminology changes.​[file:5][file:6]

---

## 5. Validation and helper functions (Python contracts)

These function contracts define the expected behavior of Python validators and helpers under `tools/`. Implementations may have more parameters and internal helpers, but must satisfy these interfaces conceptually.​[file:3][file:4][file:7]

### validate_build_structure(build, data) -> (valid: bool, violations: list[str])

Checks:

- **Bars**
  - Correct bar names (`"front"`, `"back"`).
  - Correct slots (`1`–`5` plus `"ULT"`).
  - No duplicate `slot` values per bar.
  - All `skill_id` values exist in `data["skills"]` from `data/skills.json`.​[file:2][file:3]

- **Gear**
  - All required gear slots present.
  - Exactly 1 item per slot.
  - Mythic constraint (≤ 1 mythic set across all gear).
  - Armor weights valid for armor slots.
  - All `set_id` values exist in `data["sets"]` from `data/sets.json`.​[file:2][file:3]

- **CP**
  - Exactly 3 trees: `warfare`, `fitness`, `craft`.
  - ≤ 4 slotted stars per tree.
  - No duplicates within a tree.
  - All CP IDs exist in `data["cp_stars"]` from `data/cp-stars.json`.
  - Only `slot_type: "slottable"` IDs appear in `cp_slotted`.​[file:2][file:3]

Returns:

- `valid = True` if no hard violations.
- `violations = [...]` list with file/field/description for each problem.​[file:3][file:4][file:7]

---

### aggregate_effects(build, data) -> list[active_effect]

Purpose:

- Collect all **active effect instances** for a build from all sources, prior to stacking and pillar math.​[file:3][file:4]

Sources:

- **Skills** – based on:
  - Which skills are slotted on bars.
  - Their `effects[]` entries and `timing` (for example, `"slotted"`, `"while_active"`, `"on_cast"`, `"on_hit"`, `"proc"`).​[file:2][file:3]

- **Sets** – based on:
  - Equipped pieces per `set_id`.
  - `sets.bonuses[].effects[]` at the active piece counts.​[file:2][file:3]

- **CP stars** – based on:
  - `cp_slotted` per tree.
  - `cp_stars[].effects[]` from `data/cp-stars.json`.​[file:2][file:3]

Output:

Each `active_effect` should include at least:

- `effect_id`
- `source` (for example, `"skill.deep_fissure"`, `"set.adept_rider"`, `"cp.ironclad"`)
- `timing` / trigger
- `target`
- `duration_seconds` (if applicable)​[file:3]

This list is the input to stacking rules, pillar computations, and any derived stat displays.​[file:3][file:4]

---

### validate_effect_stack_rules(effects, data) -> (normalized_effects, violations)

Purpose:

- Apply Major/Minor uniqueness rules and `stacks_with` exceptions to a list of active effects.​[file:3]

Behavior:

- Group effects by `stat` (from `data/effects.json`).
- For each group, enforce:
  - At most one effective `type: "major"` and one `type: "minor"` effect, unless `stacks_with` explicitly allows combinations.​[file:2][file:3]
- Produce:
  - `normalized_effects`: the canonical effect list for math after removing duplicates/overlaps.
  - `violations`: descriptions where stacking rules were violated (for example, multiple Major effects on the same stat without `stacks_with`).​[file:3]

---

### create_empty_build_template() -> build_json

Purpose:

- Return a skeleton build JSON object obeying all structural rules, used as a starting point for new builds.​[file:3][file:4]

Template must include:

- **Bars structure**
  - `bars.front` and `bars.back` with slots `1`–`5` and `"ULT"` (initially `null` or placeholder `skill_id`s).

- **Gear slots**
  - All 12 required gear slots present (initially empty items or `null`).

- **CP trees**
  - `cp_slotted.warfare`, `.fitness`, `.craft` as arrays of up to 4 `null` values.

- **Attributes and pillars**
  - Reasonable defaults (attributes set to 0; pillar configs empty or defaulted according to Data Model v1).​[file:2][file:3]

This function guarantees that any new build starts in a structurally valid shape before IDs are filled in.​[file:3][file:4]

---

These rules and function contracts are the backbone for all validators, exporters, and UI logic. Every tool that touches `builds/*.json` must adhere to them so that builds are structurally sound, effect math is consistent, and Markdown grids are reliable generated views over the computed data.​[file:1][file:3][file:4][file:7]
