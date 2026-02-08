# ESO Build Engine – Global Rules & Validation Checklist **docs/ESO-Build-Engine-Global-Rules.md**

## Purpose

Define the **structural and stacking rules** that apply to any build JSON (starting with Permafrost Marshal), for later implementation in Python validators.​

## 1. Bars & skills

* Exactly 2 bars: "front" and "back".
* Each bar has:
  + 5 normal slots: 1, 2, 3, 4, 5
  + 1 ultimate slot: "ULT"

**Constraints:**

* At most 1 skill per (bar, slot) pair.
* A given skill\_id may appear on both bars, but not more than once per bar.​
* All skill\_id values must exist in data/skills.json.

## 2. Gear layout & sets

**Required gear slots (12):**

* head, shoulder, chest, hands, waist, legs, feet, neck, ring1, ring2, front\_weapon, back\_weapon.

**Constraints:**

* Exactly 1 gear item per slot.
* At most **1 mythic set** equipped across all gear slots.
* Armor slots (head, shoulder, chest, hands, waist, legs, feet) must have weight ∈ {"light","medium","heavy"}.
* All set\_id values must exist in data/sets.json.​

**Soft check:**

* Number of pieces per set\_id should align with ESO set rules (e.g., no 7 pieces of a 5‑piece set).
* Soft checks produce warnings, not hard validation failures.

## 3. CP layout

* CP trees: exactly warfare, fitness, craft.

**Each tree:**

* Up to 4 slotted stars.
* No duplicated cp\_id within a tree.
* Only stars with slot\_type: "slottable" may appear in cp\_slotted.​
* All cp\_id values must exist in data/cp-stars.json.

## 4. Effect stacking rules (buffs/debuffs)

Effect semantics come from data/effects.json. The engine applies **Major/Minor uniqueness** per stat:

* For a given stat, at most:
  + One effective type: "major" effect.
  + One effective type: "minor" effect.

**Exceptions:**

* An effect may list other effect IDs in stacks\_with to allow stacking (e.g., unique + Major, or multiple unique effects).

**Goals:**

* Avoid double‑counting the same Major/Minor buff on a stat.
* Provide a canonical, normalized effect set for all math calculations (resist, damage taken, speed, etc.).

The exact math (what stat means and how value applies) is defined in data/effects.json and shared across skills, sets, and CP.

## 5. Validation and helper functions (Python contracts)

These functions define the expected behavior of Python validators and helpers under tools/.

## validate\_build\_structure(build, data) -> (valid: bool, violations: [string])

Checks:

* **Bars:**
  + Correct bar names ("front", "back").
  + Correct slots (1–5 + "ULT").
  + No duplicate slots per bar.
  + All skill\_id values exist in data/skills.json.​
* **Gear:**
  + All required gear slots present.
  + Exactly 1 item per slot.
  + Mythic constraint (≤ 1 mythic set across all gear).
  + Armor weights valid for armor slots.
  + All set\_id values exist in data/sets.json.​
* **CP:**
  + Exactly 3 trees: warfare, fitness, craft.
  + ≤ 4 slotted stars per tree.
  + No duplicates within a tree.
  + All CP IDs exist in data/cp-stars.json.
  + Only slot\_type: "slottable" IDs appear in cp\_slotted.​

Returns:

* valid = True if no hard violations.
* violations = [...] list with file/field/description for each problem.

## aggregate\_effects(build, data) -> [active\_effects]

Purpose:

* Collect all **active buffs/debuffs** for a build from all sources.

Sources:

* **Skills** – based on:
  + Which skills are slotted.
  + Their effects[].timing (e.g., "slotted", "while\_active", "on\_cast", "on\_hit", "proc").
* **Sets** – based on:
  + Equipped pieces per set\_id.
  + sets.bonuses[].effects[] at the active piece counts.
* **CP stars** – based on:
  + cp\_slotted per tree.
  + cp\_stars[].effects[].

Output:

* A flat list of effect instances with at least:
  + effect\_id
  + source (e.g., "skill.deep\_fissure", "set.adept\_rider", "cp.ironclad")
  + timing / trigger
  + target
  + duration\_seconds (if applicable)

This list is the input to the stacking rules and pillar computations.

## validate\_effect\_stack\_rules(effects, data) -> (normalized\_effects, violations)

Purpose:

* Apply Major/Minor uniqueness rules and stacks\_with exceptions to a list of active effects.

Behavior:

* Group effects by stat.
* For each group, enforce:
  + At most one effective type: "major" and one type: "minor" effect, unless stacks\_with explicitly allows combinations.
* Produce:
  + normalized\_effects: the canonical effect list to be used for math (after removing duplicates/overlaps).
  + violations: descriptions where stacking rules were violated (e.g., multiple Major buffs on the same stat without stacks\_with).

## create\_empty\_build\_template() -> build\_json

Purpose:

* Return a skeleton build JSON object obeying all structural rules, used as a starting point for new builds.

Template must include:

* Bars structure:
  + bars.front and bars.back with slots 1–5 and "ULT" (initially null or placeholder skill\_ids).
* Gear slots:
  + All 12 required gear slots present (initially empty).
* CP trees:
  + cp\_slotted.warfare, .fitness, .craft as arrays of up to 4 null values.
* Attributes and pillars:
  + Reasonable defaults (e.g., attributes set to 0, pillar configs empty or defaulted).

This function guarantees that any new build starts in a structurally valid shape before IDs are filled in.

These rules and function contracts are the backbone for all validators, exporters, and UI logic. All tools must adhere to them so that every build JSON is structurally sound, effect math is consistent, and Markdown grids are reliable generated views over the computed data.
