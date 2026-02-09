# ESO Build Engine – Data Center Tool Checklist **docs/ESO-Build-Engine-Data-Center-Tool-Checklist.md**

Source: Derived from `docs/ESO-Build-Engine-Data-Center-Scope.md`.[file:4]

## Status Legend

- [DONE] – Implemented and tested locally.
- [PLANNED] – Agreed but not implemented yet.
- [LATER] – Future / optional work.[file:7]

---

## Core Software Stack

These must be installed and working:[file:4][file:7]

- [DONE] Git – Version control for the entire repo.
- [DONE] Python 3.10+ – Automation scripts and validators (your environment: Python 3.14.3 as `python`).
- [PLANNED] Node.js 18+ – Backend API and frontend build tooling.
- [DONE] VS Code (or preferred editor) – Primary editing environment.
- [DONE] GitHub Desktop – Local Git workflow (clone, commit, push, “open in terminal”).
- [LATER] LM Studio – Optional, later, for local LLM integration.

---

## Data Files Required for Tools

All ESO data lives in JSON under `data/`, and builds under `builds/`.[file:4][file:7]

### Global data JSONs

- [DONE] `data/skills.json`  
  Skills with metadata, costs, durations, effect IDs.  
  Used by: frontend selectors, validators, MD exporter.[file:2][file:4][file:7]

- [DONE] `data/effects.json`  
  Buffs/debuffs with math (types, values, stacking).  
  Used by: effect aggregation, pillars, tooltip display.[file:2][file:3][file:4][file:7]

- [DONE] `data/sets.json`  
  Sets with bonuses per piece count.  
  Used by: gear selectors, set bonus calculation.[file:2][file:3][file:4][file:7]

- [DONE] `data/cp-stars.json`  
  CP stars with tree, slot type, effect IDs.  
  Used by: CP selectors, effect aggregation.[file:2][file:3][file:4][file:7]

### Build records

- [DONE] `builds/test-dummy.json`  
  Test build for pipeline validation.[file:4][file:7]

- [DONE] `builds/test-dummy.md`  
  Generated Markdown export for test build (tool output only).[file:4][file:7]

- [PLANNED] `builds/permafrost-marshal.json`  
  Real build (after test pipeline passes).[file:2][file:4][file:7]

- [PLANNED] `builds/permafrost-marshal.md`  
  Generated Markdown export for real build (tool output only).[file:4][file:7]

**Data integrity requirements:** valid JSON syntax, unique IDs per file, valid references into `data/effects.json`, and schema conformance to the Data Model v1 doc.[file:2][file:4][file:7]

---

## Python Tools – Phase 1 (Test Pipeline)

Minimum viable tool set to prove the pipeline before real data.[file:4][file:7]

- [DONE] `tools/validate_build_test.py`  
  Purpose: Validate `test-dummy` build structure and references.  
  Inputs: `data/*.json`, `builds/test-dummy.json`  
  Output: Console OK or list of violations (file, field, description).

- [DONE] `tools/export_build_test_md.py`  
  Purpose: Generate Markdown grid for `test-dummy` build.  
  Inputs: `data/*.json`, `builds/test-dummy.json`  
  Output: `builds/test-dummy.md` (generated, never hand-edited).

---

## Python Tools – Phase 2 (Real Build)

Expanded tools used once the test pipeline is proven.[file:4][file:7]

- [PLANNED] `tools/validate_build.py`  
  Purpose: Validate any build (structure, IDs, global rules).  
  Inputs: `data/*.json`, `builds/<build_id>.json`  
  Output: Console violations list or OK.

- [PLANNED] `tools/export_build_md.py`  
  Purpose: Generate Markdown grid for any build.  
  Inputs: `data/*.json`, `builds/<build_id>.json`  
  Output: `builds/<build_id>.md`.

- [PLANNED] `tools/aggregate_effects.py`  
  Purpose: Compute all active buffs/debuffs for a build.  
  Inputs: `data/*.json`, `builds/<build_id>.json`  
  Output: JSON aggregated effect instances list.

- [PLANNED] `tools/compute_pillars.py`  
  Purpose: Validate pillar requirements (resist, health, speed, HoTs, shields, core combo).  
  Inputs: `data/*.json`, `builds/<build_id>.json`  
  Output: JSON pillar status per pillar.

- [PLANNED] `tools/validate_data_integrity.py`  
  Purpose: Check data file consistency (unique IDs, valid references).  
  Inputs: `data/*.json`  
  Output: Console data integrity report (OK or list of problems).

- [PLANNED] `tools/llm_helper.py` (optional)  
  Purpose: LM Studio / local LLM integration helper.  
  Inputs/Outputs: Repo files as needed; logs to `logs/llm/`.[file:4][file:7]
