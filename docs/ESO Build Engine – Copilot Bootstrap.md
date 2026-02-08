# ESO Build Engine – Copilot Bootstrap

## Purpose

This document tells GitHub Copilot and other AI helpers how to work on this repository.  
It defines the architecture, non‑negotiable rules, and how changes should be made.

The human owner is a very technical systems engineer, not a formal coder.  
All AI assistance must produce complete, ready‑to-save files and avoid partial edits or hand‑wavy steps.

---

## High-level architecture

The ESO Build Engine has three layers:

1. **Data layer (JSON only)**  
   - Canonical, ESO‑agnostic data in `data/` (skills, effects, sets, CP, rules).  
   - Build definitions in `builds/` that reference only IDs from the data center.

2. **Logic layer (Python)**  
   - Pure Python tools in `tools/` that:
     - Validate data and builds.
     - Aggregate effects.
     - Run rule checks (bars, gear, CP, stacking, pillars).
   - No ESO math or game logic is duplicated outside these tools and JSON data.

3. **Presentation / UI layer**  
   - Selector-only UIs (no free‑text build editing).  
   - Frontend reads the JSON and uses the Python tools’ outputs; it does not invent its own rules.

Git and this repo are the **single source of truth**.

---

## Non‑negotiable rules

Copilot must follow these rules:

1. **No hidden state, no external dependencies**
   - All logic must live in tracked repo files.
   - No reliance on external databases, services, or “remembered” instructions.
   - If a rule or formula matters, it must exist in JSON or Python here.

2. **Data/logic separation**
   - JSON files in `data/` define skills, effects, sets, CP, global rules.
   - JSON files in `builds/` define builds using only IDs and numeric knobs.
   - Python in `tools/` reads JSON, validates, aggregates, and reports.
   - Do not hardcode ESO rules in random code locations; centralize in data or well‑named rule modules.

3. **Full-file edits only**
   - When proposing changes, always output the **entire file content** as it should exist after the change.
   - Do not say “insert X above Y” or “replace the third function”.  
   - The human will copy‑paste complete files into VS Code.

4. **Validation first**
   - Prefer adding or improving validation tools before adding complex new features.
   - New data or build formats should come with:
     - A validator script.
     - At least one small test build or test file.

5. **Respect existing docs**
   - The following docs in `docs/` are authoritative:
     - Overall project overview.
     - Data model v1.
     - Global rules and validation layer.
     - Data center & tools scope.
   - If code conflicts with docs, either:
     - Update the docs first (if the new design is genuinely better), or
     - Update the code to match the docs.

---

## Expected repository structure

At minimum, this repo uses:

- `data/`
  - `data-skills.json`
  - `data-effects.json`
  - `data-sets.json`
  - `data-cp.json`
  - (and any future data files documented in `docs/`)

- `builds/`
  - One JSON per build (e.g., `permafrost-marshal.json`).

- `tools/`
  - Python scripts like:
    - `validate_data_center.py`
    - `validate_build_structural.py`
    - `aggregate_effects.py`
    - Additional validators and utilities as the project grows.

- `docs/`
  - This bootstrap file.
  - Architecture and scope docs.

If this structure needs to evolve, update this bootstrap file in the same commit.

---

## How Copilot should behave

When assisting in this repo, Copilot should:

1. **Ask for context when unclear**
   - If a change is ambiguous, ask the human which doc or rule to follow.
   - Do not invent ESO mechanics or project rules.

2. **Align with the data-first design**
   - Prefer changing JSON + validators over hardcoding logic in UI or ad‑hoc scripts.
   - Keep builds thin: IDs and numeric values only, no embedded ESO rules.

3. **Support a systems engineer, not a full-time coder**
   - Use clear, direct code.
   - Avoid clever one‑liners that are hard to read.
   - Add short, practical comments where they help understanding.

4. **Provide runnable, testable outputs**
   - When adding or changing a tool in `tools/`, include:
     - A `main` entry point or clear usage pattern.
     - Example command lines or usage notes in comments or docs.

---

## Workflow expectations

Typical human workflow:

1. Pull latest changes.
2. Edit JSON or Python files as complete units.
3. Run validators and tools locally.
4. Review outputs and diffs.
5. Commit with clear messages.

Copilot should optimize for this workflow, not for rapid, opaque edits.

---

## When in doubt

If there is any conflict between:
- What Copilot “thinks” is best, and
- What this document and the other `docs/` files specify,

then **the docs win**. Propose doc updates explicitly if you believe a change is necessary.
