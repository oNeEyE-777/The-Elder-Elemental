# ESO Build Engine – Global Rules & Validation Checklist  
**docs/ESO-Build-Engine-Global-Rules.md**

## Purpose

Define the **structural and stacking rules** that apply to any build JSON under `builds/`, and the contracts that validators and math tools under `tools/` must follow. [file:356]

These rules are the normative source for:

- Build structure (bars, gear, CP, attributes, pillars).
- How builds reference canonical ESO data under `data/`.
- Effect stacking behavior for buffs, debuffs, HoTs, and shields.
- The shape of Python tool outputs that the backend and frontend may consume. [file:356]

The rules must support:

- **Many builds of all kinds**, not just Permafrost Marshal.
- Permafrost Marshal as a **reference example**, not a special case.
- **Large data imports** from ESO APIs and UESP into JSON, with low friction, as long as core fields remain valid. [file:356]

All tools (Python, backend, frontend) are **consumers** of these rules; none of them may introduce new game‑logic semantics that contradict `data/*.json` and the effect stacking rules defined here. [file:356]

---

## 0. Entity vs ID representation

Across all canonical data files in `data/`:

- Core entities are always represented as **objects** in arrays:
  - `skills[]` objects from `data/skills.json`.
  - `effects[]` objects from `data/effects.json`.
  - `sets[]` objects from `data/sets.json`.
  - `cp_stars[]` objects from `data/cp-stars.json`.
- Cross-file references are always represented as **string IDs**, never embedded objects:
  - `skills[].effects[].effect_id` must match some `effects[].id`.
  - `sets[].bonuses[].effects[]` entries must match `effects[].id`.
  - `cp_stars[].effects[]` entries must match `effects[].id`.

Forbidden patterns:

- Top-level arrays of bare ID strings in canonical data files (for example, `["cp.ironclad", "cp.duelists_rebuff"]` as CP stars).
- Embedding full effect objects inside skills, sets, or CP stars instead of referencing them by ID.

All Python tools, importers, and validators must assume this representation and treat any deviation as invalid data.

---

## 1. Bars & skills

- Exactly 2 bars: `front` and `back`. [file:356]

- Each bar has:

  - 5 normal slots: `1`, `2`, `3`, `4`, `5`
  - 1 ultimate slot: `"ULT"` [file:356]

**Constraints**

- At most 1 skill per `(bar, slot)` pair.
- A given `skill_id` may appear on both bars, but not more than once per bar.
- All `skill_id` values must exist in `data/skills.json`.
- Bars must be present as `build["bars"]["front"]` and `build["bars"]["back"]`, each an array of slot objects with `slot` and `skill_id` fields. [file:356]

---

## 2. Gear layout & sets

**Required gear slots (12)**

- `head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`, `neck`, `ring1`, `ring2`, `front_weapon`, `back_weapon`. [file:356]

**Constraints**

- Exactly 1 gear item per required slot.
- At most **1 mythic set** equipped across all gear slots.
- Armor slots (`head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`) must have `weight` ∈ `{ "light", "medium", "heavy" }`.
- All `set_id` values must exist in `data/sets.json`.
- Gear records reference `sets.id` by `set_id` only; no inline ESO math or tooltip text in gear. [file:356]

**Soft checks**

- Number of pieces per `set_id` should align with ESO set rules (for example, no 7 pieces of a 5‑piece set).
- Soft checks produce warnings, not hard validation failures. [file:356]

---

## 3. CP layout

- CP trees: exactly `warfare`, `fitness`, `craft`. [file:356]

**Each tree**

- Up to 4 slotted stars.
- No duplicated `cp_id` within a tree.
- Only stars with `slot_type: "slottable"` may appear in `cp_slotted`.
- All `cp_id` values must exist in `data/cp-stars.json`.
- CP layout is stored as `build["cp_slotted"][tree] = [cp_id_or_null, ...]` with up to 4 entries per tree. [file:356]

---

## 4. Effect stacking rules (buffs/debuffs)

Effect semantics come from `data/effects.json`. The engine applies **Major/Minor uniqueness** per stat: [file:356]

- For a given `stat`, at most:

  - One effective `type: "major"` effect.
  - One effective `type: "minor"` effect. [file:356]

**Exceptions**

- An effect may list other effect IDs in `stacks_with` to allow stacking (for example, unique + Major, or multiple unique effects). [file:356]

**Goals**

- Avoid double‑counting the same Major/Minor buff on a stat.
- Provide a canonical, normalized effect set for all math calculations (resist, damage taken, speed, etc.). [file:356]

The exact math (what `stat` means and how its value applies) is defined in `data/effects.json` and shared across skills, sets, and CP. [file:356]

**Logic‑driven terminology and functions**

- Effect fields, enums, and math helpers must use logic‑driven, system‑neutral terms, not ESO slang or tooltip text.
- Names must describe what they represent (`movement_speed_scalar`, `resistance_flat`, `state_active`) instead of in‑game labels like “buffed”, “unbuffed”, “Major Breach”, or “Major Resolve”.
- ESO‑specific wording belongs only in human‑facing `name`/`description` fields in JSON, never as primary keys, enum values, or function names, so that effect math and stacking rules remain stable even if ESO terminology changes.
- **No compression:** all effect IDs, field names, and stat keys must use lowercase `snake_case` with underscores between words (for example, `buff.major_resolve`, `debuff.major_breach`, `movement_speed_out_of_combat_scalar`), never compressed forms like `majorresolve` or `movementspeedscalar`.

---


## 5. Validation and helper functions (Python contracts)

These function contracts define the expected behavior of Python validators and helpers under `tools/`. Implementations may have more parameters and internal helpers, but must satisfy these interfaces conceptually. [file:356]

### 5.1 validate_build_structure(build, data) -> (valid: bool, violations: list[str])

Checks:

- **Bars**
  - Correct bar names (`"front"`, `"back"`).
  - Correct slots (`1`–`5` plus `"ULT"`).
  - No duplicate `slot` values per bar.
  - All `skill_id` values exist in `data["skills"]` from `data/skills.json`. [file:356]

- **Gear**
  - All required gear slots present.
  - Exactly 1 item per slot.
  - Mythic constraint (≤ 1 mythic set across all gear).
  - Armor weights valid for armor slots.
  - All `set_id` values exist in `data["sets"]` from `data/sets.json`. [file:356]

- **CP**
  - Exactly 3 trees: `warfare`, `fitness`, `craft`.
  - ≤ 4 slotted stars per tree.
  - No duplicates within a tree.
  - All CP IDs exist in `data["cp_stars"]` from `data/cp-stars.json`.
  - Only `slot_type: "slottable"` IDs appear in `cp_slotted`. [file:356]

Returns:

- `valid = True` if no hard violations.
- `violations = [...]` list with file/field/description for each problem. [file:356]

---

### 5.2 aggregate_effects(build, data) -> list[active_effect]

Purpose:

- Collect all **active effect instances** for a build from all sources, prior to stacking and pillar math. [file:356]

Sources:

- **Skills** – based on:
  - Which skills are slotted on bars.
  - Their `effects[]` entries and `timing` (for example, `"slotted"`, `"while_active"`, `"on_cast"`, `"on_hit"`, `"proc"`). [file:356]

- **Sets** – based on:
  - Equipped pieces per `set_id`.
  - `sets.bonuses[].effects[]` at the active piece counts. [file:356]

- **CP stars** – based on:
  - `cp_slotted` per tree.
  - `cp_stars[].effects[]` from `data/cp-stars.json`. [file:356]

Output:

Each `active_effect` should include at least:

- `effect_id`
- `source` (for example, `"skill.deep_fissure"`, `"set.adept_rider"`, `"cp.ironclad"`)
- `timing` / trigger
- `target`
- `duration_seconds` (if applicable) [file:356]

This list is the input to stacking rules, pillar computations, and any derived stat displays. [file:356]

---

### 5.3 validate_effect_stack_rules(effects, data) -> (normalized_effects, violations)

Purpose:

- Apply Major/Minor uniqueness rules and `stacks_with` exceptions to a list of active effects. [file:356]

Behavior:

- Group effects by `stat` (from `data/effects.json`).
- For each group, enforce:
  - At most one effective `type: "major"` and one `type: "minor"` effect, unless `stacks_with` explicitly allows combinations. [file:356]
- Produce:
  - `normalized_effects`: the canonical effect list for math after removing duplicates/overlaps.
  - `violations`: descriptions where stacking rules were violated (for example, multiple Major effects on the same stat without `stacks_with`). [file:356]

---

### 5.4 create_empty_build_template() -> build_json

Purpose:

- Return a skeleton build JSON object obeying all structural rules, used as a starting point for new builds. [file:356]

Template must include:

- **Bars structure**
  - `bars.front` and `bars.back` with slots `1`–`5` and `"ULT"` (initially `null` or placeholder `skill_id`s).

- **Gear slots**
  - All 12 required gear slots present (initially empty items or `null`).

- **CP trees**
  - `cp_slotted.warfare`, `.fitness`, `.craft` as arrays of up to 4 `null` values.

- **Attributes and pillars**
  - Reasonable defaults (attributes set to 0; pillar configs empty or defaulted according to Data Model v1). [file:356]

This function guarantees that any new build starts in a structurally valid shape before IDs are filled in. [file:356]

---

## 6. High-level tool contracts (concrete implementations)

The following concrete functions in `tools/` implement the contracts above for real builds and files.

### 6.1 validate_build(build_path) -> result_json

Implemented by `tools/validate_build.py`.

Responsibilities:

- Load canonical data:
  - `data/skills.json`
  - `data/effects.json`
  - `data/sets.json`
  - `data/cp-stars.json`
- Unwrap v1 containers (`skills`, `effects`, `sets`, `cpstars`/`cp_stars`) to lists.
- Load a build JSON from `build_path`.

Structural checks:

- **Bars**
  - `build["bars"]["front"]` and `build["bars"]["back"]` exist and are lists.
  - Each slot object has `slot` and `skillid` fields.
  - No duplicate `(bar, slot)` pairs.
  - Allowed slots: `"1"`, `"2"`, `"3"`, `"4"`, `"5"`, `"ULT"`.

- **Gear**
  - `build["gear"]` exists and is a list.
  - Exactly one item per required `slot`.
  - Mythic constraint (≤ 1 mythic set across all gear).
  - Armor weights valid for armor slots.

- **CP**
  - `build["cpslotted"]` exists with keys `warfare`, `fitness`, `craft`.
  - Each tree list length ≤ 4.
  - No duplicate CP IDs within a tree.

Reference checks:

- All non‑null `skillid` values exist in `skills[*].id`.
- All non‑null `setid` values exist in `sets[*].id`.
- All non‑null CP IDs in `cpslotted` exist in `cpstars[*].id`.

Output shape (conceptual `result_json`):

- `build_id`: build identifier (for example, `"build.permafrost_marshal"`).
- `build_name`: human-readable name (for example, `"Permafrost Marshal"`).
- `build_path`: path to the build JSON (for example, `"builds/permafrost-marshal.json"`).
- `status`: `"OK"` or `"ERROR"`.
- `error_count`: integer count of hard errors.
- `errors`: list of objects `{ "field": "...", "message": "..." }`.

### 6.2 aggregate_effects(build, data) -> list[active_effect]

Implemented by `tools/aggregate_effects.py` and mirrored in `tools/compute_pillars.py`.

Purpose:

- Collect all **active effect instances** for a build from all sources, prior to stacking and pillar math.

Sources:

- **Skills**
  - Which skills are slotted on `bars.front` and `bars.back`.
  - Their `effects[]` entries and `timing` (for example, `"slotted"`, `"whileactive"`, `"onhit"`).

- **Sets**
  - Equipped pieces per `setid`.
  - `sets.bonuses[*].effects[*]` at the active piece counts.

- **CP stars**
  - `cpslotted` per tree.
  - `cpstars[*].effects[*]` from `data/cp-stars.json`.

Output:

Each `active_effect` includes at least:

- `effect_id` – one of `effects[*].id` (for example, `buff.major_resolve`, `debuff.major_breach`).
- `source` – ID of the source (for example, `"skill.deep_fissure"`, `"set.adept_rider"`, `"cp.ironclad"`).
- `timing` – trigger classification (`"slotted"`, `"whileactive"`, `"onhit"`, etc.).
- `target` – logical target type (`"self"`, `"enemy"`, `"group"`, etc.).
- `duration_seconds` – numeric duration or `null`.

This list is the input to stacking rules, pillar computations, and any derived stat displays.

### 6.3 validate_effect_stack_rules(effects, data) -> normalized_effects, violations

Implemented by `tools/aggregate_effects.py` or a dedicated `tools/validate_effect_stack.py`.

Purpose:

- Apply Major/Minor uniqueness rules and `stackswith` exceptions to a list of active effects.

Behavior:

- Group effects by `stat` from `data/effects.json`.
- For each group, enforce:
  - At most one effective type `"major"` and one type `"minor"` effect, unless `stackswith` explicitly allows combinations.
- Produce:
  - `normalized_effects` – the canonical effect list for math after removing duplicates and overlapping effects.
  - `violations` – human-readable descriptions where stacking rules were violated (for example, multiple Major effects on the same stat without `stackswith`).

This keeps downstream math consumers working from a single, de-duplicated set of effects per stat.

### 6.4 create_empty_build_template() -> build_json

Implemented by `tools/create_empty_build_template.py`.

Purpose:

- Return a skeleton build JSON object obeying all structural rules, used as a starting point for new builds.

Template must include:

- **Bars structure**
  - `bars.front` and `bars.back` with slots `"1"`–`"5"` and `"ULT"` (initially `null` or placeholder `skillid`s).

- **Gear slots**
  - All 12 required gear slots present (`head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`, `neck`, `ring1`, `ring2`, `frontweapon`, `backweapon`), initially empty items or `null`.

- **CP trees**
  - `cpslotted.warfare`, `.fitness`, `.craft` as arrays of up to 4 `null` values.

- **Attributes and pillars**
  - Reasonable defaults (attributes set to 0; pillar configs empty or defaulted according to Data Model v1).

This function guarantees that any new build starts in a structurally valid shape before IDs are filled in.
