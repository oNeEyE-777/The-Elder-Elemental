File: docs/ESO-Build-Engine-Global-Rules.md
Last-Updated: 2026-02-13 05:42:00Z

# ESO Build Engine Global Rules

## 1. Purpose

This document defines the **global rules** that apply across the ESO Build Engine:

- Structural rules for builds (bars, gear, Champion Points).
- Rules for effects and stacking (e.g. Major/Minor uniqueness).
- Expectations for tools (validation, aggregation, export).
- Project-wide constraints related to external data and ESO-Hub integration.

It must remain consistent with:

- `ESO-Build-Engine-Overview.md`
- `ESO-Build-Engine-Data-Model-v1.md`
- `ESO-Build-Engine-External-Data-Scope.md`
- `ESO-Build-Engine-External-Data-Runbook.md`
- `ESO-Build-Engine-ESO-Hub-Integration.md`
- `ESO-Build-Engine-Alignment-Control.md` [file:1024][file:1015][file:1022][file:1023][file:1021][file:1018]


## 2. Build structure rules

### 2.1 Bars

- Each build must define two bars:

  - `bars.front`
  - `bars.back`

- Each bar is an array of slot objects, each with:

  - `slot`: `"1"`, `"2"`, `"3"`, `"4"`, `"5"`, or `"ULT"`.
  - `skillid`: either:
    - A canonical skill ID (e.g. `skill.deepfissure`), or
    - `null` for an intentionally empty slot.

Rules:

- All bar slots must be valid slot labels; no duplicates on the same bar.
- Any non-null `skillid` must exist in `data/skills.json`. [file:1015][file:1018]
- Tools must treat missing or malformed `skillid` values as errors, except explicit `null`.


### 2.2 Gear

- Each build must define a `gear` array with exactly these 12 slots, each appearing once:

  - `head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`,
  - `neck`, `ring1`, `ring2`,
  - `frontweapon`, `backweapon`.

- Each gear item has:

  - `slot`: one of the above.
  - `setid`: a canonical set ID (e.g. `set.markofthepariah`), or `null` only for explicit test-dummy configurations.
  - `weight`: `"light"`, `"medium"`, `"heavy"` for armor slots; `null` for jewelry and weapons.
  - `trait`: string or `null`.
  - `enchant`: string or `null`. [file:1015][file:1018]

Rules:

- No missing gear slots.
- Any non-null `setid` must exist in `data/sets.json`.
- Tools must error on unknown slots or unknown set IDs.


### 2.3 Champion Points

- Each build must define `cpslotted`:

  - `cpslotted.warfare`
  - `cpslotted.fitness`
  - `cpslotted.craft`

- Each tree is an array of up to 4 entries:

  - Each entry is either:
    - A canonical CP ID (e.g. `cp.ironclad`), or
    - `null` for an unused slot.

Rules:

- No duplicates within a single tree (e.g. no double `cp.ironclad` in `warfare`).
- Any non-null CP ID must exist in `data/cp-stars.json`. [file:1015][file:1018]
- Tools must validate both structure and references.


### 2.4 Pillars configuration

- Each build may define a `pillars` object to express target criteria for:

  - `resist`
  - `health`
  - `speed`
  - `hots`
  - `shield`
  - `corecombo` [file:1015][file:1018]

- Typical fields:

  - `resist.targetresistshown`
  - `health.focus`
  - `speed.profile`
  - `hots.minactivehots`
  - `shield.minactiveshields`
  - `corecombo.skills` (array of `skill.*` IDs that must be present on bars)

Rules:

- Field names and shapes must match the v1 Data Model.
- Any skill IDs listed in `corecombo.skills` must exist in `data/skills.json`.
- Pillar evaluation tools (`compute_pillars.py`) are allowed to assume these shapes. [file:1015][file:1018][file:1019]


## 3. Effects and stacking rules

### 3.1 Effect identity

- All effects in `data/effects.json` must:

  - Have an `id` prefixed with:
    - `buff.`
    - `debuff.`
    - `hot.`
    - `shield.`

  - Have a `stat` field that:
    - Indicates the quantitative pillar dimension (`resist`, `hot`, `shield`, speed-related stats, etc.).
  - Have a `basevalue` numeric magnitude. [file:1015][file:1018]

Effects are referenced by:

- Skills: `skill.effects[].effectid`
- Sets: `set.bonuses[].effects[*]`
- CP stars: `cp.effects[]` [file:1015][file:1018]


### 3.2 Major/Minor and uniqueness

- Major/Minor buff/debuff rules (e.g. `buff.majorresolve`, `debuff.minorbreach`) follow ESO’s in-game stacking rules:

  - Only **one** instance of a given Major or Minor effect is considered active at a time per target, regardless of source.
  - Multiple sources providing the same Major/Minor effect do not stack their magnitude; they only add redundancy.

Tools must:

- Treat multiple instances of the same Major/Minor effect as one effective instance for pillar purposes.
- Aggregate them for diagnostics (e.g. showing that you have redundant sources), but not double-count their numeric contribution. [file:1016][file:1018]


### 3.3 Pillar stat keys

Pillar logic uses the `stat` field in `effects.json` to determine which effects contribute where. Canonical stat keys include: [file:1018][file:1019]

- Resist pillar:
  - `stat: "resist"`

- Health pillar:
  - `stat` in:
    - `"maxhealth"`
    - `"healthmax"`

- Speed pillar:
  - `stat` in:
    - `"movementspeed"`
    - `"movementspeedoutofcombat"`
    - `"mountedspeed"`

- HoTs pillar:
  - `stat: "hot"`

- Shield pillar:
  - `stat: "shield"`

Rules:

- Any effect intended to influence a pillar must use one of the recognized stat keys, or the pillar logic and this document must be updated together.
- Tools must not interpret ad-hoc or new stat keys without corresponding control-doc updates. [file:1018]


## 4. Tool behavior and contracts

### 4.1 No live external access

Global rule:

- No tool in `tools/`, and no code in `backend/` or `frontend/`, may perform live HTTP calls or use external APIs to fetch ESO game data. [file:1022][file:1023]

All external data (ESO-Hub, UESP, etc.) must arrive via offline snapshots and be written into `raw-imports/` before any tool processes it. [file:1022][file:1021][file:1023]


### 4.2 Validation tools

Key validation tools must:

- Operate only on local JSON files.
- Enforce schema and ID rules as defined in `ESO-Build-Engine-Data-Model-v1.md` and `ESO-Build-Engine-Alignment-Control.md`. [file:1015][file:1018]

Examples:

- `tools/validate_data_integrity.py`:
  - Checks `data/skills.json`, `data/effects.json`, `data/sets.json`, `data/cp-stars.json` for:
    - Unique IDs.
    - Correct namespace prefixes.
    - Valid `effectid` references. [file:1018]

- `tools/validate_build.py`:
  - Checks each build for:
    - Required top-level keys.
    - Valid bar structure.
    - Valid gear slots and set references.
    - Valid CP slotted references. [file:1016][file:1018]


### 4.3 Aggregation and pillars

- `tools/aggregate_effects.py` must:

  - Read builds from `builds/` and data from `data/`.
  - Produce a list of effect instances with:
    - `effectid` (canonical `effects.id`).
    - `source` (`skill.*`, `set.*`, or `cp.*`).
    - `timing`, `target`, `durationseconds`. [file:1016][file:1018]

- `tools/compute_pillars.py` must:

  - Use aggregated effects and pillar configuration to:
    - Determine active vs inactive effects.
    - Compute pillar metrics and statuses (met/not met).
  - Resolve effect metadata strictly via `effects.json` and the `stat` field—no ad-hoc logic. [file:1019][file:1018]

Rules:

- Any changes to aggregation or pillar math must remain consistent with this document and with `effects.json` stat definitions.
- Tools must not dynamically invent or reinterpret effect IDs or stat keys. [file:1018]


### 4.4 External import tools

External import tools (ESO-Hub and optional UESP) must:

- Live under `tools/`.
- Accept snapshot paths under `raw-imports/` as input.
- Produce `*.import-preview.json` files under `raw-imports/` in canonical v1 shapes.
- Never write directly to `data/*.json`. [file:1022][file:1023]

For ESO-Hub (primary path):

- `tools/import_skills_from_esohub.py`
- `tools/import_sets_from_esohub.py`
- `tools/import_cp_from_esohub.py` [file:1021][file:1023]

These must align with:

- Snapshot schemas in `ESO-Build-Engine-ESO-Hub-Integration.md`.
- Import flows in `ESO-Build-Engine-External-Data-Runbook.md`. [file:1021][file:1023]


### 4.5 Markdown export

- `tools/export_build_md.py` must:

  - Read canonical `data/*.json` and builds.
  - Render Markdown views of builds (bars, gear, CP, and optionally pillar summaries). [file:1016][file:1018]

Rules:

- Markdown exports are **views only**:
  - They must not be hand-edited.
  - They must not be treated as inputs for other tools.

Any change to Markdown layout must not affect data semantics.


## 5. External data alignment

### 5.1 ESO-Hub as external baseline

Global rule:

- ESO-Hub is the primary external baseline for:
  - Skill, set, and CP tooltips and naming.
  - The user-visible text used in the UI hover tooltips. [file:1022][file:1021][file:1024]

Tools and JSON must:

- Ensure that tooltip fields (`tooltipeffecttext`, `bonuses[].tooltipraw`, CP tooltip fields) originate from ESO-Hub snapshots, unless explicitly corrected.
- Not reword or renumber tooltips silently; any correction must be documented. [file:1021][file:1023]


### 5.2 Secondary sources and corrections

Secondary external sources (UESP, raw dumps, addons):

- Can be used to:
  - Validate ESO-Hub data.
  - Provide additional metadata (e.g. internal IDs, flags). [file:1022]

- Must **not** silently override ESO-Hub-derived text fields.
- Any corrections to canonical JSON based on secondary sources must be:
  - Reproducible from snapshot inputs.
  - Documented in either:
    - A corrections section in a control doc, or
    - A dedicated corrections file.

Tools must not implicitly trust secondary sources over ESO-Hub without this documentation.


## 6. Change management

Any change that affects:

- Build structure rules.
- Effect IDs or stat keys.
- Tool contracts (inputs/outputs/behaviors).
- External data flow assumptions (e.g. ESO-Hub vs other sources).

must be accompanied by:

- An update to this document (Global Rules).
- Updates to the relevant control docs:
  - `ESO-Build-Engine-Data-Model-v1.md`
  - `ESO-Build-Engine-Alignment-Control.md`
  - `ESO-Build-Engine-External-Data-Scope.md`
  - `ESO-Build-Engine-External-Data-Runbook.md`
  - `ESO-Build-Engine-ESO-Hub-Integration.md` [file:1015][file:1018][file:1022][file:1023][file:1021]

No code or JSON change is allowed to introduce new behavior that contradicts these rules without corresponding updates to the documentation and alignment validation.
