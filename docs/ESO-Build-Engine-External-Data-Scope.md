File: docs/ESO-Build-Engine-External-Data-Scope.md
Last-Updated: 2026-02-13 05:24:00Z

# ESO Build Engine External Data Scope

## 1. Purpose

This document defines how the ESO Build Engine v1 Data Center aligns to **external ESO data sources**, with a focus on:

- Which upstream sources are considered authoritative.
- How their concepts and IDs map into v1 JSON schemas.
- What part of the external ingestion pipeline lives **inside** this repository vs. **outside** it.

It complements:

- `ESO-Build-Engine-Overview.md`
- `ESO-Build-Engine-Data-Model-v1.md`
- `ESO-Build-Engine-Global-Rules.md`
- `ESO-Build-Engine-Data-Center-Scope.md`
- `ESO-Build-Engine-Data-Center-Tool-Checklist.md`
- `ESO-Build-Engine-External-Data-Runbook.md`
- `ESO-Build-Engine-Alignment-Control.md`
- `ESO-Build-Engine-ESO-Hub-Integration.md` [file:1014][file:1015][file:1016][file:1010][file:1020][file:1018][file:1021]

This document does **not** redefine internal JSON schemas or tool behaviors; those remain controlled by the v1 Data Model and Alignment Control docs. Instead, this file explains how ESO-Hub and other external sources are used to populate those schemas.


## 2. External sources – roles and priorities

### 2.1 ESO-Hub as primary upstream

For v1, **ESO-Hub** is the primary external data source for:

- Skills:
  - Names.
  - Class and skill line groupings.
  - Tooltip header fields (cost, target, duration, range, radius).
  - Tooltip body text, including baseline numeric values and morph “new effect” descriptions. [file:1021][web:775]
- Sets:
  - Set names and categories (overland, dungeon, trial, crafted, class, mythic, etc.).
  - Drop source/location metadata.
  - Full 2–5 piece bonus tooltips at an empty level 50 baseline. [file:1021][web:921]
- Champion Points:
  - Star names and trees (Warfare, Fitness, Craft).
  - Slottable vs passive status.
  - Tooltip text and per-rank descriptions where available. [file:1021][web:972]

ESO-Hub’s visible pages and internal tooltip engine are assumed to reflect the in-game tooltips for the current patch at that baseline. When we speak about “external truth” for skills, sets, and CP, we mean “ESO-Hub’s version of those tooltips and names” unless explicitly noted otherwise. [file:1021]


### 2.2 Secondary sources (UESP, raw data, addons)

Other sources remain **valuable but secondary**:

- UESP:
  - Provides detailed ESO data dumps (Lua, CSV, JSON) with raw IDs and structured fields.
  - Useful for:
    - Cross-checking ESO-Hub values.
    - Filling in non-tooltip fields (e.g. internal ability IDs, flags) when ESO-Hub doesn’t expose them clearly.
  - No longer the required or primary upstream for tooltips or naming.

- Raw ESO client exports and addons:
  - ESO client Lua or `EsoExtractData` exports.
  - Logging addons that capture tooltips and IDs.
  - Useful for:
    - Deep verification of edge cases.
    - Researching discrepancies between ESO-Hub and the game.
  - Not required for the v1 Data Center import path.

When secondary sources disagree with ESO-Hub:

- ESO-Hub is preferred for **what the user sees** (tooltip text and in-game naming).
- Secondary data may be used to:
  - Confirm ESO-Hub is correct.
  - Justify explicit corrections, which must be documented and reproducible.


## 3. Ingestion boundary and responsibilities

### 3.1 Local environment vs. repository

The ingestion path is intentionally split:

- **Local environment (outside this repo)**:
  - Owns:
    - Crawlers/spiders that walk ESO-Hub and collect detail URLs. [file:1021]
    - Scrapers that fetch ESO-Hub HTML and turn it into compact JSON snapshots for:
      - Skills.
      - Sets.
      - CP stars.
    - Any optional scripts that merge in secondary sources (UESP, raw ESO data) *into* those snapshots before they reach this repo.
  - Outputs:
    - Frozen snapshot files:
      - `skills-esohub-snapshot.json`
      - `sets-esohub-snapshot.json`
      - `cp-esohub-snapshot.json` (and variants as needed). [file:1021]

- **Repository (`raw-imports/`, `data/`, `tools/`)**:
  - Sees only snapshot JSON files copied into `raw-imports/`.
  - Runs import preview tools to map snapshot rows into v1 canonical schemas.
  - Validates and promotes into `data/*.json` via the Runbook and Alignment Control processes. [file:1020][file:1018]
  - Never performs live HTTP or external API calls. [file:1020]

This separation keeps the repo deterministic and replayable, while allowing the local environment to evolve scraping strategies without changing core tools.


### 3.2 No live external access in tools/backend/frontend

The following are **prohibited** inside this repository:

- Live HTTP requests to ESO-Hub, UESP, or any other external site in:
  - `tools/*.py`
  - `backend/` Node/Express API.
  - `frontend/` React/Vite UI.
- Any hidden external database used as a source of ESO data.

All external ESO data must exist as tracked files in this repo, under `raw-imports/` for snapshots and `data/` for canonical JSON. [file:1020][file:1018]


## 4. Snapshot expectations and scope

This section summarizes what the repo expects from snapshot files, matching details in `ESO-Build-Engine-ESO-Hub-Integration.md`. [file:1021]

### 4.1 Snapshot location and naming

Primary ESO-Hub snapshots are expected under `raw-imports/`:

- Skills:
  - `raw-imports/skills-esohub-snapshot.json`
- Sets:
  - `raw-imports/sets-esohub-snapshot.json`
- CP stars:
  - `raw-imports/cp-esohub-snapshot.json` [file:1021]

Alternative or experimental snapshots (e.g. UESP-aligned) must follow clear naming, such as:

- `raw-imports/skills-uesp-snapshot.json`
- `raw-imports/sets-uesp-snapshot.json`
- `raw-imports/cp-uesp-snapshot.json`

The repo tools must never treat any snapshot as canonical; snapshots are **inputs** only. [file:1020]


### 4.2 Snapshot content requirements (high-level)

Regardless of source (ESO-Hub primary, UESP secondary), snapshots must:

- Be valid UTF‑8 JSON.
- Represent each skill, set, or CP star as an object with:
  - A stable external identifier (`external_id`).
  - The external URL where applicable (`url`).
  - Human-readable name (`name`).
  - Grouping/key metadata (class and skill line for skills, category/source for sets, tree for CP).
  - Tooltip text fields that will populate `tooltipeffecttext` (skills), `bonuses[].tooltipraw` (sets), and CP tooltip fields in canonical JSON. [file:1021][file:1015][file:1018]
- Include a `source_tag` or equivalent provenance marker (e.g. `esohub-20260213`, `uesp-20260213`) so runs can be traced and compared. [file:1021][file:1020]

The precise field-level snapshot schemas for ESO-Hub are defined in `ESO-Build-Engine-ESO-Hub-Integration.md`. [file:1021]


## 5. Mapping external concepts to v1 JSON

This section clarifies how external concepts (primarily from ESO-Hub) are expected to align with v1 Data Center schemas. The detailed field mappings are specified in `ESO-Build-Engine-Data-Model-v1.md` and **must not** be contradicted here. [file:1015]

### 5.1 Skills

External concepts from ESO-Hub: [file:1021][web:775]

- Skill identity:
  - ESO-Hub skill URL and `external_id`.
  - Name, class, skill line, morph-of relationship, active/passive/ultimate.
- Tooltip header:
  - Cost, target, duration, range, radius, etc.
- Tooltip body:
  - Effect text and morph “new effect” text at level‑50 baseline.

Expected mapping into `data/skills.json` (high level):

- Canonical IDs:
  - `id`: `skill.<normalized-name-or-key>`
- Text:
  - Main tooltip text into `tooltipeffecttext`.
- Metadata:
  - ESO-Hub `external_id` into `externalids.esohub`.
  - Class/skill line mapped to internal `classid`/`skilllineid`.
- Effects:
  - Initially, `effects` arrays may be empty or simplistic until curated mappings are established, as allowed by the External Data Runbook. [file:1020][file:1018]


### 5.2 Sets

External concepts from ESO-Hub: [file:1021][web:921]

- Set identity:
  - ESO-Hub set URL and `external_id`.
  - Set name and category (overland, dungeon, trial, crafted, class, mythic, etc.).
- Bonus tiers:
  - `pieces_required`.
  - Full tooltip text for each tier at level‑50 baseline.

Expected mapping into `data/sets.json`:

- Canonical IDs:
  - `id`: `set.<normalized-name-or-key>`
- Text:
  - Each bonus tier’s tooltip into `bonuses[].tooltipraw`.
- Metadata:
  - ESO-Hub `external_id` into `externalids.esohub`.
  - Category/source into fields like `type` and `sourcetag` (per v1 Data Model). [file:1015][file:1018]
- Effects:
  - `bonuses[].effects` may start as empty or minimal until full effect mappings are available.


### 5.3 Champion Points

External concepts from ESO-Hub: [file:1021][web:972]

- CP star identity:
  - ESO-Hub CP URL and `external_id`.
  - Star name and tree (Warfare, Fitness, Craft).
- Slottable vs passive.
- Tooltip text and per-rank descriptions.

Expected mapping into `data/cp-stars.json`:

- Canonical IDs:
  - `id`: `cp.<normalized-name-or-key>`
- Text:
  - ESO-Hub tooltip into the canonical CP tooltip field (per v1 Data Model).
- Metadata:
  - `tree` and `slot_type` mapped directly.
  - ESO-Hub `external_id` into `externalids.esohub`.
- Effects:
  - `effects` arrays may be initially minimal, consistent with the External Data Runbook. [file:1020][file:1018]


## 6. Import tools and source-specific pipelines

The actual import logic is defined in `tools/*.py` and governed by `ESO-Build-Engine-External-Data-Runbook.md` and `ESO-Build-Engine-Alignment-Control.md`. [file:1020][file:1018] This section only clarifies **source-specific** expectations.

### 6.1 ESO-Hub importers (primary path)

The primary import path uses the ESO-Hub snapshots and the following tools:

- `tools/import_skills_from_esohub.py`
- `tools/import_sets_from_esohub.py`
- `tools/import_cp_from_esohub.py` [file:1021][file:1020]

These tools must:

- Accept a `--snapshot-path` pointing to ESO-Hub snapshots under `raw-imports/`.
- Produce:
  - `raw-imports/skills.import-preview.json`
  - `raw-imports/sets.import-preview.json`
  - `raw-imports/cp-stars.import-preview.json`
  in v1 canonical shapes.
- Never write directly to `data/*.json`; promotion is a separate step, as defined in the Runbook. [file:1020][file:1018]


### 6.2 UESP or other importers (secondary, optional)

Existing UESP import stubs (if present):

- `tools/import_skills_from_uesp.py`
- `tools/import_sets_from_uesp.py`
- `tools/import_cp_from_uesp.py` [file:932][file:933][file:934]

are considered **optional secondary** pipelines. If they are used:

- They must target the same `*.import-preview.json` outputs and schemas as ESO-Hub importers.
- They must not bypass validation or promotion steps.
- Their snapshot schemas (e.g. `skills-uesp-snapshot.json`) must be documented separately and kept consistent with v1 Data Model expectations.


## 7. Frontend scope: hover tooltips and visual fidelity

Although detailed frontend behavior belongs in UI docs, this scope document captures one key integration requirement:

- The **visual tooltips** shown in the Build Engine frontend (on hover over skill, set, or CP entries) must be derived from:
  - `tooltipeffecttext` for skills.
  - `bonuses[].tooltipraw` for sets.
  - The canonical CP tooltip field for CP stars. [file:1015][file:1018][file:1021]
- Those fields are populated from ESO-Hub snapshots and should match ESO-Hub’s baseline tooltips for each patch, barring explicitly documented corrections.

This ensures that the Data Center’s external alignment directly supports the human-facing UI behavior you rely on for theorycrafting.


## 8. Out-of-scope items and removed constraints

The following are **explicitly out of scope** for v1 external alignment, or have been downgraded from earlier assumptions:

- Mandatory ingestion of full raw ESO client dumps (Lua, CSV, etc.) into the repo.
- Requirement that UESP or any other single site is the exclusive “source of truth.”
- Live querying of any external service at runtime for tooltips or metadata.

Instead:

- ESO-Hub is the authoritative external baseline for tooltips and in-game naming.
- Secondary sources are optional validation/augmentation.
- All external data reaching the repo must flow through offline snapshots and import tools. [file:1020][file:1021]


## 9. Change management

Any change to:

- Which external sources are considered primary or secondary.
- Snapshot shapes or required fields.
- The mapping of external fields into canonical v1 JSON.

must be reflected in:

- This document (External Data Scope).
- `ESO-Build-Engine-ESO-Hub-Integration.md` (for ESO-Hub specifics).
- `ESO-Build-Engine-External-Data-Runbook.md` (for process).
- `ESO-Build-Engine-Data-Model-v1.md` and `ESO-Build-Engine-Alignment-Control.md` (for schemas and tool behaviors). [file:1015][file:1018][file:1020][file:1021]

No tool or JSON format is allowed to introduce new external assumptions or shortcuts that contradict these documents without an explicit, documented update and corresponding validation.
