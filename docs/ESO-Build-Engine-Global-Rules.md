\# ESO Build Engine – Global Rules \& Validation Checklist \*\*docs/ESO-Build-Engine-Global-Rules.md\*\*



\## Purpose



Define the \*\*structural and stacking rules\*\* that apply to any build JSON (starting with Permafrost Marshal), and the Python contracts that validators and math tools under `tools/` must follow.\[file:3]\[file:4]



These rules are the normative source for build structure, CP layout, gear constraints, and effect stacking behavior; all tools and UIs must conform to them.\[file:1]\[file:3]\[file:4]



---



\## 1. Bars \& skills



\- Exactly 2 bars: `front` and `back`.

\- Each bar has:

&nbsp; - 5 normal slots: `1`, `2`, `3`, `4`, `5`

&nbsp; - 1 ultimate slot: `"ULT"`\[file:2]\[file:3]



\*\*Constraints\*\*



\- At most 1 skill per `(bar, slot)` pair.

\- A given `skill\_id` may appear on both bars, but not more than once per bar.

\- All `skill\_id` values must exist in `data/skills.json`.\[file:2]\[file:3]

\- Bars must be present as `build\["bars"]\["front"]` and `build\["bars"]\["back"]`, each an array of slot objects with `slot` and `skill\_id` fields.\[file:2]\[file:3]



---



\## 2. Gear layout \& sets



\*\*Required gear slots (12)\*\*



\- `head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`, `neck`, `ring1`, `ring2`, `front\_weapon`, `back\_weapon`.\[file:2]\[file:3]



\*\*Constraints\*\*



\- Exactly 1 gear item per required slot.

\- At most \*\*1 mythic set\*\* equipped across all gear slots.

\- Armor slots (`head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`) must have `weight` ∈ `{ "light", "medium", "heavy" }`.

\- All `set\_id` values must exist in `data/sets.json`.\[file:2]\[file:3]

\- Gear records reference `sets.id` by `set\_id` only; no inline ESO math or tooltip text in gear.\[file:2]\[file:3]



\*\*Soft checks\*\*



\- Number of pieces per `set\_id` should align with ESO set rules (e.g., no 7 pieces of a 5‑piece set).

\- Soft checks produce warnings, not hard validation failures.\[file:3]



---



\## 3. CP layout



\- CP trees: exactly `warfare`, `fitness`, `craft`.\[file:2]\[file:3]



\*\*Each tree\*\*



\- Up to 4 slotted stars.

\- No duplicated `cp\_id` within a tree.

\- Only stars with `slot\_type: "slottable"` may appear in `cp\_slotted`.

\- All CP IDs must exist in `data/cp-stars.json`.\[file:2]\[file:3]

\- CP layout is stored as `build\["cp\_slotted"]\[tree] = \[cp\_id\_or\_null, ...]` with up to 4 entries per tree.\[file:2]\[file:3]



---



\## 4. Effect stacking rules (buffs/debuffs)



Effect semantics come from `data/effects.json`. The engine applies \*\*Major/Minor uniqueness\*\* per stat:\[file:2]\[file:3]



\- For a given `stat`, at most:

&nbsp; - One effective `type: "major"` effect.

&nbsp; - One effective `type: "minor"` effect.



\*\*Exceptions\*\*



\- An effect may list other effect IDs in `stacks\_with` to allow stacking (for example, unique + Major, or multiple unique effects).\[file:2]\[file:3]



\*\*Goals\*\*



\- Avoid double‑counting the same Major/Minor buff on a stat.

\- Provide a canonical, normalized effect set for all math calculations (resist, damage taken, speed, etc.).\[file:2]\[file:3]



The exact math (what `stat` means and how `value` applies) is defined in `data/effects.json` and shared across skills, sets, and CP.\[file:2]\[file:3]



---



\## 5. Validation and helper functions (Python contracts)



These function contracts define the expected behavior of Python validators and helpers under `tools/`. Implementations may have more parameters and internal helpers, but must satisfy these interfaces conceptually.\[file:3]\[file:4]\[file:7]



\### validate\_build\_structure(build, data) -> (valid: bool, violations: list\[str])



Checks:



\- \*\*Bars\*\*

&nbsp; - Correct bar names (`"front"`, `"back"`).

&nbsp; - Correct slots (`1`–`5` plus `"ULT"`).

&nbsp; - No duplicate `slot` values per bar.

&nbsp; - All `skill\_id` values exist in `data\["skills"]` from `data/skills.json`.\[file:2]\[file:3]



\- \*\*Gear\*\*

&nbsp; - All required gear slots present.

&nbsp; - Exactly 1 item per slot.

&nbsp; - Mythic constraint (≤ 1 mythic set across all gear).

&nbsp; - Armor weights valid for armor slots.

&nbsp; - All `set\_id` values exist in `data\["sets"]` from `data/sets.json`.\[file:2]\[file:3]



\- \*\*CP\*\*

&nbsp; - Exactly 3 trees: `warfare`, `fitness`, `craft`.

&nbsp; - ≤ 4 slotted stars per tree.

&nbsp; - No duplicates within a tree.

&nbsp; - All CP IDs exist in `data\["cp\_stars"]` from `data/cp-stars.json`.

&nbsp; - Only `slot\_type: "slottable"` IDs appear in `cp\_slotted`.\[file:2]\[file:3]



Returns:



\- `valid = True` if no hard violations.

\- `violations = \[...]` list with file/field/description for each problem.\[file:3]\[file:4]\[file:7]



---



\### aggregate\_effects(build, data) -> list\[active\_effect]



Purpose:



\- Collect all \*\*active buffs/debuffs\*\* for a build from all sources, prior to stacking and pillar math.\[file:3]\[file:4]



Sources:



\- \*\*Skills\*\* – based on:

&nbsp; - Which skills are slotted on bars.

&nbsp; - Their `effects\[]` entries and `timing` (for example, `"slotted"`, `"while\_active"`, `"on\_cast"`, `"on\_hit"`, `"proc"`).\[file:2]\[file:3]

\- \*\*Sets\*\* – based on:

&nbsp; - Equipped pieces per `set\_id`.

&nbsp; - `sets.bonuses\[].effects\[]` at the active piece counts.\[file:2]\[file:3]

\- \*\*CP stars\*\* – based on:

&nbsp; - `cp\_slotted` per tree.

&nbsp; - `cp\_stars\[].effects\[]` from `data/cp-stars.json`.\[file:2]\[file:3]



Output:



Each `active\_effect` should include at least:



\- `effect\_id`

\- `source` (for example, `"skill.deep\_fissure"`, `"set.adept\_rider"`, `"cp.ironclad"`)

\- `timing` / trigger

\- `target`

\- `duration\_seconds` (if applicable)\[file:3]



This list is the input to stacking rules, pillar computations, and any derived stat displays.\[file:3]\[file:4]



---



\### validate\_effect\_stack\_rules(effects, data) -> (normalized\_effects, violations)



Purpose:



\- Apply Major/Minor uniqueness rules and `stacks\_with` exceptions to a list of active effects.\[file:3]



Behavior:



\- Group effects by `stat` (from `data/effects.json`).

\- For each group, enforce:

&nbsp; - At most one effective `type: "major"` and one `type: "minor"` effect, unless `stacks\_with` explicitly allows combinations.\[file:2]\[file:3]

\- Produce:

&nbsp; - `normalized\_effects`: the canonical effect list for math after removing duplicates/overlaps.

&nbsp; - `violations`: descriptions where stacking rules were violated (for example, multiple Major buffs on the same stat without `stacks\_with`).\[file:3]



---



\### create\_empty\_build\_template() -> build\_json



Purpose:



\- Return a skeleton build JSON object obeying all structural rules, used as a starting point for new builds.\[file:3]\[file:4]



Template must include:



\- \*\*Bars structure\*\*

&nbsp; - `bars.front` and `bars.back` with slots `1`–`5` and `"ULT"` (initially `null` or placeholder `skill\_id`s).



\- \*\*Gear slots\*\*

&nbsp; - All 12 required gear slots present (initially empty items or `null`).



\- \*\*CP trees\*\*

&nbsp; - `cp\_slotted.warfare`, `.fitness`, `.craft` as arrays of up to 4 `null` values.



\- \*\*Attributes and pillars\*\*

&nbsp; - Reasonable defaults (attributes set to 0; pillar configs empty or defaulted according to Data Model v1).\[file:2]\[file:3]



This function guarantees that any new build starts in a structurally valid shape before IDs are filled in.\[file:3]\[file:4]



---



These rules and function contracts are the backbone for all validators, exporters, and UI logic. Every tool that touches `builds/\*.json` must adhere to them so that builds are structurally sound, effect math is consistent, and Markdown grids are reliable generated views over the computed data.\[file:1]\[file:3]\[file:4]\[file:7]



