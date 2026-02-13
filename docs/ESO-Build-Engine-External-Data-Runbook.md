# ESO Build Engine – External Data Runbook

## 1. Purpose

This runbook defines how external ESO data (such as UESP-aligned exports) is brought into the ESO Build Engine v1 Data Center using offline snapshots and import tools. It complements the Overview, v1 Data Model, Global Rules, External Data Scope, and Alignment Control docs that define schemas, IDs, and process-level non-negotiables.

## 2. Rules for External Data

All external ESO data is ingested offline from frozen snapshots; there are no live HTTP or API calls from tools, the backend, or the frontend.

- No tool in `tools/` may perform live HTTP requests or call external APIs.
- No external databases or hidden configuration stores are allowed; all imported data must exist as tracked files in the repo.
- Canonical ESO data lives only under `data/`:
  - `data/skills.json`
  - `data/effects.json`
  - `data/sets.json`
  - `data/cp-stars.json`
- Import tools may write only under `raw-imports/` during development and preview; they must never write directly into any `data/*.json` file.
- Canonical JSON updates for `data/*.json` are always full-file replacements performed via explicit promotion steps and Git commits, not in-place edits.

## 3. File Locations and Naming

All external snapshots and intermediate outputs live under `raw-imports/`. Nothing in `raw-imports/` is canonical; these files are inputs, previews, or scratch artifacts for the import pipeline.

Recommended naming for raw external dumps:

- `raw-imports/uesp-skills-raw-YYYYMMDD.json`
- `raw-imports/uesp-sets-raw-YYYYMMDD.json`
- `raw-imports/uesp-cp-raw-YYYYMMDD.json`

Recommended naming for normalized modeling snapshots (small, hand-curated or pre-processed views used by the import tools):

- `raw-imports/skills.snapshot.json`
- `raw-imports/sets.snapshot.json`
- `raw-imports/cp-stars.snapshot.json`

### 3.1 Snapshot JSON examples

These examples show minimal shapes aligned to the v1 Data Model import appendices (abilityId/internalName for skills, setId/setName for sets, cpId/cpName for CP). They are not canonical; they are typical inputs that importers will read.

#### 3.1.1 `raw-imports/skills.snapshot.json`

```json
{
  "skills": [
    {
      "abilityId": 86112,
      "internalName": "Deep Fissure",
      "classTag": "Warden",
      "skillLineTag": "Warden Animal Companions",
      "mechanicType": "Magicka",
      "baseCost": 2700,
      "castTimeType": "instant",
      "targetType": "area",
      "baseDurationSeconds": 9,
      "radiusMeters": 20,
      "isUltimate": false,
      "isPassive": false,
      "rawTooltipText": "Unleash a fissure that opens after a short delay, applying Major and Minor Breach to enemies hit.",
      "sourceTag": "uesp-YYYYMMDD"
    }
  ]
}
```

#### 3.1.2 `raw-imports/sets.snapshot.json`

```json
{
  "sets": [
    {
      "setId": 404,
      "setName": "Mark of the Pariah",
      "setType": "armor",
      "setSource": "overland",
      "setTags": ["pvp", "tank"],
      "bonusRows": [
        {
          "piecesRequired": 5,
          "bonusTooltipRaw": "Increases your Physical and Spell Resistance the lower your Health, up to a maximum value.",
          "bonusEffectIdentifiers": []
        }
      ]
    }
  ]
}
```

#### 3.1.3 `raw-imports/cp-stars.snapshot.json`

```json
{
  "cpStars": [
    {
      "cpId": 1,
      "cpName": "Ironclad",
      "cpTree": "Warfare",
      "slotType": "slottable",
      "cpTooltipRaw": "Reduces damage taken from direct damage attacks.",
      "cpTags": ["defense", "mitigation"],
      "cpEffectIdentifiers": []
    }
  ]
}
```

## 4. Import Preview Tools

The import preview tools read snapshot files under `raw-imports/`, normalize them to the v1 Data Model, and write preview JSONs back into `raw-imports/`. They never write to `data/*.json`.

### 4.1 Skills import preview

Tool: `tools/import_skills_from_uesp.py`

Command (from repo root):

```powershell
python tools\import_skills_from_uesp.py --snapshot-path raw-imports\skills.snapshot.json
```

Preview output:

- `raw-imports/skills.import-preview.json`

This preview file contains a top-level skills container using the canonical `data/skills.json` shape, with stable `skill.*` IDs, v1 fields (such as `class_id`, `skill_line_id`, `resource`, `duration_seconds`), and an `effects` array per skill. For now, effect references may be empty until the full mapping is implemented.

### 4.2 Sets import preview

Tool: `tools/import_sets_from_uesp.py`

Command:

```powershell
python tools\import_sets_from_uesp.py --snapshot-path raw-imports\sets.snapshot.json
```

Preview output:

- `raw-imports/sets.import-preview.json`

This preview file contains a top-level sets container matching `data/sets.json`, with `set.*` IDs, human-readable names, type/source/tags fields, and `bonuses` arrays. Each bonus tier includes `pieces`, `tooltip_raw`, and an `effects` array (currently empty) for downstream wiring.

### 4.3 CP stars import preview

Tool: `tools/import_cp_from_uesp.py`

Command:

```powershell
python tools\import_cp_from_uesp.py --snapshot-path raw-imports\cp-stars.snapshot.json
```

Preview output:

- `raw-imports/cp-stars.import-preview.json`

This preview file mirrors the `data/cp-stars.json` schema, with `cp.*` IDs, tree and slot type fields, `tooltip_raw`, and an `effects` array that will eventually carry canonical effect IDs (currently empty during early iterations).

Across all three preview files, the intent is to express canonical IDs and v1 Data Model fields, using `effects: []` as a safe default until curated effect mappings are in place.

## 5. Preview Validation and Promotion

The validation and promotion flow ensures that canonical `data/*.json` files only change via well-checked full-file replacements.

### 5.1 Preview validation

A dedicated validator exists for skills preview files:

- Tool: `tools/validate_import_preview.py`

This validator reads `raw-imports/skills.import-preview.json`, checks that it matches the v1 skill schema and ID rules, and reports any structural or referential issues.

Similar validators for sets and CP previews will be added later (for example, `tools/validate_import_preview_sets.py`, `tools/validate_import_preview_cp.py`), and will become required once they exist.

### 5.2 Promotion (future)

A future promotion tool (for example, `tools/promote_import_preview.py`) will handle the controlled update of canonical data files:

- Read preview files:
  - `raw-imports/skills.import-preview.json`
  - `raw-imports/sets.import-preview.json`
  - `raw-imports/cp-stars.import-preview.json`
- Write full replacement canonical files:
  - `data/skills.json`
  - `data/sets.json`
  - `data/cp-stars.json`

Promotion rules:

- All preview validators must pass successfully (skills, sets, CP).
- After writing new `data/*.json` files, `python tools\validate_data_integrity.py` must succeed, confirming ID uniqueness, namespace prefixes, and cross-file references.
- Promotion is a manual, deliberate action, followed by Git diff review and a single commit that captures both preview and canonical changes.

## 6. External Data Update Checklist

Use this checklist for each external data update cycle (for example, when aligning to a new ESO patch or refreshed UESP export):

1. Acquire raw external data and save it under `raw-imports/uesp-*-raw-YYYYMMDD.json` (skills, sets, CP), keeping the files frozen for that run.
2. Prepare normalized modeling snapshots under `raw-imports/*.snapshot.json` (skills, sets, CP), either by hand-curation or thin transformation from the raw dumps.
3. Run the three import preview tools against the snapshots:
   - `python tools\import_skills_from_uesp.py --snapshot-path raw-imports\skills.snapshot.json`
   - `python tools\import_sets_from_uesp.py --snapshot-path raw-imports\sets.snapshot.json`
   - `python tools\import_cp_from_uesp.py --snapshot-path raw-imports\cp-stars.snapshot.json`
4. Run preview validators (currently `tools/validate_import_preview.py` for skills, with sets/CP equivalents added later) and fix any reported issues before proceeding.
5. (Future) Run the promotion tool to overwrite `data/skills.json`, `data/sets.json`, and `data/cp-stars.json` from the validated preview files.
6. Run `python tools\validate_data_integrity.py` to confirm canonical data consistency, and rerun any build validators as needed.
7. Commit all related changes together (raw dumps, snapshots, previews, and updated `data/*.json` if promotion occurred) in a single cohesive Git commit.
