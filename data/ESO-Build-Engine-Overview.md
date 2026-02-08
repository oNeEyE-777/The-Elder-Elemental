# Doc 1 - ESO Build Engine – Overview & Non‑Negotiables **docs/ESO-Build-Engine-Overview.md**

## Purpose

Define what the ESO Build Engine is, and the non‑negotiable rules for how it is built and how AI is allowed to interact with it.​

## High‑level description

We are building a **data‑driven ESO build engine**, starting with a single build: **Permafrost Marshal** (Warden / Necromancer / Dragonknight, PvP, high‑speed tank).

The system has three layers:

* **Data layer**: JSON “database” files (skills, effects, sets, CP, builds).​
* **Logic layer**: validation + math over those JSONs (buff stacking, resist/speed, pillars).
* **Presentation layer**: a real web UI:
  + No flat text entry for core game entities.
  + Users select skills/sets/CP/etc. from global data, and the UI auto‑populates tooltips and derived fields.​

Markdown build grids (like Permafrost Marshal) are **generated views** of the data, not sources of truth.

## Non‑negotiable process rules

* **Git repo is the single source of truth.**
  + All ESO data lives in JSON under data/.
  + All builds live in JSON under builds/.
  + Markdown grids are views, derived from build JSON, never edited by hand.​
* **No copy/paste for data or code.**
  + Changes are made via complete file contents or dedicated tools.
  + No “paste this snippet into line 47”; only full‑file replace or new file creation.
* **AI interaction constraints.**
  + AI may only operate via:
    - Complete file contents to be saved at specific paths.
    - Python tools that read/write repo files.
  + AI cannot fetch from GitHub or external APIs for this project; Git/GitHub are only for your own sync/backup/CI.​
* **Local environment controls all file I/O.**
  + All reading/writing of JSON/MD is done on the local clone (VS Code + Python scripts).
  + Backend and frontend read only from these JSON files, not from external services.

## Data‑driven, ID‑based design

* Skills, sets, CP stars, buffs, and other entities are all referenced by **IDs**, never by free text.
* Tooltips, math, and relationships are stored once, in global data tables (e.g. data/skills.json, data/effects.json, data/sets.json, data/cp-stars.json).
* Build records store only:
  + IDs (skills, sets, CP, Mundus, food/drink, enchants).
  + Numeric configuration (attributes, CP total, pillar targets, etc.).
  + No duplicated tooltip or math text in build files.

## Front end is selector‑only

* All core game entities are chosen via selectors backed by global JSON data:
  + Skills, sets, CP stars, Mundus, food/drink, enchants are selected from dropdowns/search.
* When you select an ID, the UI:
  + Looks up all details (tooltip, cost, duration, buffs, math) automatically from data/\*.json.
  + Never lets the user hand‑edit those details.

## Centralized math and validation

* Buff/debuff semantics (Major/Minor, values, stacking) live in data/effects.json as the **single source of truth**.
* Global rules (bars, gear layout, CP limits, mythic limits, etc.) are implemented in Python validators under tools/.
* Pillar checks (Resist, Health, Speed, HoTs, Shields, Core combo) are computed from:
  + Build IDs + global data + effect math.
  + Never from ad‑hoc calculations inside the UI or Markdown.

All tools and services must respect these rules: JSON + IDs are the truth, validators and math live in one place, and everything else is a generated view over that data.
