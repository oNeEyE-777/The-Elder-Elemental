File: docs/ESO-Build-Engine-Overview.md
Last-Updated: 2026-02-13 05:37:00Z

# ESO Build Engine Overview

## 1. High-level goal

The ESO Build Engine is a **data-driven build analysis and presentation system** for The Elder Scrolls Online (ESO). It is designed to:

- Represent ESO builds (skills, gear, Champion Points) as structured JSON.
- Aggregate and analyze effects from those builds (resists, health, speed, HoTs, shields, core combo).
- Render human-readable views (Markdown, UI) with accurate tooltips and stats for theorycrafting.

The engine’s first anchor build is *Permafrost Marshal*, but the architecture must scale to any ESO build without changing core logic. [file:1014]


## 2. Architecture overview

### 2.1 Repo structure and responsibility split

The repository is organized into clear layers:

- `data/`:
  - Canonical ESO game data:
    - `skills.json`
    - `effects.json`
    - `sets.json`
    - `cp-stars.json`
  - These files are the **single source of truth** for game mechanics inside the engine. [file:1015][file:1018]

- `builds/`:
  - Build records (e.g. `permafrost-marshal.json`) that reference IDs from `data/` and specify configuration (bars, gear, CP, pillars).
  - No raw tooltip text or free-form effects live here; builds only reference canonical IDs. [file:1015][file:1018]

- `tools/`:
  - Python tools for:
    - Data validation.
    - External data import and preview.
    - Effect aggregation.
    - Pillar computation.
    - Markdown export.
  - All game logic lives here, not in ad-hoc scripts or the frontend/backend. [file:1016][file:1018]

- `backend/`:
  - Node/Express/TypeScript API that:
    - Reads JSON from `data/` and `builds/`.
    - Exposes build and data endpoints to the UI.
  - Does not talk to external data sources; it only reads local canonical JSON. [file:1010][file:1018]

- `frontend/`:
  - React/Vite UI that:
    - Presents build grids, selectors, and hover tooltips.
    - Uses selector-only inputs (no free-text editing of core entities).
  - Treats `data/` and `builds/` as immutable inputs via the API. [file:1010][file:1014]

- `docs/`:
  - Control documents (this file, Data Model, Global Rules, External Data Scope, ESO-Hub Integration, etc.) that define non-negotiable rules and schemas. [file:1015][file:1016][file:1021][file:1022][file:1023]


### 2.2 Non-negotiable principles

The following rules apply across the entire system:

- **Single source of truth**:
  - Canonical ESO data lives only in `data/*.json`.
  - Builds live only in `builds/*.json`.
  - No hidden databases or external configuration have authority. [file:1018]

- **No live external dependencies**:
  - Tools, backend, and frontend may not perform live HTTP requests or call external APIs for game data.
  - All external data (e.g. ESO-Hub) is ingested via offline snapshots under `raw-imports/`. [file:1022][file:1023]

- **Schema-first**:
  - JSON schemas and field names are defined in `ESO-Build-Engine-Data-Model-v1.md` and `ESO-Build-Engine-Alignment-Control.md`.
  - Tools and data must conform to these docs; if reality changes, the docs are updated first. [file:1015][file:1018]

- **No partial edits**:
  - Any file we “touch” in a given change is written as a **full file** (no patch fragments).
  - Canonical `data/*.json` updates happen via full-file promotion, not ad-hoc editing. [file:1018]

- **Deterministic behavior**:
  - Given the same `data/` and `builds/`, tools must produce identical outputs (effects, pillars, Markdown) every time.
  - No tooling may depend on environment-specific state. [file:1016][file:1018]


## 3. Data model summary

The v1 Data Model is defined in detail in `ESO-Build-Engine-Data-Model-v1.md`. This section summarizes the core entities. [file:1015]

### 3.1 Skills

- Stored in: `data/skills.json`.
- Identity:
  - `id`: `skill.<key>` (e.g. `skill.deepfissure`).
- Core fields:
  - `name`
  - `tooltipeffecttext` (human tooltip text displayed on hover).
  - `classid`, `skilllineid`
  - `type` (active, passive, ultimate)
  - `resource`, `cost`, `casttime`, `target`, `durationseconds`, `radiusmeters`
  - `abilityid` and `externalids` (e.g. `externalids.esohub`) for linking back to ESO-Hub. [file:1015][file:1021]

- Effects:
  - `effects` array referencing `effects.id` (`buff.*`, `debuff.*`, `hot.*`, `shield.*`) with timing/target/duration metadata.
  - This array drives pillar computation and effect aggregation. [file:1015][file:1018]


### 3.2 Effects

- Stored in: `data/effects.json`.
- Identity:
  - `id`: `buff.*`, `debuff.*`, `hot.*`, `shield.*`.
- Core fields:
  - `stat`: canonical stat key used by pillar math (e.g. `resist`, `hot`, `shield`, specific speed stats).
  - `basevalue`: magnitude used for quantitative evaluation.
  - Optional metadata: `name`, `tags`, `notes`. [file:1015][file:1018]

Effects are the bridge between game entities (skills/sets/CP) and pillar metrics.


### 3.3 Sets

- Stored in: `data/sets.json`.
- Identity:
  - `id`: `set.<key>` (e.g. `set.markofthepariah`).
- Core fields:
  - `name`
  - `bonuses`: array of tiers, each with:
    - `pieces`
    - `tooltipraw` (set bonus tooltip text)
    - `effects`: array of effect IDs or richer effect objects. [file:1015][file:1018]

Sets contribute effects based on equipped pieces and are central to tank/speed configurations like Permafrost Marshal. [file:1015][file:1019]


### 3.4 Champion Points

- Stored in: `data/cp-stars.json`.
- Identity:
  - `id`: `cp.<key>` (e.g. `cp.ironclad`).
- Core fields:
  - `name`
  - `tree`: `warfare`, `fitness`, or `craft`
  - Tooltip field for the star’s effect (e.g. `tooltipraw`)
  - `effects`: effect IDs relating to mitigation, speed, etc. [file:1015][file:1018]

CP stars extend effects and pillars, especially for mitigation and movement speed.


### 3.5 Builds

- Stored in: `builds/*.json` (e.g. `builds/permafrost-marshal.json`).
- Identity:
  - `id`: `build.<key>` (e.g. `build.permafrostmarshal`).
- Core fields:
  - `name`
  - `bars`:
    - `front` and `back`, each an array of slots with `slot` and `skillid`.
  - `gear`:
    - 12 canonical slots (head, chest, ring1, etc.) with `setid`, `weight`, `trait`, `enchant`.
  - `cpslotted`:
    - CP stars per tree, referencing `cp.*` IDs.
  - `pillars`:
    - Configuration for resist/health/speed/HoTs/shield/corecombo targets. [file:1015][file:1018]

Builds are pure configurations; they never embed tooltip text or effect math directly.


## 4. External data and ESO-Hub

### 4.1 ESO-Hub as primary external source

For v1, ESO-Hub is the **primary external data source** for:

- Skill names, groupings, and tooltips.
- Set names, categories, sources, and full bonus tooltips.
- Champion Point names, trees, and tooltips. [file:1021][file:1022]

ESO-Hub’s tooltips are taken at an empty level-50 baseline, which aligns with the engine’s needs for normalized data. [file:1021]

Secondary sources (UESP, raw ESO dumps, addons) are optional and used only to:

- Cross-check ESO-Hub.
- Fill non-tooltip fields (e.g. internal IDs) when needed. [file:1022]


### 4.2 Snapshot ingestion model

External data never flows directly into `data/*.json`. Instead, it follows this pattern:

1. **Local environment (outside repo)**:
   - ESO-Hub crawler discovers skill, set, and CP detail URLs.
   - Scraper fetches ESO-Hub HTML and converts it into JSON snapshots:
     - `skills-esohub-snapshot.json`
     - `sets-esohub-snapshot.json`
     - `cp-esohub-snapshot.json` [file:1021][file:1022]

2. **Repo `raw-imports/`**:
   - Snapshots are copied into `raw-imports/` unchanged.
   - Import tools (`tools/import_*_from_esohub.py`) read these snapshots and generate:
     - `raw-imports/skills.import-preview.json`
     - `raw-imports/sets.import-preview.json`
     - `raw-imports/cp-stars.import-preview.json` in v1 canonical shapes. [file:1023]

3. **Validation and promotion**:
   - Preview validators confirm schema and ID correctness.
   - A promotion step (current or future) replaces `data/skills.json`, `data/sets.json`, and `data/cp-stars.json` from the previews, followed by `validate_data_integrity`. [file:1023][file:1018]

No tool in this repo is allowed to call ESO-Hub or any other site directly. [file:1022][file:1023]


### 4.3 Hover tooltips and UI fidelity

A core design goal is that **hover tooltips in the UI** match what you see on ESO-Hub and in-game:

- Backend serves from `data/`:
  - Skills: `tooltipeffecttext`.
  - Sets: `bonuses[].tooltipraw`.
  - CP stars: CP tooltip field. [file:1015][file:1018][file:1021]

- Frontend:
  - Renders skills, sets, and CP stars by canonical IDs.
  - On hover:
    - Looks up the relevant object in memory.
    - Builds a tooltip popup showing:
      - Name.
      - Key header fields (cost, duration, etc.).
      - Tooltip text from `data/*.json`. [file:1021][file:1023]

There is no live tooltip pull from ESO-Hub; fidelity is achieved by ensuring snapshots are up to date and importers map them faithfully into canonical JSON. [file:1021][file:1022]


## 5. Tools and workflows (summary)

Detailed tool behavior is documented in `ESO-Build-Engine-Global-Rules.md`, `ESO-Build-Engine-Alignment-Control.md`, and the External Data Runbook. This section summarizes the main workflows. [file:1016][file:1018][file:1023]

### 5.1 Core validation tools

Key Python tools include:

- `tools/validate_data_integrity.py`:
  - Validates `skills.json`, `effects.json`, `sets.json`, `cp-stars.json` for:
    - Unique IDs.
    - Correct prefixes.
    - Valid effect references. [file:1018]

- `tools/validate_build.py`:
  - Validates `builds/*.json` against:
    - Structure rules.
    - Cross-references to `data/*.json`. [file:1016][file:1018]

- `tools/aggregate_effects.py`:
  - Aggregates active effects from a build’s skills, sets, and CP into a list of effect instances. [file:1016][file:1018]

- `tools/compute_pillars.py` (via `compute_pillars.txt`):
  - Evaluates build pillars (resist, health, speed, HoTs, shields, core combo) based on aggregated effects and pillar config. [file:1019][file:1018]


### 5.2 External data tools

Primary external data tools (ESO-Hub):

- `tools/import_skills_from_esohub.py`
- `tools/import_sets_from_esohub.py`
- `tools/import_cp_from_esohub.py` [file:1021][file:1023]

These tools:

- Read ESO-Hub snapshots under `raw-imports/`.
- Produce import previews in v1 schemas under `raw-imports/`.
- Never write directly to `data/*.json`. [file:1022][file:1023]

Secondary (optional) UESP importers mirror the same pattern and must output the same preview shapes. [file:1022][file:1023]


### 5.3 Markdown export

- `tools/export_build_md.py`:
  - Reads build JSON and canonical data.
  - Outputs a Markdown view of:
    - Bars.
    - Gear.
    - CP layout.
    - (Future) Tooltip hints and pillar summaries. [file:1016][file:1018]

Markdown exports are **views only** and must never be edited by hand. [file:1018]


## 6. Current scope and next steps

### 6.1 v1 scope

For v1, the intended scope is:

- One fully validated, high-fidelity build (Permafrost Marshal) using:
  - Canonical skills, sets, CP, and effects.
  - Correct pillar outputs.
  - Accurate hover tooltips based on ESO-Hub-derived data. [file:1015][file:1019][file:1021]

- Stable import pipeline:
  - ESO-Hub snapshots → import previews → validated promotion → `data/*.json`. [file:1022][file:1023]

- Reliable tools:
  - Build validation, effect aggregation, pillars, Markdown export. [file:1016][file:1018][file:1019]


### 6.2 Future directions

Future phases (beyond this v1) are expected to:

- Expand `data/*.json` to cover more of ESO’s skills, sets, and CP.
- Introduce a more comprehensive build database backed by the Data Center JSON.
- Add richer UI features, such as:
  - Visual comparison of builds.
  - Inline pillar diagnostics.
  - Scenario-based analysis.

All future expansion must respect the same core principles:

- ESO-Hub as primary external reference for human-facing tooltips.
- Offline snapshots and import tools for data ingestion.
- Canonical schemas and IDs enforced by control documents. [file:1021][file:1022][file:1018]
