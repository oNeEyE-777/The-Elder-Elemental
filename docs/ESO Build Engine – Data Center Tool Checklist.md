# ESO Build Engine – Data Center Tool Checklist

Source: Derived from `docs/ESO-Build-Engine-Data-Center-Scope.md`.[file:17]

## Status Legend

- [DONE] – Implemented and tested locally.
- [PLANNED] – Agreed but not implemented yet.
- [LATER] – Future / optional work.[file:20]

---

## Core Software Stack

These must be installed and working:[file:17][file:20]

- [DONE] Git – Version control for the entire repo.
- [DONE] Python 3.10+ – Automation scripts and validators (your environment: Python 3.14.3 as `python`).
- [PLANNED] Node.js 18+ – Backend API and frontend build tooling.
- [DONE] VS Code (or preferred editor) – Primary editing environment.
- [DONE] GitHub Desktop – Local Git workflow (clone, commit, push, “open in terminal”).
- [LATER] LM Studio – Optional, later, for local LLM integration.[file:20]

---

## Data Files Required for Tools

All ESO data lives in JSON under `data/`, and builds under `builds/`.[file:17][file:20]

### Global data JSONs

- [DONE] `data/skills.json`  
  Skills with metadata, costs, durations, effect IDs.  
  Used by: frontend selectors, validators, MD exporter.[file:17][file:20]

- [DONE] `data/effects.json`  
  Buffs/debuffs with math (types, values, stacking).  
  Used by: effect aggregation, pillars, tooltip display.[file:17][file:20]

- [DONE] `data/sets.json`  
  Sets with bonuses per piece count.  
  Used by: gear selectors, set bonus calculation.[file:17][file:20]

- [DONE] `data/cp-stars.json`  
  CP stars with tree, slot type, effect IDs.  
  Used by: CP selectors, effect aggregation.[file:17][file:20]

### Build records

- [DONE] `builds/test-dummy.json`  
  Test build for pipeline validation.[file:20]

- [DONE] `builds/test-dummy.md`  
  Generated Markdown export for test build (tool output only).[file:20]

- [DONE] `builds/permafrost-marshal.json`  
  Real build (after test pipeline passes).[file:17][file:15]

- [DONE] `builds/permafrost-marshal.md`  
  Generated Markdown export for real build (tool output only).[file:17]

**Data integrity requirements:** valid JSON syntax, unique IDs per file, valid references into `data/effects.json`, and schema conformance to the Data Model v1 doc.[file:17][file:20]

---

## Python Tools – Phase 1 (Test Pipeline)

Minimum viable tool set to prove the pipeline before real data.[file:17][file:20]

- [DONE] `tools/validate_build_test.py`  
  Purpose: Validate `test-dummy` build structure and references.  
  Inputs: `data/*.json`, `builds/test-dummy.json`  
  Output: Console OK or list of violations (file, field, description).[file:20]

- [DONE] `tools/export_build_test_md.py`  
  Purpose: Generate Markdown grid for `test-dummy` build.  
  Inputs: `data/*.json`, `builds/test-dummy.json`  
  Output: `builds/test-dummy.md` (generated, never hand-edited).[file:20]

---

## Python Tools – Phase 2 (Real Build)

Expanded tools used once the test pipeline is proven.[file:17][file:20]

- [PLANNED] `tools/validate_build.py`  
  Purpose: Validate any build (structure, IDs, global rules).  
  Inputs: `data/*.json`, `builds/<build_id>.json`  
  Output: Console violations list or OK.[file:17][file:20]

- [PLANNED] `tools/export_build_md.py`  
  Purpose: Generate Markdown grid for any build.  
  Inputs: `data/*.json`, `builds/<build_id>.json`  
  Output: `builds/<build_id>.md`.[file:17][file:20]

- [DONE] `tools/aggregate_effects.py`  
  Purpose: Compute all active buffs/debuffs for a build.  
  Inputs: `data/*.json`, `builds/<build_id>.json`  
  Output: JSON aggregated effect instances list.[file:17][file:5]

- [PLANNED] `tools/compute_pillars.py`  
  Purpose: Validate pillar requirements (resist, health, speed, HoTs, shields, core combo).  
  Inputs: `data/*.json`, `builds/<build_id>.json`  
  Output: JSON pillar status per pillar.[file:17][file:20]

- [PLANNED] `tools/validate_data_integrity.py`  
  Purpose: Check data file consistency (unique IDs, valid references).  
  Inputs: `data/*.json`  
  Output: Console data integrity report (OK or list of problems).[file:17][file:20]

- [PLANNED] `tools/llm_helper.py` (optional)  
  Purpose: LM Studio / local LLM integration helper.  
  Inputs/Outputs: Repo files as needed; logs to `logs/llm/`.[file:17][file:20]
