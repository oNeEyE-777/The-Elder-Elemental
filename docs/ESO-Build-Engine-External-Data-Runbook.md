File: docs/ESO-Build-Engine-External-Data-Runbook.md
Last-Updated: 2026-02-13 05:31:00Z

# ESO Build Engine External Data Runbook

## 1. Purpose

This runbook defines **how external ESO data** (skills, sets, Champion Point stars) is brought into the ESO Build Engine v1 Data Center.

It explains:

- Where external data comes from (ESO-Hub as primary, others as secondary).
- How that data must be prepared into offline snapshots.
- How import preview tools transform snapshots into v1 canonical schemas.
- How validation and promotion safely update `data/*.json`.

It complements and must remain consistent with:

- `ESO-Build-Engine-Overview.md`
- `ESO-Build-Engine-Data-Model-v1.md`
- `ESO-Build-Engine-Global-Rules.md`
- `ESO-Build-Engine-External-Data-Scope.md`
- `ESO-Build-Engine-Alignment-Control.md`
- `ESO-Build-Engine-ESO-Hub-Integration.md` [file:1014][file:1015][file:1016][file:1022][file:1018][file:1021]


## 2. Rules for external data

The following rules are non-negotiable for all external data ingestion:

- **Offline snapshots only**:
  - All external ESO data must be ingested from **frozen snapshot files**.
  - No tool in `tools/`, `backend/`, or `frontend/` may perform live HTTP requests or call external APIs. [file:1022][file:1018]

- **ESO-Hub as primary upstream**:
  - ESO-Hub is the primary external source for:
    - Skill names, groupings, and tooltips.
    - Set names, types, sources, and bonus tooltips.
    - Champion Point star names, trees, and tooltips. [file:1021][file:1022]
  - Other sources (UESP, raw dumps, addons) are secondary and optional.

- **Repository as source of truth**:
  - Canonical ESO data lives only under `data/`:
    - `data/skills.json`
    - `data/effects.json`
    - `data/sets.json`
    - `data/cp-stars.json` [file:1018]
  - All imported data must exist as tracked files in this repo.

- **Import tools write only to `raw-imports/`**:
  - Import tools may write:
    - Snapshot-normalized previews.
    - Import preview files.
  - Import tools must never write directly into any `data/*.json` file. [file:1018]

- **Promotion is explicit and validated**:
  - Canonical JSON updates for `data/*.json` are always full-file replacements performed via explicit promotion steps and Git commits, never in-place edits.
  - Promotion must follow the validation flow in sections 5 and 6 of this runbook. [file:1018]


## 3. File locations and naming

### 3.1 Snapshot files (`raw-imports/*-snapshot.json`)

All external snapshots and intermediate outputs live under `raw-imports/`. Nothing in `raw-imports/` is canonical; these files are inputs, previews, or scratch artifacts for the import pipeline. [file:1022][file:1018]

Primary snapshot naming (ESO-Hub):

- Skills snapshot:
  - `raw-imports/skills-esohub-snapshot.json`
- Sets snapshot:
  - `raw-imports/sets-esohub-snapshot.json`
- CP stars snapshot:
  - `raw-imports/cp-esohub-snapshot.json` [file:1021][file:1022]

Optional alternative snapshots (e.g. UESP-aligned) must be clearly named:

- `raw-imports/skills-uesp-snapshot.json`
- `raw-imports/sets-uesp-snapshot.json`
- `raw-imports/cp-uesp-snapshot.json`


#### 3.1.1 Skills snapshot example

A minimal ESO-Hub–aligned skills snapshot entry may look like:

```json
[
  {
    "external_id": "eso-hub:skill:warden:animal-companions:deep-fissure",
    "url": "https://eso-hub.com/en/skills/warden/animal-companions/deep-fissure",
    "name": "Deep Fissure",
    "class": "Warden",
    "skill_line": "Animal Companions",
    "role": "Active",
    "morph_of": null,

    "cost": "2700 Magicka",
    "target": "Area",
    "duration": "9 seconds",
    "max_range": "20 meters",
    "radius": "20 meters",

    "tooltip_effect": "Unleash a fissure that opens after a short delay, applying Major and Minor Breach to enemies hit.",
    "tooltip_new_effect": null,

    "source_tag": "esohub-20260213"
  }
]
