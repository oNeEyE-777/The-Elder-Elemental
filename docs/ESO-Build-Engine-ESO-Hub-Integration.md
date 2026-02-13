# ESO Build Engine – ESO-Hub Integration

## 1. Purpose

This document defines how ESO-Hub is used as the **primary external data source** for the ESO Build Engine v1 Data Center.

It sits alongside:

- `ESO-Build-Engine-Overview.md`
- `ESO-Build-Engine-Data-Model-v1.md`
- `ESO-Build-Engine-Global-Rules.md`
- `ESO-Build-Engine-Data-Center-Scope.md`
- `ESO-Build-Engine-Data-Center-Tool-Checklist.md`
- `ESO-Build-Engine-External-Data-Runbook.md`
- `ESO-Build-Engine-Alignment-Control.md` [file:927][file:930]

and specializes those documents for ESO-Hub–based external data.

Goals:

- Declare ESO-Hub as the **authoritative upstream** for skills, sets, and Champion Points tooltips and naming.
- Define the **boundary** between:
  - Local ESO-Hub crawlers/scrapers (outside this repo).
  - Import tools and canonical JSON inside this repo.
- Specify the expected **snapshot JSON shapes** coming from ESO-Hub.
- Constrain how importers map ESO-Hub snapshots into v1 Data Center schemas.

This document is normative for anything that claims to import ESO-Hub data into the Build Engine.


## 2. ESO-Hub as Primary External Source

### 2.1 Scope and trust level

ESO-Hub is designated as the **primary external source of truth** for:

- Skills:
  - Names and grouping (class, skill line, active vs passive, ultimate).
  - Tooltip header fields (cost, target, duration, range, radius, etc.).
  - Tooltip body text including numeric values and “new effect” descriptions. [web:775][page:0]
- Sets:
  - Set names, types (overland, dungeon, trial, class sets, mythic, etc.).
  - Drop sources and high-level tags.
  - Full 2–5 piece bonus tooltip text at a normalized level-50 baseline. [web:921]
- Champion Points:
  - Star names and trees (Warfare, Fitness, Craft).
  - Slottable vs passive.
  - Tooltip text and per-rank descriptions where available. [web:972]

ESO-Hub values are assumed to match in-game tooltips on an empty level 50 character, as documented on their skills and sets pages. [web:775][web:921]


### 2.2 Other external sources

Other sources (UESP, raw ESO dumps, addons, etc.) are treated as **secondary**:

- They may be used:
  - To cross-check ESO-Hub data for obvious mistakes.
  - To backfill missing fields that ESO-Hub does not expose clearly.
- They must not override the ESO-Hub baseline silently.

If a conflict between ESO-Hub and another source is discovered:

- The discrepancy must be recorded in a future “Data Corrections” section of this document or in a dedicated corrections file.
- Any corrections applied to canonical JSON must be reproducible and documented.


## 3. Separation of Concerns

### 3.1 Local crawler/scraper vs repo tools

The ESO Build Engine maintains a strict separation:

- **Local environment (outside repo)**:
  - Holds the ESO-Hub crawler/spider and HTML→snapshot scraper.
  - Is responsible for:
    - Fetching ESO-Hub HTML pages (skills, sets, CP).
    - Parsing them into compact JSON snapshots.
    - Freezing those snapshots (no in-place mutation during an import run).
  - Is *not* part of the tracked repository.

- **Repository (`data/`, `tools/`, `raw-imports/`)**:
  - Sees only **snapshot files** under `raw-imports/`.
  - Uses importers and validators to convert snapshots into canonical data.
  - Never performs live HTTP or calls any external API. [file:927][file:930]

This keeps the repo deterministic, reproducible, and independent of network access.


### 3.2 No live ESO-Hub access from repo tools

The following are explicitly forbidden inside this repo:

- Any `tools/*.py`, `backend/`, or `frontend/` code that:
  - Performs live HTTP requests to ESO-Hub or any other external site.
  - Calls any external API to fetch or update game data.
- Any persistent external database used as a hidden source of ESO data.

All ESO-Hub-derived data must flow through:

1. Local crawler/scraper → ESO-Hub snapshots.
2. Snapshots copied into `raw-imports/`.
3. Importers and validators → `data/*.json`. [file:927]


## 4. ESO-Hub Snapshot Files

### 4.1 Snapshot location and naming

All ESO-Hub snapshots live under `raw-imports/` and follow this naming pattern:

- Skills:
  - `raw-imports/skills-esohub-snapshot.json`
- Sets:
  - `raw-imports/sets-esohub-snapshot.json`
- Champion Points:
  - `raw-imports/cp-esohub-snapshot.json`

Snapshots are **frozen** for the duration of a given import run. They are not canonical; they are inputs to the import pipeline. [file:927]


### 4.2 General snapshot rules

- Snapshots must be valid UTF‑8 JSON.
- Snapshots must be arrays of objects (one object per skill/set/CP star), unless otherwise specified.
- Snapshots must include a minimal `external_id` that uniquely identifies each record in ESO-Hub terms, such as:
  - ESO-Hub URL path.
  - ESO-Hub-internal numeric ID, if available.
- Snapshots must include raw tooltip text fields that reflect what ESO-Hub shows for the relevant item at the level‑50 baseline. [web:775][web:921][web:972]


## 5. ESO-Hub Snapshot Schemas

The following sections define the expected **input shapes** for ESO-Hub snapshots, before mapping into v1 Data Center schemas.

These shapes are not the canonical in-repo schemas; they are external interchange formats expected by ESO-Hub importers.


### 5.1 Skills snapshot (`skills-esohub-snapshot.json`)

Structure:

```json
[
  {
    "external_id": "eso-hub:skill:sorcerer:dark-magic:absorption-field",
    "url": "https://eso-hub.com/en/skills/sorcerer/dark-magic/absorption-field",
    "name": "Absorption Field",
    "class": "Sorcerer",
    "skill_line": "Dark Magic",
    "role": "Ultimate",
    "morph_of": "Negate Magic",

    "cost": "225 Ultimate",
    "target": "Ground",
    "duration": "12 seconds",
    "max_range": "28 meters",
    "radius": "8 meters",

    "tooltip_effect": "Create a globe of magic suppression for 12 seconds, removing and preventing all enemy area of effect abilities from occurring in the area. Enemies within the globe are stunned, while enemy players will be silenced rather than stunned. The globe also heals you and your allies for 1038 Health every 1 second.",
    "tooltip_new_effect": "The globe also heals you and your allies standing inside it.",

    "source_tag": "esohub-YYYYMMDD"
  }
]
```

Field expectations (skills):
external_id:
Required.
Unique within the snapshot.
Stable across ESO-Hub crawls for the same skill.
url:
Required.
ESO-Hub detail page URL for this skill.
name, class, skill_line:
Required.
Values must match ESO-Hub displays. [page:0][web:775]
role:
Required.
One of: "Active", "Passive", "Ultimate", or similar categories ESO-Hub uses.
morph_of:
Optional.
Name of the base skill if this is a morph; otherwise null or omitted.
cost, target, duration, max_range, radius:
Optional but strongly recommended.
Copied directly from the ESO-Hub header spec for the skill. [page:0]
tooltip_effect:
Required.
Main tooltip effect text as shown on the ESO-Hub detail page (baseline level 50). [page:0][web:775]
tooltip_new_effect:
Optional.
“New effect” text when ESO-Hub describes how the morph differs from the base skill. [page:0]
source_tag:
Required.
Snapshot provenance marker, e.g. esohub-20260213.

### 5.2 Sets snapshot (sets-esohub-snapshot.json)

Structure:

```json
[
  {
    "external_id": "eso-hub:set:mark-of-the-pariah",
    "url": "https://eso-hub.com/en/sets/mark-of-the-pariah",
    "name": "Mark of the Pariah",

    "set_type": "overland",
    "source": "Wrothgar",
    "weight_slots": ["light", "medium", "heavy", "jewelry"],

    "bonuses": [
      {
        "pieces_required": 2,
        "bonus_tooltip_raw": "Adds 1206 Maximum Health"
      },
      {
        "pieces_required": 5,
        "bonus_tooltip_raw": "Increases your Physical and Spell Resistance the lower your Health, up to a maximum of 10206."
      }
    ],

    "source_tag": "esohub-YYYYMMDD"
  }
]
```

Field expectations (sets):
external_id:
Required.
Unique within the snapshot.
Typically derived from the ESO-Hub set URL path.
url:
Required.
ESO-Hub detail page URL for this set. [web:921]
name:
Required.
ESO-Hub set name.
set_type:
Required.
ESO-Hub category, e.g. "overland", "dungeon", "trial", "crafted", "class-set", "mythic" etc. [web:921]
source:
Optional but recommended.
ESO-Hub’s description of where the set drops (zone, dungeon, arena, etc.).
weight_slots:
Optional.
List describing which armor weights and jewelry/weapon slots the set can appear in, based on ESO-Hub’s listing.
bonuses:
Required.
Array of objects describing each bonus tier.
pieces_required:
Required; integer piece count for the tier (2, 3, 4, 5, etc.).
bonus_tooltip_raw:
Required; full text of that tier’s set bonus as shown by ESO-Hub (level‑50 baseline). [web:921]
source_tag:
Required.
esohub-YYYYMMDD-style provenance marker.

### 5.3 CP snapshot (cp-esohub-snapshot.json)

Structure:

```json
[
  {
    "external_id": "eso-hub:cp:warfare:ironclad",
    "url": "https://eso-hub.com/en/champion-points/warfare/ironclad",
    "name": "Ironclad",

    "tree": "warfare",
    "slot_type": "slottable",
    "max_rank": 50,

    "cp_tooltip_raw": "Reduces damage taken from direct damage attacks by up to 10%.",

    "ranks": [
      {
        "rank": 10,
        "tooltip": "Reduces damage taken from direct damage attacks by 2%."
      },
      {
        "rank": 50,
        "tooltip": "Reduces damage taken from direct damage attacks by 10%."
      }
    ],

    "source_tag": "esohub-YYYYMMDD"
  }
]
```

Field expectations (CP):
external_id:
Required.
Unique within the snapshot.
Typically eso-hub:cp:<tree>:<slug>.
url:
Required.
ESO-Hub detail page URL for this CP star. [web:972]
name:
Required.
CP star name.
tree:
Required.
One of: "warfare", "fitness", "craft" matching ESO-Hub. [web:972][file:930]
slot_type:
Required.
"slottable" or "passive" (or ESO-Hub’s equivalent).
max_rank:
Required.
Maximum rank for the star, per ESO-Hub.
cp_tooltip_raw:
Required.
Tooltip text summarizing the star’s effect at max rank (or ESO-Hub’s main tooltip). [web:972]
ranks:
Optional but recommended.
Array of per-rank tooltip objects.
source_tag:
Required.
esohub-YYYYMMDD-style provenance marker.

## 6. ESO-Hub Crawler / Spider Requirements

This section defines the behavioral contract for the external crawler/spider that produces URLs and snapshots. The implementation lives outside the repo but must conform to these rules.

### 6.1 Allowed roots and domains

The crawler must be restricted to:

- Domain:
  - https://eso-hub.com
- Root pages:
  - Skills: https://eso-hub.com/en/skills
  - Sets: https://eso-hub.com/en/sets
  - Champion Points: https://eso-hub.com/en/champion-points [web:775][web:921][web:972]

The crawler may follow internal links under these roots as needed to discover all detail pages.

### 6.2 URL discovery and URL lists

The crawler must produce three URL lists, stored outside the repo or as intermediate artifacts:

- skill-urls.json:
  - Array of ESO-Hub skill detail URLs, e.g.:
    - https://eso-hub.com/en/skills/sorcerer/dark-magic/absorption-field
- set-urls.json:
  - Array of ESO-Hub set detail URLs, e.g.:
    - https://eso-hub.com/en/sets/mark-of-the-pariah
- cp-urls.json:
  - Array of ESO-Hub CP star detail URLs, e.g.:
    - https://eso-hub.com/en/champion-points/warfare/ironclad

The crawler may perform breadth-first or depth-first traversal, but must:

- Deduplicate URLs.
- Avoid infinite loops (e.g., by tracking visited URLs).
- Limit itself to ESO-Hub domains and the relevant paths.

### 6.3 Snapshot scraper behavior

The snapshot scraper (which can be a separate program) must:

- Read the URL lists produced by the crawler.
- For each URL:
  - Fetch the HTML page from ESO-Hub.
  - Parse it to extract the fields defined in section 5 (skills, sets, CP).
  - Build a normalized snapshot object with:
    - external_id
    - url
    - Metadata fields (class, skill line, set_type, tree, etc.).
    - Tooltip fields.
  - Append each object to the appropriate snapshot array.
- Write the snapshot arrays into JSON files:
  - skills-esohub-snapshot.json
  - sets-esohub-snapshot.json
  - cp-esohub-snapshot.json

Once written for a given run, these snapshot files are treated as immutable inputs for the importers in this repo. [file:927]

## 7. Importers for ESO-Hub Snapshots

The importers for ESO-Hub snapshots live in `tools/` and follow the same patterns described in the External Data Runbook and Alignment Control. [file:927][file:930]

### 7.1 Tool list

The following tools are expected:

- tools/import_skills_from_esohub.py
- tools/import_sets_from_esohub.py
- tools/import_cp_from_esohub.py

Each importer:

- Accepts a `--snapshot-path` argument pointing to the appropriate ESO-Hub snapshot (skills-esohub-snapshot.json, etc.).
- Writes a preview file under `raw-imports/`:
  - Skills: raw-imports/skills.import-preview.json
  - Sets: raw-imports/sets.import-preview.json
  - CP: raw-imports/cp-stars.import-preview.json
- Never writes directly to any `data/*.json` file. [file:927][file:930]

### 7.2 Mapping to canonical Data Center schemas

The mapping must respect the v1 Data Model and Alignment Control. [file:930]

#### 7.2.1 Skills (to `data/skills.json` shape)

Given a skills snapshot row as in 5.1, `import_skills_from_esohub.py` must:

- Generate canonical skill IDs:
  - `id`: `skill.<normalized-name-or-key>`
- Map ESO-Hub fields to canonical fields, for example:

| ESO-Hub snapshot field | Canonical skill field     |
| ---------------------- | ------------------------- |
| name                   | name                      |
| tooltip_effect         | tooltipeffecttext         |
| external_id            | externalids.esohub (nested) |
| class                  | classid (mapped to your class key) |
| skill_line             | skilllineid               |
| role                   | type (active/passive/ultimate) |
| cost                   | cost (parsed or left as metadata) |
| duration               | durationseconds (parsed to number where feasible) |

Exact field mappings must align with `ESO-Build-Engine-Data-Model-v1.md` Appendix A and `ESO-Build-Engine-Alignment-Control.md`. [file:930]

The importer may initially leave `effects` empty or minimally populated until curated effect mappings are in place, consistent with the External Data Runbook. [file:927]

#### 7.2.2 Sets (to `data/sets.json` shape)

Given a sets snapshot row as in 5.2, `import_sets_from_esohub.py` must:

- Generate canonical set IDs:
  - `id`: `set.<normalized-name-or-key>`
- Map ESO-Hub fields to canonical fields, for example:

| ESO-Hub snapshot field     | Canonical set field    |
| -------------------------- | ---------------------- |
| name                       | name                   |
| set_type                   | type (or sourcetag mapping) |
| source                     | sourcetag or similar metadata |
| bonuses[].pieces_required  | bonuses[].pieces       |
| bonuses[].bonus_tooltip_raw | bonuses[].tooltipraw  |
| external_id                | externalids.esohub (nested) |

`effects` arrays in set bonuses may remain empty or minimal until effect mappings are defined, as with skills. [file:927][file:930]

#### 7.2.3 CP stars (to `data/cp-stars.json` shape)

Given a CP snapshot row as in 5.3, `import_cp_from_esohub.py` must:

- Generate canonical CP IDs:
  - `id`: `cp.<normalized-name-or-key>`
- Map ESO-Hub fields to canonical fields:

| ESO-Hub snapshot field | Canonical CP field              |
| ---------------------- | -------------------------------- |
| name                   | name                             |
| tree                   | tree                             |
| slot_type              | used to indicate slottable/passive in metadata |
| cp_tooltip_raw         | tooltipraw (or equivalent field in cp-stars schema) |
| external_id            | externalids.esohub (nested)      |

Again, `effects` arrays may be initially empty until canonical effect IDs are wired in. [file:927][file:930]

## 8. Hover Tooltips in the Build Engine

### 8.1 Tooltip data flow

For mouse-over tooltips in the Build Engine frontend:

- ESO-Hub snapshots populate:
  - `tooltipeffecttext` in skills.
  - `bonuses[].tooltipraw` in sets.
  - `tooltipraw` (or equivalent) in CP stars. [file:930]
- Canonical JSON (`data/skills.json`, `data/sets.json`, `data/cp-stars.json`) is served by the backend to the frontend.
- The frontend:
  - Renders skills, sets, and CP stars by their canonical IDs (e.g. `skill.deepfissure`, `set.markofthepariah`, `cp.ironclad`). [file:930]
  - On hover, looks up the corresponding object and displays a tooltip component populated from those text fields.
- Tooltips in the UI must never be fetched directly from ESO-Hub at runtime; they must come from the Data Center JSON files.

### 8.2 Consistency expectations

Tooltip text displayed in the Build Engine should match ESO-Hub’s baseline tooltips for the relevant patch, modulo:

- Minor formatting differences.
- Explicit corrections documented separately if ESO-Hub is demonstrably wrong.

Any transformation that changes meaning (e.g. rewording, changing numbers) must be treated as a correction and documented.

## 9. Validation and Promotion

ESO-Hub importers participate in the same validation and promotion flows defined in:

- `ESO-Build-Engine-External-Data-Runbook.md`
- `ESO-Build-Engine-Alignment-Control.md` [file:927][file:930]

Key points:

- Importers write only to:
  - `raw-imports/skills.import-preview.json`
  - `raw-imports/sets.import-preview.json`
  - `raw-imports/cp-stars.import-preview.json`
- Preview validators ensure these files:
  - Match canonical schemas.
  - Use proper ID prefixes (`skill.`, `set.`, `cp.`).
- Promotion tools (current or future) are the only mechanisms allowed to overwrite:
  - `data/skills.json`
  - `data/sets.json`
  - `data/cp-stars.json`
- After promotion, `tools/validate_data_integrity.py` and build validators must pass before changes are committed. [file:927][file:930]

## 10. Change Management

This document controls:

- Which external source is treated as primary (ESO-Hub).
- How ESO-Hub snapshots must be structured.
- How importers map those snapshots into canonical data.

Any change to:

- Snapshot shapes,
- Importer behavior,
- The role of ESO-Hub vs other sources,

must be accompanied by an update to this document and any affected sections in:

- `ESO-Build-Engine-External-Data-Runbook.md`
- `ESO-Build-Engine-Alignment-Control.md`
- `ESO-Build-Engine-Data-Model-v1.md` [file:927][file:930]

No tool or JSON format is allowed to introduce ad-hoc shortcuts, schema drift, or alternative external sources that bypass the processes defined here.
