# ESO Build Engine – Data & Tool Alignment Control

This document freezes the alignment rules between `data/`, `builds/`, and `tools/` so future changes do not reintroduce schema drift.

It is normative alongside:

- `ESO-Build-Engine-Overview.md`
- `ESO-Build-Engine-Data-Model-v1.md`
- `ESO-Build-Engine-Global-Rules.md`
- `ESO-Build-Engine-Data-Center-Scope.md`
- `ESO-Build-Engine-Data-Center-Tool-Checklist.md`
- `ESO-Build-Engine-Runbook.md`

---

## 1. Canonical ID prefixes

The following prefixes are canonical and must appear exactly as shown in all JSON and tools:

- Skills: `skill.` (e.g. `skill.deep_fissure`)
- Effects: `buff.`, `debuff.`, `shield.`, `hot.` (e.g. `buff.major_resolve`, `hot.resolving_vigor`)
- Sets: `set.` (e.g. `set.mark_of_the_pariah`)
- Champion Points: `cp.` (e.g. `cp.ironclad`)
- Builds: `build.` (e.g. `build.permafrost_marshal`)

No tool may add these prefixes at runtime or map “bare” IDs to prefixed IDs.

---

## 2. Canonical data file schemas (`data/*.json`)

All data files live under `data/` and follow these shapes.

### 2.1 `data/skills.json`

Top-level:

- Either a bare array of skill objects, or:
- An object: `{ "skills": [ ... ] }`

Each skill:

- `id` (string, `skill.*`)
- `name` (string)
- `tooltip_effect_text` (string, optional)
- `effects` (array of effect entries)

Each effect entry in `skill.effects`:

- `effect_id` (string, must match an `effects.id`)
- `timing` (string, e.g. `on_hit`, `on_cast`, `while_active`)
- `target` (string, e.g. `self`, `enemy`, `group`, `self_area`)
- `duration_seconds` (number or null)

No aliases such as `effectid` or `durationseconds` are allowed.

### 2.2 `data/effects.json`

Top-level:

- Either a bare array of effect objects, or:
- An object: `{ "effects": [ ... ] }`

Each effect:

- `id` (string, starts with `buff.`, `debuff.`, `shield.`, or `hot.`)
- `name` (string, optional)
- `stat` (string, canonical stat key, see section 3)
- `base_value` (number; used as the magnitude for pillar math)
- Additional metadata fields as needed (e.g. tags, notes).

IDs must be unique within the file.

### 2.3 `data/sets.json`

Top-level:

- Either a bare array of set objects, or:
- An object: `{ "sets": [ ... ] }`

Each set:

- `id` (string, `set.*`)
- `name` (string)
- `bonuses` (array of bonus objects)

Each bonus:

- `pieces` (integer, required piece count)
- `effects` (array)

Each entry in `bonus.effects`:

- Preferred canonical form: string `effect_id` that matches `effects.id`.
- Optional richer form: object with:
  - `effect_id` (string, matches `effects.id`)
  - `timing` (string, overrides set-level timing for that effect)
  - `duration_seconds` (number or null)
  - `target` (string)

Tooling must accept both forms but must not accept any `effectid` aliases.

### 2.4 `data/cp-stars.json`

Top-level:

- Either a bare array of CP star objects, or:
- An object: `{ "cp_stars": [ ... ] }`

Each CP star:

- `id` (string, `cp.*`)
- `name` (string)
- `tree` (string: `warfare`, `fitness`, or `craft`)
- `effects` (array)

Each entry in `cp_star.effects`:

- Preferred canonical form: string `effect_id` matching `effects.id`.
- Optional richer form: object with:
  - `effect_id` (string, matches `effects.id`)
  - `timing` (string)
  - `duration_seconds` (number or null)
  - `target` (string)

No alias keys such as `effectid` are allowed.

---

## 3. Canonical stat keys used by pillars

Pillar evaluation in `tools/compute_pillars.py` uses `effects.json` via the `stat` field and `base_value` magnitude. [file:581]

Canonical `stat` values:

- Resist pillar:
  - `stat == "resist"`

- Health pillar:
  - `stat` in:
    - `"maxhealth"`
    - `"healthmax"`

- Speed pillar:
  - `stat` in:
    - `"movement_speed"`
    - `"movement_speed_out_of_combat"`
    - `"mounted_speed"`

- HoTs pillar:
  - `stat == "hot"`

- Shield pillar:
  - `stat == "shield"`

Any new effect intended to influence these pillars must use one of the stat keys above, or pillar logic and this doc must be updated together.

---

## 4. Canonical build schema (`builds/*.json`)

All builds live in `builds/` and follow the v1 Data Model. [file:584]

### 4.1 Top-level fields

Required:

- `id` (string, `build.*`)
- `name` (string)
- `bars` (object)
- `gear` (array)
- `cp_slotted` (object)

Common additional fields (encouraged but not required by validators):

- `class_core` (string)
- `sub_classes` (array of strings)
- `cp_total` (integer)
- `role_tags` (array of strings)
- `attributes` (object with `health`, `magicka`, `stamina`)
- `pillars` (object, see 4.4)

### 4.2 Bars

`bars`:

- Object with keys: `"front"`, `"back"`.

Each bar (`bars.front`, `bars.back`):

- Array of slot objects.

Each slot object:

- `slot`:
  - `"1"`, `"2"`, `"3"`, `"4"`, `"5"`, or `"ULT"` (string form).
- `skill_id`:
  - String (must exist in `skills.id`), or `null` for an empty slot.

Validators and exporters treat any missing or non-string `skill_id` as invalid (except explicit `null`). [file:578][file:580]

### 4.3 Gear

`gear`:

- List of gear items.

Each gear item:

- `slot` (string, one of):
  - `"head"`, `"shoulder"`, `"chest"`, `"hands"`, `"waist"`, `"legs"`, `"feet"`,
    `"neck"`, `"ring1"`, `"ring2"`, `"front_weapon"`, `"back_weapon"`
- `set_id`:
  - String `set.*`, or `null` for an intentionally empty slot (test-dummy only).
- `weight`:
  - `"light"`, `"medium"`, `"heavy"` for armor slots, `null` for jewelry/weapons.
- `trait` (string or `null`)
- `enchant` (string or `null`)

All 12 canonical slots must be present exactly once. [file:576][file:584]

### 4.4 Champion Points

`cp_slotted`:

- Object with keys: `"warfare"`, `"fitness"`, `"craft"`.

Each tree:

- Array of up to 4 entries.
- Each entry:
  - String `cp.*` (must exist in `cp_stars.id`), or
  - `null` (unused slot).

Duplicates within a tree are not allowed. [file:576][file:586]

### 4.5 Pillars configuration

`pillars` (optional but required for pillar evaluation):

- `resist`:
  - `target_resist_shown` (number; target combined resist value).

- `health`:
  - `focus` (string; e.g. `"health_first"`).

- `speed`:
  - `profile` (string; e.g. `"extreme_speed"`).

- `hots`:
  - `min_active_hots` (integer; minimum unique HoT effects required).

- `shield`:
  - `min_active_shields` (integer; minimum unique shield effects required).

- `core_combo`:
  - `skills` (array of `skill.*` IDs that must be slotted somewhere on the bars).

Key names must match these exactly; no alternate forms such as `minactivehots` or `targetresistshown` are permitted at the schema level. [file:571][file:581]

---

## 5. Tool behavior and expectations

### 5.1 Validators

- `tools/validate_data_integrity.py`:
  - Enforces:
    - Unique IDs per file.
    - Correct namespace prefixes.
    - All `effect_id` references exist in `effects.id`.
  - Operates on:
    - `skills.json`, `effects.json`, `sets.json`, `cp-stars.json`. [file:575]

- `tools/validate_build_test.py`:
  - Validates `builds/test-dummy.json` against:
    - Structural rules (top-level keys, bars, gear, CP layout).
    - Canonical cross-references to skills, sets, and CP stars. [file:576]

- `tools/validate_build.py`:
  - Validates arbitrary builds (e.g. `builds/permafrost-marshal.json`) against the same rules. [file:578]

All three validators assume the canonical schemas in sections 2–4 and must not implement compatibility aliases. [file:571]

### 5.2 Aggregation and pillars

- `tools/aggregate_effects.py`:
  - Canonical `aggregate_effects(build, data)` implementation.
  - Returns a list of effect instances:
    - `effect_id` (canonical `effects.id`)
    - `source` (`skill.*`, `set.*`, or `cp.*`)
    - `timing`
    - `target`
    - `duration_seconds` [file:579]

- `tools/compute_pillars.py`:
  - Uses `aggregate_effects(build, data)` to compute:
    - Inactive vs active effect sets.
    - Pillar statuses for resist, health, speed, HoTs, shield, core combo. [file:581]
  - Resolves effect metadata via `effects.json` with:
    - Direct lookup on `effect_id`.
    - No runtime mapping of “bare” IDs or prefix injection.

Any change to aggregation or pillar math must remain consistent with this document and `effects.json` stat definitions. [file:571][file:567]

### 5.3 Markdown export

- `tools/export_build_md.py`:
  - Renders build bars, gear, and Champion Points into Markdown.
  - Assumes the canonical build schema described in section 4. [file:580]

Markdown exports are views only and must not be edited by hand. [file:571]

---

## 6. Import safety and promotion process

### 6.1 Importers

The UESP importers:

- `tools/import_skills_from_uesp.py`
- `tools/import_sets_from_uesp.py`
- `tools/import_cp_from_uesp.py`

Must:

- Write only to `raw-imports/`:

  - `raw-imports/skills.import-preview.json`
  - `raw-imports/sets.import-preview.json`
  - `raw-imports/cp-stars.import-preview.json`

- Never write directly to any `data/*.json` file. [file:571][file:572][file:573][file:574]

### 6.2 Promotion from `raw-imports/` to `data/`

Promotion is a manual, gated process:

1. Run the full validation chain on the candidate data and builds:

   In VS Code integrated terminal (recommended):

   - cd C:\Projects\The-Elder-Elemental
   - python tools\validate_build_test.py
   - python tools\validate_build.py builds\permafrost-marshal.json
   - python tools\validate_data_integrity.py
   - python tools\aggregate_effects.py builds\permafrost-marshal.json
   - python tools\compute_pillars.py builds\permafrost-marshal.json
   - python tools\export_build_md.py builds\permafrost-marshal.json

2. Confirm:

- All commands report status: "OK" and zero hard errors.
- Aggregated effects and pillar outputs look sane for Permafrost Marshal and Test Dummy.
- New data respects sections 2–4 of this document. [file:571][file:582][file:583]

3. Manually move or integrate raw-imports/* into data/*.json with:

- Explicit Git diffs reviewed.
- No direct editing of data/*.json without validator reruns. [file:571]

## 7. Control and change management

This document is the control point for:

- Canonical field names.
- Canonical stat keys.
- ID prefixes and reference shapes.
- Import and promotion rules. [file:571]

If any tool or JSON format needs to change:

- Update this document and the relevant v1 model/overview docs first.
- Then update the tools and data to match.
- Finally, rerun the validation and export chain listed in section 6.2. [file:571]

No tool is allowed to introduce new aliases, fallback mappings, or schema drift that contradicts this document. Any such change must be accompanied by an update here and in the core model docs. [file:571]
