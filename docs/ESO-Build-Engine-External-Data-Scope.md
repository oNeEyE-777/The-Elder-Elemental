# ESO Build Engine – External Data Alignment Scope

## 1. Objective

Define and lock the authoritative external data sources (ESO client, Lua API, UESP, community APIs) and their formats that will feed the Build Engine’s `/data/*.json` layer, then align internal JSON schemas and IDs to those sources so a future “mass data dump” is mechanical instead of bespoke. [web:422][web:432]

Goals:

- One **canonical source of record** for skills, effects, sets, CP stars, etc.  
- `/data/*.json` structures that are **lossless projections** of that source at the level of tooltips and math-driving stats.  
- Python tools that assume **direct foreign-key matches** between build references and that data (no mapping layers or “guessing”).  

This scope explicitly supersedes any ad-hoc ID or field naming that cannot be traced back to the chosen ESO data sources.

The guiding operational rule is:

> External ESO data is ingested **offline** as versioned snapshots after each official patch, with no live call-outs at runtime, and only after upstream data (UESP) has been updated and stabilized for that patch. [web:422][web:432]

---

## 2. External data sources

### 2.1 UESP Global Data (primary canonical source)

**Description**

UESP’s ESO Data sites and APIs (e.g., `esodata.uesp.net`, `esoapi.uesp.net`) provide versioned global exports built from ESO client files and Lua logs via UESP’s tooling (`EsoExtractData`, `uesp-esolog`, `uespLog` addon). [web:422][web:432][web:430][web:426]

**Why this is canonical for the Build Engine**

- Includes **full tooltip text** (raw and processed) for skills, sets, CP stars, and buffs/effects. [web:432][web:423]  
- Exposes **math-driving stats**: ability IDs, set IDs, magnitudes, scaling coefficients, and category flags that determine how ESO applies each effect. [web:432][web:430]  
- Tracks **ESO API versions** per patch (e.g., `v101047`), enabling patch-aligned snapshots. [web:432]  

**Evaluation tasks**

- Identify the latest ESO API version we plan to track (e.g., `v101047+`) as the current target. [web:432]  
- For that version, inspect the relevant UESP exports:

  - Skill tables: names, `abilityId`, costs, cooldowns, durations, raw tooltips, flagged effects. [web:432][web:423]  
  - Set item tables: `setId`, set name, bonus descriptions, bonus conditions. [web:423][web:432]  
  - Buff/debuff/effect representations: Major/Minor names, internal IDs, magnitudes, and type flags. [web:429][web:432]  
  - CP star tables (if available): star IDs, names, tooltips, numerical effects. [web:432]

- Decide which UESP artifacts to consume:

  - **Preferred:** UESP’s raw DB exports (CSV/TSV/SQL-like) and transform locally into `/data/*.json`. [web:430][web:426]  
  - Optionally: UESP’s pre-processed JSON-like endpoints (if/when they exist for certain domains), but still funneled through the same local import pipeline.

**Reference URLs**

- ESO API versions index (UESP): [https://esoapi.uesp.net/index.html](https://esoapi.uesp.net/index.html) [web:422]  
- Versioned ESO data exports (UESP): [https://esodata.uesp.net](https://esodata.uesp.net) [web:432]


### 2.2 ESO Lua API / SavedVariables (indirect, via UESP; optional direct use for gaps)

**Description**

ESO’s Lua API exposes in-game data (abilities, buffs, sets) to addons. UESP’s `uespLog` addon and associated tooling already collect this data via SavedVariables and upload it to UESP’s processing pipeline. [web:425][web:424][web:426]

**Baseline policy**

- The Build Engine does **not** call the Lua API or SavedVariables directly at runtime.  
- By default, it relies on **UESP’s processed exports** as the reflection of ESO’s client and Lua API data. [web:422][web:432]

**Evaluation tasks**

- Confirm that UESP exports provide all the **tooltips and math-driving values** we need for:
  - Effects (IDs, magnitudes, categories).  
  - Skills (abilityId, resource costs, base durations).  
  - Sets (setId, bonus magnitudes).  
  - CP stars.  

- Determine if there are **gaps** (e.g., brand-new systems, scribing, or subclass interactions) where UESP data is insufficient or delayed.

  - If gaps exist and are material to build math, consider a **small, focused custom addon** plus SavedVariables parser to record only those missing pieces, still feeding into the same offline import pipeline.

- Document which Lua-side identifiers (e.g., `abilityId`, buff IDs, internal set IDs) will be stored under `external_ids.*` fields in our JSON and which remain UESP-only.

### 2.3 Community APIs / Tools (secondary / gap fillers)

These are not primary canonical sources but may inform schema design and provide cross-checks:

- ESO-Hub / build editors: skill and set semantics, buff naming conventions. [web:429][web:431]  
- Combat log tools (Combat Metrics, ESO Logs, etc.): how buffs, debuffs, sets appear in logs and real encounters. [web:428][web:434]  

**Evaluation tasks**

- Confirm we **do not** depend on these for authoritative numbers or IDs.  
- Borrow naming patterns and UX conventions only when they do not conflict with ESO/UESP identifiers and the mapping spec.


### 2.4 UESP Build Editor as conceptual guide (docs only)

The UESP ESO Build Editor documentation provides a clear, user-facing breakdown of build components and computed outputs (Items/Sets, Skills, Buffs, CP, Raw Data, Computed Statistics). Although we **do not** consume the Build Editor itself as a data source, we treat its structure as a conceptual guide for how to slice and present data in the ESO Build Engine. [web:422]

In particular:

- The Build Editor’s **Items/Sets tab** maps conceptually to our `data/sets.json` and gear sections in `builds/*.json`.  
- The **Skills tab** maps to `data/skills.json` and bar layouts in `builds/*.json`.  
- The **Buffs tab** maps to `data/effects.json`, where buff/debuff/HoT/shield effects are defined.  
- The **CPs tab** maps to `data/cp-stars.json` and CP layouts in `builds/*.json`.  
- The **Raw Data** and **Computed Statistics** tabs align conceptually with our Python tools (`aggregate_effects.py`, `compute_pillars.py`, future simulators) and any exported summaries. [file:376][file:377][file:389]

Design directive:

- Use the UESP Build Editor help pages as **UX and concept references** when deciding how to group or label data and computed outputs.  
- Use `esodata.uesp.net` and `esoapi.uesp.net` as the **only authoritative machine-readable data sources** for skills, sets, effects, and CP stars. [web:432][web:422]

---

## 3. Canonical ID and naming strategy

This section locks the ID conventions the engine must follow after alignment with ESO/UESP exports.

### 3.1 Core entity IDs

To support mechanical imports and patch resilience:

- **Effects**: `buff.*`, `debuff.*`, `hot.*`, `shield.*`, and possibly `proc.*` or similar categories, with a stable mapping to ESO ability IDs, buff IDs, or UESP effect identifiers where available.  
- **Skills**: `skill.<machine_name>` (often derived from class/line + name), with `external_ids.ability_id` and/or `external_ids.uesp` storing the ESO numeric ID for round-tripping. [file:381][web:432]  
- **Sets**: `set.<machine_name>`, with `external_ids.set_id` and/or `external_ids.eso_sets_api` linking to ESO and UESP set identifiers. [file:392][web:423]  
- **CP stars**: `cp.<machine_name>`, with a stable mapping to ESO/UESP CP IDs where available. [file:393][web:432]

Requirements:

- A given **effect** has **exactly one** ID string in `/data/effects.json`.  
- All references (`effect_id` in skills, sets, CP stars, and aggregate_effects output) must use that ID verbatim—**no alternative bare vs namespaced forms**.  
- When we ingest UESP/ESO data, any numeric IDs or internal strings are stored under `external_ids.*`, **not** as the primary `id`.

### 3.2 Field naming and types

The Build Engine’s fields are stable projections of ESO/UESP columns, not re-inventions.

**For effects**

- `stat`: normalized dimension of impact, derived from ESO data, such as:
  - `resistance_flat` (e.g., Major/Minor Resolve/Breach).  
  - `movement_speed_scalar`, `movement_speed_out_of_combat_scalar`, `mounted_speed_scalar`.  
  - `damage_taken_scalar`.  
  - `hot` (heal-over-time scalar).  
  - `shield` (shield scalar).  

- `magnitude_kind`: how ESO applies the effect numerically, e.g.:
  - `flat`.  
  - `multiplier_additive`.  
  - `multiplier_multiplicative`.  

- `magnitude_value`: numeric magnitude; sign and scale follow ESO’s conventions:
  - Negative for reductions (e.g., Breach to resistance, increased damage taken).  
  - Positive for bonuses (e.g., Resolve, movement speed, HoTs).  

- `category`, `scope`, `stacking_rule`, `stacks_with`:
  - Provide enough structure to model ESO’s stacking behavior (Major/Minor exclusivity, unique sources, etc.).

**For skills, sets, and CP**

- Carry raw ESO values faithfully:
  - `ability_id` / `external_ids.*`.  
  - Base cost, duration, radius, etc.  
  - `tooltip_raw` or equivalent for the full tooltip text.  

- Map these into normalized v1 Data Model fields (`duration_seconds`, `resource`, `tooltip_effect_text`, etc.) without losing the ability to reconstruct the original ESO/UESP semantics. [file:375][file:381][file:392][file:393]

---

## 4. Process steps for external data alignment

This section describes how to go from ESO/UESP source data to aligned `/data/*.json` and tools, in a patch-aware, offline way.

### Step 0 – Freeze current internal data model

- Lock `ESO-Build-Engine-Data-Model-v1.md` as the reference for JSON shapes. [file:375]  
- Treat this scope doc (`ESO-Build-Engine-External-Data-Scope.md`) as **authoritative** for IDs and external alignment until it is explicitly updated. [file:437]

### Step 1 – Source analysis and mapping spec

1. **Catalog UESP data for a chosen ESO API version**

   - Pick one ESO API version (e.g., `v101047`) as the target. [web:432]  
   - For each domain (skills, sets, effects, CP):

     - List the specific UESP tables/files we will read (e.g., skills table, SetItem, buff/effect tables). [web:422][web:423][web:430]  
     - Identify key columns: IDs, names, raw tooltips, base magnitudes, duration fields, flags.

2. **Design mapping tables (documented, not ad-hoc)**

   - ESO/UESP → engine effect `stat` and `magnitude_kind`.  
   - ESO/UESP IDs → engine IDs (`buff.major_resolve`, `set.mark_of_the_pariah`, `cp.ironclad`, etc.).  
   - ESO/UESP tooltip/text fields → engine `tooltip_effect_text` / `description`.  

   Note any **lossy transformations** and ensure they are acceptable for build math (e.g., approximating Pariah’s scaling as a single “max” value for pillars).

3. **Deliverable**

   - A “Data Mapping Appendix” inside this scope doc or a separate `ESO-Build-Engine-Data-Mapping.md` that lists field-by-field mappings per domain.

During this step, **no JSON in `/data` is modified**; we only define the mapping.

### Step 2 – Normalize `/data/effects.json` to canonical schema

Once the mapping for effects is defined:

- Use the mapping from Step 1 to ensure:

  - Every row in `data/effects.json` corresponds to a distinct ESO effect/buff/debuff concept in the UESP data. [web:432][web:429]  
  - IDs, stats, and magnitudes match the ESO/UESP interpretation, including sign conventions and stacking behavior.

- Add `external_ids` fields as needed (e.g., `external_ids.uesp_effect_id`, `external_ids.ability_id`) to enable round-tripping and future patch diffs; do **not** change the primary `id` structure unless the mapping spec requires it.

This normalization should be done via full-file replacements and is **not** repeated per run; future updates are driven by the import pipeline in Step 5.

### Step 3 – Align `skills.json`, `sets.json`, `cp-stars.json` to effects

For each data file (`data/skills.json`, `data/sets.json`, `data/cp-stars.json`):

- Ensure the entity IDs (`skill.*`, `set.*`, `cp.*`) are stable and, where possible, map to ESO/UESP identifiers via `external_ids.*`. [file:381][file:392][file:393][web:432]  

- For all effect references (`effect_id` fields and set/CP effects lists):

  - Replace any non-canonical or “short” IDs with the exact `effects[].id` strings from `data/effects.json`.  
  - Remove any reliance on tool-side mapping (no prefix/suffix guessing or secondary ID schemes).

Each file is updated via a full-file replacement, followed by:

- `tools/validate_build.py` run against the build(s). [file:387]  
- `tools/aggregate_effects.py` and `tools/compute_pillars.py` runs to verify references resolve cleanly. [file:376][file:377]

### Step 4 – Simplify Python tools to the canonical model

Once all `/data` files are aligned:

- `tools/validate_build.py`
  - Confirm every `effect_id` in skills/sets/CP refers to a valid `effects[].id`, using a direct dictionary lookup with no fallback variants. [file:387]

- `tools/aggregate_effects.py`
  - Treat `effect_id` as a straight foreign key into `effects.id`.  
  - Do not attempt to add prefixes, strip suffixes, or otherwise “fix” IDs on the fly. [file:376]

- `tools/compute_pillars.py`
  - Use only the canonical `stat`, `magnitude_kind`, and `magnitude_value` from `effects.json` for math. [file:377][file:374]  
  - Recognize HoTs and shields by **stat** (`"hot"`, `"shield"`) and/or by ID prefixes (`"hot."`, `"shield."`) that directly match `effects[].id`.  
  - Remove any mapping or guessing logic around `effect.*` vs bare IDs.

- `tools/export_build_md.py`
  - When showing effect names and magnitudes, always pull from `effects.json` using the canonical ID, not hardcoded text. [file:389]

Each tool change is a full-file replacement with the standard validation run (validate → aggregate → pillars → export).

### Step 5 – Plan and implement automated mass dump import (offline)

Design and implement a Python-based import pipeline in `tools/` that can:

1. **Per ESO patch:**

   - Detect that a new ESO API version is live (e.g., `v101047`). [web:432]  
   - Apply a **buffer window** (e.g., several days) to allow UESP’s data to be fully updated and stabilized from logs and client extraction. [web:430][web:426]  

2. **Snapshot UESP data:**

   - Download the relevant UESP exports for that API version (skills, sets, effects, CP). [web:422][web:432][web:430]  
   - Store them locally (e.g., under a `raw-data/eso-api-101047/` folder) as part of the repo or an external artifact.

3. **Run importers:**

   - `tools/import_effects_from_uesp.py` → regenerate `data/effects.json`.  
   - `tools/import_skills_from_uesp.py` → regenerate `data/skills.json`.  
   - `tools/import_sets_from_uesp.py` → regenerate `data/sets.json`.  
   - `tools/import_cp_from_uesp.py` → regenerate `data/cp-stars.json`.

   Each importer uses the mapping spec from Step 1 to translate UESP columns into our canonical JSON fields.

4. **Validate and diff:**

   - Run the standard validation chain (`validate_build`, `aggregate_effects`, `compute_pillars`, `export_build_md`).  
   - Optionally, generate a diff report summarizing changes since the previous ESO API version (e.g., new/removed effects, changed magnitudes).

This pipeline is run manually or via CI/CD only when we decide to **update our local database to a new ESO patch**. There are **no live, runtime calls** to UESP or ESO APIs; all data is static once imported.

### Step 6 – Data safety and backup policy

To protect existing canonical data and known-good snapshots during importer development and patch updates:

- `/data/*.json` is treated as **read-only** by all import tools during development and testing. Import scripts must not overwrite `data/skills.json`, `data/effects.json`, `data/sets.json`, or `data/cp-stars.json` directly in experimental runs. [file:500]  
- `data-backups/` is reserved for **manual, human-triggered snapshots** of known-good canonical JSON (for example, `effects.backup-2026-02-11.json`). Import tools must not write to `data-backups/` automatically.  
- All automated or experimental import outputs must be written to a separate tree such as `raw-imports/` (for example, `raw-imports/skills.import-preview.json`, `raw-imports/effects.import-preview.json`, `raw-imports/sets.import-preview.json`, `raw-imports/cp-stars.import-preview.json`).  
- Promotion from `raw-imports/*.json` into `data/*.json` is a **deliberate, manual step** carried out via full-file replacement under Git, after:
  - Validation with `tools/validate_data_integrity.py` and build validators, and  
  - Manual diff review against the previous canonical snapshot. [file:499][file:502]

This policy guarantees that current v1 data (including Permafrost Marshal and any future builds) remains intact while external-alignment import pipelines are designed, tested, and iterated.

---

## 5. Acceptance criteria

The external-data alignment is considered complete for v1 when:

**For each domain (effects, skills, sets, CP):**

- There is exactly **one canonical ID scheme**, documented and enforced.  
- Every reference in `/data` and `builds/` matches those IDs exactly (no implicit translations).

**For Python tools:**

- They perform **no ID translation or guessing** at runtime.  
- Any mapping logic between ESO/UESP and engine fields is:
  - Implemented only in the import tools.  
  - Explicitly documented in the Data Mapping Appendix or `ESO-Build-Engine-Data-Mapping.md`.

**For patch updates:**

- The repo can be updated to a new ESO API version by:

  - Running the documented import tools against a UESP snapshot for that API version.  
  - Manually reviewing diffs for sanity and correctness.  
  - Updating version tags in docs (e.g., “Data aligned to ESO API v101047”) without refactoring IDs or core JSON schemas.

At that point, the Build Engine’s `/data/*.json` is a **frozen, accurate snapshot** of ESO’s data per patch, with full tooltips and math-driven stats, and no reliance on live external calls.

---

## Appendix A – Effects Data Mapping (UESP → `data/effects.json`)

This appendix defines the high-level mapping between UESP’s ESO data exports and the Build Engine’s `data/effects.json` schema. It is intentionally abstracted from any one specific table so it can be applied to future UESP formats as long as they expose equivalent fields. [web:422][web:432][web:430]

### A.1 UESP source fields (conceptual)

From UESP’s ESO data for a given API version (`esodata.uesp.net` / `esoapi.uesp.net`), we expect to read:

- **Effect identity and naming**
  - A stable internal identifier for the effect or buff/debuff (e.g., effect row key, buff ID, or abilityId + effect index).
  - Human-readable name (e.g., "Major Resolve", "Minor Breach"). [web:429][web:432]
  - An optional category flag (buff/debuff/other) if available.

- **Tooltip and description**
  - Raw tooltip text or description fields that explain what the effect does.
  - Optional “short description” fields if present. [web:432]

- **Numeric behavior**
  - Magnitude values: numeric amount (e.g., +5948 resist, -2974 resist, +10% speed).
  - Sign conventions (buff vs debuff).
  - Type/category fields that distinguish:
    - Flat modifiers vs percent modifiers.
    - Damage taken vs resistance vs movement vs HoT/shield behavior.
  - Optional flags or columns that distinguish Major vs Minor tiers and unique vs stackable effects. [web:429][web:432]

- **Linkage to skills/sets/CP**
  - References to which abilityIds, setIds, or CP stars apply this effect, when available.
  - These are used only for `external_ids.*` or cross-checks, not as primary keys.

The exact source table names and column names (e.g., `buffs`, `abilities`, `setBonuses`) will be enumerated in the future `ESO-Build-Engine-Data-Mapping.md` document, but must provide the concepts above. [web:422][web:430]

### A.2 Target schema (`data/effects.json`)

Each effect row in `data/effects.json` will use:

- `id` (string): Engine-level effect ID, e.g.:
  - `buff.major_resolve`
  - `debuff.minor_breach`
  - `hot.resolving_vigor`
  - `shield.barrier`
- `name` (string): Human-readable name (usually ESO’s name or a clear derivative).
- `category` (string): Logical category such as `modifier` (buff/debuff), or future categories as needed.
- `scope` (string): Target scope, e.g. `self`, `target`, `group`, `self_area`.
- `stat` (string): Normalized impact dimension, such as:
  - `resistance_flat`
  - `movement_speed_scalar`
  - `movement_speed_out_of_combat_scalar`
  - `mounted_speed_scalar`
  - `damage_taken_scalar`
  - `hot`
  - `shield`
- `magnitude_kind` (string): How the magnitude is applied:
  - `flat`
  - `multiplier_additive`
  - `multiplier_multiplicative`
- `magnitude_value` (number): Numeric magnitude in engine convention:
  - Positive for buffs (e.g., +5948 resist, +0.10 speed).
  - Negative for debuffs and increased damage taken (e.g., -2974 resist, +0.10 damage taken represented as 0.10 with appropriate `stat`).
- `stacking_rule` (string): Logical stacking behavior:
  - Examples: `exclusive_tier`, `unique_source`, `stacking`, etc.
- `stacks_with` (array of strings): List of other `effects.id` values this effect explicitly stacks with (if any).
- `description` (string): Human-facing description derived from UESP tooltips, expressing what the effect does in plain language.
- `external_ids` (object, optional): Pointers back to UESP/ESO identifiers, e.g.:
  - `external_ids.uesp_effect_id`
  - `external_ids.ability_id`
  - `external_ids.buff_id`

### A.3 Mapping rules

When constructing `data/effects.json` from UESP:

1. **ID generation**
   - Group UESP effect/buff records into conceptual effects (e.g., “Major Resolve” buff as it appears across abilities).
   - Assign a stable engine `id`:
     - Buffs: `buff.<normalized_name>` (e.g., `buff.major_resolve`).
     - Debuffs: `debuff.<normalized_name>` (e.g., `debuff.minor_breach`).
     - HoTs: `hot.<normalized_name>` (e.g., `hot.resolving_vigor`).
     - Shields: `shield.<normalized_name>` (e.g., `shield.barrier`).
   - Normalization rules (lowercase, snake_case where needed) must match the v1 Data Model and Global Rules.

2. **Stat and magnitude mapping**
   - Determine `stat` based on UESP effect type/category and the dimension impacted:
     - Resist-type buffs/debuffs → `resistance_flat`.
     - Movement speed modifiers → `movement_speed_scalar` or `movement_speed_out_of_combat_scalar`.
     - Mounted movement modifiers → `mounted_speed_scalar`.
     - Damage taken modifiers → `damage_taken_scalar`.
     - Periodic healing effects → `hot`.
     - Shield effects → `shield`.
   - Determine `magnitude_kind`:
     - Flat changes (e.g., ±5948 resist) → `flat`.
     - Percentage-like additive modifiers → `multiplier_additive`.
     - Multiplicative stacking modifiers (if ESO distinguishes them) → `multiplier_multiplicative`.
   - Set `magnitude_value` from UESP’s numeric fields, preserving ESO’s sign convention:
     - Debuffs that reduce resist or increase damage taken become negative or positive in a way consistent with the chosen `stat`.

3. **Stacking behavior**
   - Use UESP’s Major/Minor tier flags and uniqueness information to choose `stacking_rule`:
     - Effects in the same Major/Minor “tier” share `exclusive_tier`.
     - Effects that can only exist once from a unique source use `unique_source`.
     - Other stacking behaviors can be modeled as needed.
   - Populate `stacks_with` only where ESO explicitly allows stacking of multiple effects of the same type (e.g., specific combos like Adept Rider + Wild Hunt).

4. **Scope and category**
   - Map UESP’s targeting and category info to:
     - `scope`: `self`, `target`, `group`, `self_area`, etc.
     - `category`: `modifier` or other logical grouping.
   - Where UESP does not provide explicit scope, infer from ability context and document the rule in `ESO-Build-Engine-Data-Mapping.md`.

5. **Descriptions and external IDs**
   - Derive `description` from UESP tooltip or summary fields, simplified as necessary while preserving the math-relevant information.
   - Fill `external_ids` from UESP fields:
     - Link to the underlying ability or buff record (e.g., `abilityId`, internal effect key).
     - These fields are used for traceability and future patch diffs, not for in-engine lookup.

### A.4 Import tool expectations

The future `tools/import_effects_from_uesp.py` script must:

- Read one or more UESP exports for a specific ESO API version that contain effect/buff data. [web:422][web:432][web:430]
- Apply the mapping rules above to produce a complete `data/effects.json` that:
  - Contains exactly one row per conceptual buff/debuff/effect relevant to builds.
  - Uses canonical `id` strings consistent with the v1 Data Model and Global Rules.
  - Fills `stat`, `magnitude_kind`, and `magnitude_value` in a way that is sufficient for Build Engine math (pillars, simulations, aggregation).
  - Includes `external_ids` for backlinking to UESP/ESO data.

Subsequent tools (validators, aggregators, pillar evaluators, exporters) must treat `data/effects.json` as the **only source** of truth for effect math and names, and must never attempt to re-interpret raw UESP data directly.
