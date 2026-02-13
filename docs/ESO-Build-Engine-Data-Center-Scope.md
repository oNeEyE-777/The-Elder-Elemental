File: docs/ESO-Build-Engine-Data-Center-Scope.md
Last-Updated: 2026-02-13 05:40:00Z

# ESO Build Engine Data Center Scope

## 1. Purpose

This document defines the **scope and responsibilities** of the ESO Build Engine Data Center:

- What data it holds and in what shape.
- How that data flows into and out of the rest of the system.
- How external ESO sources (primarily ESO-Hub) relate to canonical JSON in this repo.

It complements:

- `ESO-Build-Engine-Overview.md`
- `ESO-Build-Engine-Data-Model-v1.md`
- `ESO-Build-Engine-Global-Rules.md`
- `ESO-Build-Engine-External-Data-Scope.md`
- `ESO-Build-Engine-External-Data-Runbook.md`
- `ESO-Build-Engine-ESO-Hub-Integration.md`
- `ESO-Build-Engine-Alignment-Control.md` [file:1024][file:1015][file:1016][file:1022][file:1023][file:1021][file:1018]


## 2. Data Center responsibilities

### 2.1 What the Data Center owns

The Data Center is responsible for **all structured ESO game data and builds** used by the engine. Concretely, it owns:

- Canonical ESO data:
  - `data/skills.json`
  - `data/effects.json`
  - `data/sets.json`
  - `data/cp-stars.json` [file:1015][file:1018]

- Build definitions:
  - `builds/*.json` (e.g. `builds/permafrost-marshal.json`).

- External data artifacts:
  - Snapshot inputs under `raw-imports/` (ESO-Hub and optional secondary sources).
  - Import preview files under `raw-imports/`. [file:1022][file:1023]

Data Center responsibilities include:

- Maintaining canonical schemas and IDs as defined in the v1 Data Model and Alignment Control docs.
- Ensuring data integrity (ID uniqueness, valid references).
- Providing stable inputs to tools, backend, and frontend.


### 2.2 What the Data Center does not own

The Data Center explicitly does **not** own:

- External ESO sources themselves:
  - ESO-Hub site and its internal databases.
  - UESP, ESO client dumps, or addon logs. [file:1022][file:1021]
- Scraping/crawling logic:
  - ESO-Hub crawlers and HTML→JSON scrapers live **outside** this repo.
- Presentation logic:
  - Backend API routing and HTTP concerns.
  - Frontend React/Vite components and styling.

The Data Center’s job is to **hold and validate the truth**, not to acquire it directly from the web or present it to users.


## 3. Inbound data scope

### 3.1 ESO-Hub snapshots (primary)

For v1, the primary inbound data scope is **ESO-Hub–derived snapshots** for:

- Skills:
  - Names, class/skill line grouping, role (active/passive/ultimate).
  - Tooltip header fields and effect text at level‑50 baseline. [file:1021]
- Sets:
  - Names, categories (overland/dungeon/trial/crafted/class/mythic).
  - Source/location metadata.
  - Full 2–5 piece bonus tooltips. [file:1021]
- Champion Points:
  - Names and trees (Warfare/Fitness/Craft).
  - Slottable vs passive.
  - Tooltip text and rank details where available. [file:1021]

These arrive as **offline snapshot files** copied into `raw-imports/`:

- `raw-imports/skills-esohub-snapshot.json`
- `raw-imports/sets-esohub-snapshot.json`
- `raw-imports/cp-esohub-snapshot.json` [file:1021][file:1022]

Snapshots are immutable for the duration of an import run.


### 3.2 Secondary sources (optional)

Secondary sources, if used, are limited to:

- UESP exports.
- ESO client Lua dumps / `EsoExtractData` outputs.
- Addon-generated logs of tooltips and IDs. [file:1022]

Their **scope** is:

- Provide additional metadata not clearly exposed by ESO-Hub (e.g. internal numeric IDs).
- Cross-check ESO-Hub for correctness.

They may be merged into snapshot JSON **before** it is copied into `raw-imports/`, but the Data Center does not depend on them for basic tooltip text or naming. ESO-Hub remains primary for what users see. [file:1022][file:1021]


## 4. Outbound data scope

### 4.1 Tools

The Data Center provides data inputs to Python tools under `tools/`:

- Validation:
  - `tools/validate_data_integrity.py`
  - `tools/validate_build.py` [file:1016][file:1018]

- Effects and pillars:
  - `tools/aggregate_effects.py`
  - `tools/compute_pillars.py` (see `compute_pillars.txt`) [file:1019][file:1018]

- External import:
  - `tools/import_skills_from_esohub.py`
  - `tools/import_sets_from_esohub.py`
  - `tools/import_cp_from_esohub.py` [file:1023][file:1021]

- Export:
  - `tools/export_build_md.py` (Markdown views).
  - Future JSON or API exporters as needed. [file:1016][file:1018]

All of these tools:

- Read canonical data from `data/` and builds from `builds/`.
- May read snapshots and previews from `raw-imports/`.
- Must not call external services at runtime. [file:1022][file:1023]


### 4.2 Backend

The backend (`backend/`) consumes canonical JSON from the Data Center to:

- Serve build and data endpoints to the UI.
- Expose precomputed fields (e.g. aggregated effects, pillar scores) as needed.

Scope boundaries:

- Backend does not hold independent game data; it reads only from `data/` and `builds/`.
- Backend never calls ESO-Hub, UESP, or other external game data sources. [file:1010][file:1018][file:1022]


### 4.3 Frontend

The frontend (`frontend/`) uses the backend’s outputs to:

- Render build views (bars, gear, CP).
- Provide selector-only inputs for choosing skills/sets/CP based on canonical IDs.
- Show **hover tooltips** for skills, sets, and CP stars by using the text fields from `data/*.json`:

  - Skills: `tooltipeffecttext`
  - Sets: `bonuses[].tooltipraw`
  - CP: CP tooltip field [file:1024][file:1015][file:1021]

The frontend does not query ESO-Hub or any external source directly.


## 5. Lifecycle and change flow

### 5.1 Ingest and evolve canonical data

The Data Center’s lifecycle for external data is:

1. **Snapshot acquisition** (outside repo):
   - ESO-Hub snapshots generated and frozen locally. [file:1021][file:1022]

2. **Snapshot import**:
   - Snapshots copied into `raw-imports/`.
   - Import tools generate `*.import-preview.json` in canonical v1 shapes. [file:1023]

3. **Preview validation**:
   - Validators check preview files against schemas and ID rules. [file:1023][file:1018]

4. **Promotion to canonical**:
   - Promotion tool (current or future) replaces relevant `data/*.json` files from previews.
   - `tools/validate_data_integrity.py` is run to ensure consistency. [file:1018][file:1023]

5. **Commit and propagate**:
   - All changes (snapshots, previews, data) are committed together.
   - Backend/frontend tooling can then rely on updated canonical JSON.

External updates (e.g. a new ESO patch) follow this cycle; no step may be skipped. [file:1023]


### 5.2 Versioning and stability

The Data Center’s JSON files represent the **current** patch baseline of ESO as reflected by ESO-Hub and validated by tools:

- The `source_tag` fields and dates in snapshots/metadata can be used to track which patch a given dataset corresponds to.
- Changes between versions should be observable via Git diffs.
- Tools and UI are expected to be robust to additions (new skills/sets/CP) but not to breaking schema changes, which must be coordinated via the control docs. [file:1015][file:1018][file:1021]


## 6. Scope limits and non-goals

The following are **out of scope** for the v1 Data Center:

- Hosting or mirroring entire external databases (ESO-Hub, UESP).
- Real-time or per-user data (e.g. account-specific progression, inventory).
- Live performance logs or combat logs.

The Data Center is intentionally focused on:

- Static, patch-aligned ESO game data.
- Build definitions and their derived analytics.

Future phases may introduce additional layers (e.g. a relational DB or additional indexes) but must continue to treat `data/` and `builds/` as the canonical definitions of game data and builds, unless the control docs are explicitly updated. [file:1011][file:1019][file:1018]


## 7. Change management

Any change to:

- What data the Data Center holds.
- How external data is ingested and mapped.
- How tools interact with `data/`, `builds/`, or `raw-imports/`.

must be reflected in:

- This document (Data Center Scope).
- `ESO-Build-Engine-External-Data-Scope.md`
- `ESO-Build-Engine-External-Data-Runbook.md`
- `ESO-Build-Engine-ESO-Hub-Integration.md`
- `ESO-Build-Engine-Data-Model-v1.md`
- `ESO-Build-Engine-Alignment-Control.md` [file:1022][file:1023][file:1021][file:1015][file:1018]

No code or JSON changes are allowed to introduce new behaviors or assumptions outside this documented scope without coordinated updates to the relevant control documents.
