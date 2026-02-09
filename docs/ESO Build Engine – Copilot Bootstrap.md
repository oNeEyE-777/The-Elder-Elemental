# ESO Build Engine – Copilot Bootstrap

## Purpose

This document tells GitHub Copilot and other AI helpers how to work on this repository.  
It defines the architecture, non‑negotiable rules, and how changes should be made.[file:6]

The human owner is a very technical systems engineer, not a formal coder.  
All AI assistance must produce complete, ready‑to-save files and avoid partial edits or hand‑wavy steps.[file:6]

---

## High-level architecture

The ESO Build Engine has three layers:[file:1][file:4][file:6]

1. **Data layer (JSON only)**  
   - Canonical, ESO‑agnostic data in `data/` (skills, effects, sets, CP, rules).  
   - Build definitions in `builds/` that reference only IDs from the data center.

2. **Logic layer (Python)**  
   - Pure Python tools in `tools/` that:
     - Validate data and builds.
     - Aggregate effects.
     - Run rule checks (bars, gear, CP, stacking, pillars).[file:3][file:4]
   - No ESO math or game logic is duplicated outside these tools and JSON data.[file:1][file:3]

3. **Presentation / UI layer**  
   - Selector-only UIs (no free‑text build editing).  
   - Frontend reads the JSON and uses validator/math outputs; it does not invent its own rules.[file:1][file:4]

Git and this repo are the **single source of truth**.[file:1][file:4][file:24]

---

## Non‑negotiable rules

Copilot must follow these rules:[file:1][file:6][file:24]

1. **No hidden state, no external dependencies**
   - All logic must live in tracked repo files.
   - No reliance on external databases, services, or “remembered” instructions.
   - If a rule or formula matters, it must exist in JSON or Python here.

2. **Data/logic separation**
   - JSON files in `data/` define skills, effects, sets, CP, global rules.[file:1][file:2][file:4]
   - JSON files in `builds/` define builds using only IDs and numeric knobs.[file:1][file:2]
   - Python in `tools/` reads JSON, validates, aggregates, and reports.[file:3][file:4]
   - Do not hardcode ESO rules in random code locations; centralize in data or well‑named rule modules.

3. **Full-file edits only**
   - When proposing changes, always output the **entire file content** as it should exist after the change.
   - Do not say “insert X above Y” or “replace the third function”.  
   - The human will copy‑paste complete files into VS Code.

4. **Validation first**
   - Prefer adding or improving validation tools before adding complex new features.[file:3][file:4][file:7]
   - New data or build formats should come with:
     - A validator script.
     - At least one small test build or test file.

5. **Respect existing docs**
   - The following docs in `docs/` are authoritative:[file:1][file:2][file:3][file:4][file:5][file:7][file:24]
     - `ESO-Build-Engine-Overview.md` (overall project overview).
     - `ESO-Build-Engine-Data-Model-v1.md` (data model v1).
     - `ESO-Build-Engine-Global-Rules.md` (global rules and validation layer).
     - `ESO-Build-Engine-Data-Center-Scope.md` (data center & tools scope).
     - `ESO Build Database Project Specification.md` (downstream database project).
     - `ESO Build Engine – Data Center Tool Checklist.md` (status of data center tools).
   - If code conflicts with docs, either:
     - Update the docs first (if the new design is genuinely better), or
     - Update the code to match the docs.

---

## Expected repository structure

At minimum, this repo uses:[file:1][file:2][file:3][file:4][file:7][file:24]

- `data/`  
  - `skills.json`  
  - `effects.json`  
  - `sets.json`  
  - `cp-stars.json`  
  - (and any future data files documented in `docs/` such as `mundus.json`, `food.json`, `enchants.json`).

- `builds/`  
  - One JSON per build (e.g., `permafrost-marshal.json`, plus test builds like `test-dummy.json`).[file:2][file:4][file:7]

- `tools/`  
  - Python scripts such as:
    - `validate_build_test.py` – validate `test-dummy` build structure and references.[file:4][file:7]
    - `export_build_test_md.py` – export Markdown for `test-dummy`.[file:4][file:7]
    - `validate_build.py` – validate any build (structure, IDs, global rules).[file:3][file:4][file:7]
    - `export_build_md.py` – generate Markdown grid for any build.[file:4][file:7]
    - `aggregate_effects.py` – compute active buffs/debuffs for a build.[file:3][file:4][file:7]
    - `compute_pillars.py` – evaluate pillar requirements (resist, health, speed, HoTs, shields, core combo).[file:3][file:4][file:7]
    - `validate_data_integrity.py` – check data file consistency (unique IDs, valid references).[file:4][file:7]
    - Additional validators and utilities as the project grows (e.g., `llm_helper.py` for local LLM integrations).[file:4][file:7]

- `backend/`  
  - Node/Express/TypeScript API that:
    - Reads JSON from `data/` and `builds/`.
    - Exposes endpoints for data and builds (`/api/data/*`, `/api/builds/*`).[file:4]
    - Uses types aligned with the v1 Data Model.[file:2][file:4]

- `frontend/`  
  - React/Vite UI that:
    - Provides selector-only inputs for skills, sets, CP, etc.
    - Never allows free-text editing of core ESO entities.
    - Reads from the backend API and reflects validator/math outputs.[file:1][file:4]

- `docs/`  
  - This bootstrap file.
  - Architecture and scope docs (Overview, Data Model v1, Global Rules, Data Center Scope, Tool Checklist, Database Specification, Spaces-related control docs).[file:1][file:2][file:3][file:4][file:5][file:7][file:23][file:24][file:25]

If this structure needs to evolve, update this bootstrap file in the same commit.

---

## How Copilot should behave

When assisting in this repo, Copilot (or any AI helper) should:[file:6][file:24]

1. **Ask for context when unclear**
   - If a change is ambiguous, ask which doc or rule to follow.
   - Do not invent ESO mechanics or project rules.

2. **Align with the data-first design**
   - Prefer changing JSON + validators over hardcoding logic in UI or ad‑hoc scripts.
   - Keep builds thin: IDs and numeric values only, no embedded ESO rules.[file:1][file:2][file:3]

3. **Support a systems engineer, not a full-time coder**
   - Use clear, direct code.
   - Avoid clever one‑liners that are hard to read.
   - Add short, practical comments where they help understanding.

4. **Provide runnable, testable outputs**
   - When adding or changing a tool in `tools/`, include:
     - A `main` entry point or clear usage pattern.
     - Example command lines or usage notes in comments or docs.[file:4][file:7]

---

## Workflow expectations

Typical human workflow:[file:4][file:6][file:24]

1. Pull latest changes.
2. Edit JSON or Python files as complete units.
3. Run validators and tools locally (e.g., `python tools/validate_data_integrity.py`, `python tools/validate_build.py --build builds/permafrost-marshal.json`).[file:4][file:7]
4. Review outputs and diffs.
5. Commit with clear messages.

Copilot should optimize for this workflow, not for rapid, opaque edits.

---

## When in doubt

If there is any conflict between:

- What Copilot “thinks” is best, and  
- What this document and the other `docs/` files specify,

then **the docs win**.[file:1][file:3][file:4][file:6][file:24]

Propose doc updates explicitly if you believe a change is necessary.
