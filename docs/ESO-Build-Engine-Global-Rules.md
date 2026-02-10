# ESO Build Engine – Global Rules & Validation Checklist **docs/ESO-Build-Engine-Global-Rules.md**

## Purpose

Define the **structural and stacking rules** that apply to any build JSON (starting with Permafrost Marshal), and the Python contracts that validators and math tools under `tools/` must follow.

These rules are the normative source for build structure, CP layout, gear constraints, and effect stacking behavior; all tools and UIs must conform to them.

---

## 1. Bars & skills

- Exactly 2 bars: `front` and `back`.
- Each bar has:
  - 5 normal slots: `1`, `2`, `3`, `4`, `5`
  - 1 ultimate slot: `"ULT"`

**Constraints**

- At most 1 skill per `(bar, slot)` pair.
- A given `skillid` may appear on both bars, but not more than once per bar.
- All `skillid` values must exist in `data/skills.json`.
- Bars must be present as `build["bars"]["front"]` and `build["bars"]["back"]`, each an array of slot objects with `slot` and `skillid` fields.

---

## 2. Gear layout & sets

**Required gear slots (12)**

- `head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`, `neck`, `ring1`, `ring2`, `frontweapon`, `backweapon`.

**Constraints**

- Exactly 1 gear item per required slot.
- At most **1 mythic set** equipped across all gear slots.
- Armor slots (`head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`) must have `weight` ∈ `{ "light", "medium", "heavy" }`.
- All `setid` values must exist in `data/sets.json`.
- Gear records reference `sets.id` by `setid` only; no inline ESO math or tooltip text in gear.

**Soft checks**

- Number of pieces per `setid` should align with ESO set rules (for example, no 7 pieces of a 5‑piece set).
- Soft checks produce warnings, not hard validation failures.

---

## 3. CP layout

- CP trees: exactly `warfare`, `fitness`, `craft`.

**Each tree**

- Up to 4 slotted stars.
- No duplicated `cp` ID within a tree.
- Only stars with `slottype: "slottable"` may appear in `cpslotted`.
- All `cp` IDs must exist in `data/cp-stars.json`.
- CP layout is stored as `build["cpslotted"][tree] = [cp_or_null, ...]` with up to 4 entries per tree.

---

## 4. Effect stacking rules (buffs/debuffs)

Effect semantics come from `data/effects.json`. The engine applies **Major/Minor uniqueness** per stat (expressed via `stackingrule` and `stackswith` in the effect records):

- For a given `stat`, at most:
  - One effective Major‑tier effect.
  - One effective Minor‑tier effect.

**Exceptions**

- An effect may list other effect IDs in `stackswith` to allow stacking (for example, unique + Major, or multiple unique effects).

**Goals**

- Avoid double‑counting the same Major/Minor buff on a stat.
- Provide a canonical, normalized effect set for all math calculations (resist, damage taken, speed, etc.).

The exact math (what `stat` means and how its value applies) is defined in `data/effects.json` and shared across skills, sets, and CP.

**Logic‑driven terminology and functions**

- Effect fields, enums, and math helpers must use logic‑driven, system‑neutral terms, not ESO slang or tooltip text.
- Names must describe what they represent (for example, `movementspeedscalar`, `resistanceflat`, `healingovertimescalar`) instead of in‑game UI labels.
- ESO‑specific wording belongs only in human‑facing `name`/`description` fields in JSON, never as primary keys, enum values, or function names, so that effect math and stacking rules remain stable even if ESO terminology changes.

---

## 5. Validation and helper functions (Python contracts)

These function contracts define the expected behavior of Python validators and helpers under `tools/`. Implementations may have more parameters and internal helpers, but must satisfy these interfaces conceptually.

### validate_build(build_path) -> result_json

Implemented by `tools/validate_build.py`.

- Loads `data/skills.json`, `data/effects.json`, `data/sets.json`, `data/cp-stars.json` and the given build JSON.
- Unwraps v1 containers (`skills`, `sets`, `cpstars`) to lists.
- Runs structural checks and reference checks:
  - Bars:
    - `bars.front` and `bars.back` exist and are lists.
    - Each slot has a `skillid`.
  - Gear:
    - `gear` exists and is a list; each item has `slot`, `setid`, etc.
  - CP:
    - `cpslotted` exists with keys `warfare`, `fitness`, `craft`, each a list of up to 4 IDs or `null`.
  - References:
    - All `skillid` values exist in `skills.id`.
    - All `setid` values exist in `sets.id`.
    - All non‑null CP IDs in `cpslotted` exist in `cpstars.id`.

Output shape:

```json
{
  "build_id": "build.permafrostmarshal",
  "build_name": "Permafrost Marshal",
  "build_path": "builds/permafrost-marshal.json",
  "status": "OK" | "ERROR",
  "error_count": N,
  "errors": [
    { "field": "...", "message": "..." }
  ]
}
```

### aggregate_effects(build, data) -> list[active_effect]

Implemented by `tools/aggregate_effects.py` and mirrored inside `tools/compute_pillars.py`.

Purpose:

- Collect all **active effect instances** for a build from all sources, prior to stacking and pillar math.

Sources:

- **Skills** – based on:
  - Which skills are slotted on `bars.front` and `bars.back`.
  - Their `effects[]` entries and `timing` values (for example, `"slotted"`, `"whileactive"`, `"onhit"`).

- **Sets** – based on:
  - Equipped pieces per `setid`.
  - `sets.bonuses[].effects[]` at the active piece counts.

- **CP stars** – based on:
  - `cpslotted` per tree.
  - `cpstars[].effects[]` from `data/cp-stars.json`.

Output:

Each `active_effect` includes at least:

- `effect_id` – one of `effects.id` (for example, `buff.majorresolve`, `debuff.majorbreach`).
- `source` – ID of the source (for example, `"skill.deepfissure"`, `"set.adeptrider"`, `"cp.ironclad"`).
- `timing` – trigger classification (for example, `"slotted"`, `"whileactive"`, `"onhit"`).
- `target` – logical target type (`"self"`, `"enemy"`, `"group"`, etc.).
- `duration_seconds` – numeric duration or `null`.

This list is the input to stacking rules, pillar computations, and any derived stat displays.

### compute_pillars(build, data) -> dict

Implemented by `tools/compute_pillars.py`.

Purpose:

- Evaluate whether a build meets its pillar goals for resist, health, speed, HoTs, shields, and core combo, using the v1 data model.

Inputs:

- `build` – a v1 build object (`builds/permafrost-marshal.json` shape).
- `data` – dictionaries for `skills`, `effects`, `sets`, and `cpstars` loaded from `data/*.json`.

Behavior:

1. Calls `aggregate_effects(build, data)` to get a flat list of `active_effect` records.
2. Splits effects into two logical states:
   - `inactive` – baseline, always‑on effects (all `set.*` and `cp.*` sources, plus selected `skill.*` based on timing like `"whileactive"`).
   - `active` – full effect set available during a core window (all effects).
3. Reads `build["pillars"]` configuration:
   - `pillars.resist.targetresistshown` – numeric target for shown resist in the active state.
   - `pillars.health.focus` – for example, `"healthfirst"`.
   - `pillars.speed.profile` – for example, `"extremespeed"`.
   - `pillars.hots.minactivehots` – minimum distinct HoT effects.
   - `pillars.shield.minactiveshields` – minimum distinct shield effects.
   - `pillars.corecombo.skills` – list of required `skillid` values for the core combo.
4. Uses `data/effects.json` metadata (`stat`, `category`, `magnitudekind`, `magnitudevalue`) to compute pillar status:
   - **Resist** – sum contributions from effects with `stat` in `{"resistanceflat", "resist", "armor"}` and compare to `targetresistshown`.
   - **Health** – inspect `build.attributes.health` and any `maxhealth`/`healthmax` effects, and evaluate against `focus` (for example, `healthfirst` means all 64 attribute points in health).
   - **Speed** – collect movement‑related effects with `stat` in `{"movementspeedscalar", "movementspeedoutofcombatscalar", "mountedspeedscalar"}` and evaluate against `profile` (for example, `extremespeed` requires at least one such effect).
   - **HoTs** – count distinct effects where `category == "overtime"` and `stat == "healingovertimescalar"` and compare to `minactivehots`.
   - **Shields** – count distinct effects where `category == "shield"` and `stat` starts with `"shield"` and compare to `minactiveshields`.
   - **Core combo** – check that all `pillars.corecombo.skills` appear in the slotted `skillid` set across both bars.

Output shape:

```json
{
  "build_id": "...",
  "pillars": {
    "resist": {
      "inactive": { "meets_target": bool | null, "computed_resist_shown": int, "target_resist_shown": int | null, "sources": [...] },
      "active":   { ... }
    },
    "health": { "inactive": { ... }, "active": { ... } },
    "speed":  { "inactive": { ... }, "active": { ... } },
    "hots":   { "inactive": { ... }, "active": { ... } },
    "shield": { "inactive": { ... }, "active": { ... } },
    "core_combo": {
      "meets_target": bool | null,
      "required_skills": [ ... ],
      "missing_skills": [ ... ],
      "all_skills_slotted": bool | null
    }
  }
}
```

### validate_data_integrity() -> result_json

Implemented by `tools/validate_data_integrity.py`.

Purpose:

- Verify that the canonical data files under `data/` are self‑consistent and reference only known IDs.

Behavior:

- Loads `data/skills.json`, `data/effects.json`, `data/sets.json`, `data/cp-stars.json`.
- Unwraps v1 containers to lists: `skills`, `effects`, `sets`, `cpstars`.
- Checks:
  - **ID uniqueness and namespace**
    - `skills.id` are unique and start with `"skill."`.
    - `effects.id` are unique and start with one of `"buff."`, `"debuff."`, `"shield."`, `"hot."`.
    - `sets.id` are unique and start with `"set."`.
    - `cpstars.id` are unique and start with `"cp."`.
  - **Effect references**
    - All `skills[*].effects[*].effectid` values exist in `effects.id`.
    - All `sets[*].bonuses[*].effects[*]` (string or object) exist in `effects.id`.
    - All `cpstars[*].effects[*]` (string or object) exist in `effects.id`.

Output shape:

```json
{
  "status": "OK" | "ERROR",
  "error_count": N,
  "errors": [
    { "field": "...", "message": "..." }
  ]
}
```

### validate_effect_stack_rules(effects, data) -> (normalized_effects, violations)

(Not yet fully implemented in tools, but this is the intended contract.)

Purpose:

- Apply Major/Minor uniqueness rules and `stackswith` exceptions to a list of active effects.

Behavior:

- Group effects by `stat` (from `data/effects.json`).
- For each group, enforce:
  - At most one effective Major‑tier and one Minor‑tier effect, unless `stackswith` explicitly allows combinations.
- Produce:
  - `normalized_effects`: the canonical effect list for downstream math.
  - `violations`: descriptions where stacking rules were violated.

### create_empty_build_template() -> build_json

(Not yet fully implemented in tools, but this is the intended contract.)

Purpose:

- Return a skeleton build JSON object obeying all structural rules, used as a starting point for new builds.

Template must include:

- **Bars structure**
  - `bars.front` and `bars.back` with slots `1`–`5` and `"ULT"` (initially `null` or placeholder `skillid`s).

- **Gear slots**
  - All 12 required gear slots present (initially empty items or `null`).

- **CP trees**
  - `cpslotted.warfare`, `.fitness`, `.craft` as arrays of up to 4 `null` values.

- **Attributes and pillars**
  - Attributes set to 0 by default.
  - Pillar configs present with either empty objects or sensible defaults matching the v1 Data Model.

This function guarantees that any new build starts in a structurally valid shape before IDs are filled in.

---

These rules and function contracts are the backbone for all validators, exporters, and UI logic. Every tool that touches `builds/*.json` must adhere to them so that builds are structurally sound, effect math is consistent, and Markdown grids are reliable generated views over the computed data.
