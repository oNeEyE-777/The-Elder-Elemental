\# Doc 1 – ESO Build Engine Overview \& Non‑Negotiables \*\*docs/ESO-Build-Engine-Overview.md\*\*



\## Purpose



Define what the ESO Build Engine is, and the non‑negotiable rules for how it is built and how AI is allowed to interact with it.\[file:1]\[file:6]\[file:24]



---



\## High‑level description



We are building a \*\*data‑driven ESO build engine\*\*, starting with a single build: \*\*Permafrost Marshal\*\* (Warden / Necromancer / Dragonknight, PvP, high‑speed tank).\[file:1]\[file:2]



The system has three layers:\[file:1]\[file:4]\[file:6]



\- \*\*Data layer\*\* – JSON “database” files:

&nbsp; - `data/skills.json`

&nbsp; - `data/effects.json`

&nbsp; - `data/sets.json`

&nbsp; - `data/cp-stars.json`

&nbsp; - `builds/\*.json` for per-build records.\[file:2]\[file:4]

\- \*\*Logic layer\*\* – validation and math over those JSONs:

&nbsp; - Structural rules (bars, gear, CP layout).

&nbsp; - Effect aggregation and stacking (Major/Minor, uniques).

&nbsp; - Pillar checks (resist, health, speed, HoTs, shields, core combo).\[file:3]\[file:4]

\- \*\*Presentation layer\*\* – a real web UI:

&nbsp; - No flat text entry for core game entities.

&nbsp; - Users select skills/sets/CP/etc. from global data, and the UI auto‑populates tooltips and derived fields.\[file:1]\[file:4]



Markdown build grids (like Permafrost Marshal) are \*\*generated views\*\* of the data, not sources of truth.\[file:1]\[file:4]\[file:7]



---



\## Non‑negotiable process rules



\- \*\*Git repo is the single source of truth.\*\*

&nbsp; - All ESO data lives in JSON under `data/`.

&nbsp; - All builds live in JSON under `builds/`.

&nbsp; - Markdown grids are views derived from build JSON, never edited by hand.\[file:1]\[file:4]\[file:7]

\- \*\*No partial edits or copy/paste snippets.\*\*

&nbsp; - Changes are made via complete file contents or dedicated tools.

&nbsp; - No “paste this snippet into line 47”; only full‑file replace or new file creation.\[file:1]\[file:6]\[file:24]

\- \*\*AI interaction constraints.\*\*

&nbsp; - AI may only operate via:

&nbsp;   - Complete file contents to be saved at specific paths.

&nbsp;   - Python tools under `tools/` that read/write repo files.

&nbsp; - AI must not rely on hidden state or external databases; Git/GitHub are for sync/backup/CI only.\[file:1]\[file:4]\[file:6]\[file:24]

\- \*\*Local environment controls all file I/O.\*\*

&nbsp; - All reading/writing of JSON/MD is done on the local clone (VS Code + Python scripts).

&nbsp; - Backend and frontend read only from these JSON files, not from external services at runtime.\[file:1]\[file:4]



---



\## Data‑driven, ID‑based design



\- Skills, sets, CP stars, buffs, and other entities are all referenced by \*\*IDs\*\*, never by free text.\[file:1]\[file:2]\[file:3]

\- Tooltips, math, and relationships are stored once, in global data tables:

&nbsp; - `data/skills.json`

&nbsp; - `data/effects.json`

&nbsp; - `data/sets.json`

&nbsp; - `data/cp-stars.json`

&nbsp; - Future: `data/mundus.json`, `data/food.json`, `data/enchants.json`.\[file:2]\[file:4]

\- Build records store only:

&nbsp; - IDs (skills, sets, CP, Mundus, food/drink, enchants).

&nbsp; - Numeric configuration (attributes, CP total, pillar targets, etc.).

&nbsp; - No duplicated tooltip or math text in build files.\[file:1]\[file:2]\[file:3]



This ID‑based design ensures that any change to ESO rules happens in one place and flows through validators, math, backend, frontend, and exports consistently.\[file:1]\[file:2]\[file:3]\[file:4]



---



\## Frontend is selector‑only



\- All core game entities are chosen via selectors backed by global JSON data:

&nbsp; - Skills, sets, CP stars, Mundus, food/drink, enchants are selected from dropdowns/search.\[file:1]\[file:4]

\- When you select an ID, the UI:

&nbsp; - Looks up all details (tooltip, cost, duration, buffs, math) automatically from `data/\*.json`.

&nbsp; - Never lets the user hand‑edit those details.\[file:1]\[file:4]

\- Build JSON written by the backend:

&nbsp; - Contains only IDs and numeric configuration.

&nbsp; - Is validated by Python tools before being committed.\[file:3]\[file:4]\[file:7]



The frontend’s job is to \*\*reflect\*\* the data center and validators, not to invent or duplicate ESO rules.\[file:1]\[file:4]



---



\## Centralized math and validation



\- Buff/debuff semantics (Major/Minor, values, stacking) live in `data/effects.json` as the single source of truth for effect math.\[file:2]\[file:3]\[file:4]

\- Global rules (bars, gear layout, CP limits, mythic limits, etc.) are defined in `docs/ESO-Build-Engine-Global-Rules.md` and implemented in Python validators under `tools/`.\[file:3]\[file:4]\[file:7]

\- Pillar checks (Resist, Health, Speed, HoTs, Shields, Core combo) are computed from:

&nbsp; - Build IDs + global data + effect math.

&nbsp; - Never from ad‑hoc calculations inside the UI or Markdown.\[file:1]\[file:3]\[file:4]



All tools and services must respect these rules: JSON + IDs are the truth, validators and math live in one place, and everything else is a generated view over that data.\[file:1]\[file:3]\[file:4]\[file:6]\[file:24]



