ESO Build Engine – Data Center Tool Checklist
Source: Derived from docs/ESO-Build-Engine-Data-Center-Scope.md (Doc 4).
​

1. Core Software Stack
These must be installed and working:

Git – Version control for the entire repo.
​

Python 3.10+ – Automation scripts and validators (your environment: Python 3.14.3 as python).
​

Node.js 18+ – Backend API and frontend build tooling.
​

VS Code (or preferred editor) – Primary editing environment.
​

GitHub Desktop – Local Git workflow (clone, commit, push, “open in terminal”).
​

LM Studio – Optional, later, for local LLM integration.
​

2. Data Files Required for Tools
All ESO data lives in JSON under data/, and builds under builds/.
​

Global data JSONs
data/skills.json

Skills with metadata, costs, durations, effect IDs.

Used by: frontend selectors, validators, MD exporter.
​

data/effects.json

Buffs/debuffs with math (types, values, stacking).

Used by: effect aggregation, pillars, tooltip display.
​

data/sets.json

Sets with bonuses per piece count.

Used by: gear selectors, set bonus calculation.
​

data/cp-stars.json

CP stars with tree, slot type, effect IDs.

Used by: CP selectors, effect aggregation.
​

Build records
builds/test-dummy.json

Test build for pipeline validation.
​

builds/test-dummy.md

Generated Markdown export for test build (tool output only).
​

builds/permafrost-marshal.json

Real build (after test pipeline passes).
​

builds/permafrost-marshal.md

Generated Markdown export for real build (tool output only).
​

Data integrity requirements: valid JSON syntax, unique IDs per file, valid references into data/effects.json, and schema conformance to the Data Model doc.
​

3. Python Tools – Phase 1 (Test Pipeline)
Minimum viable tool set to prove the pipeline before real data.
​

tools/validate_build_test.py
Purpose: Validate test-dummy build structure and references.
​

Inputs: data/*.json, builds/test-dummy.json

Output: Console OK or list of violations (file, field, description).
​

tools/export_build_test_md.py
Purpose: Generate Markdown grid for test-dummy build.
​

Inputs: data/*.json, builds/test-dummy.json

Output: builds/test-dummy.md (generated, never hand-edited).
​

4. Python Tools – Phase 2 (Real Build)
Expanded tools used once the test pipeline is proven.
​

tools/validate_build.py
Purpose: Validate any build (structure, IDs, global rules).
​

Inputs: data/*.json, builds/<build_id>.json

Output: Console violations list or OK.
​

tools/export_build_md.py
Purpose: Generate Markdown grid for any build.
​

Inputs: data/*.json, builds/<build_id>.json

Output: builds/<build_id>.md.
​

tools/aggregate_effects.py
Purpose: Compute all active buffs/debuffs for a build.
​

Inputs: data/*.json, builds/<build_id>.json

Output: JSON aggregated effect instances list.
​

tools/compute_pillars.py
Purpose: Validate pillar requirements (resist, health, speed, HoTs, shields, core combo).
​

Inputs: data/*.json, builds/<build_id>.json

Output: JSON pillar status per pillar.
​

tools/validate_data_integrity.py
Purpose: Check data file consistency (unique IDs, valid references).
​

Inputs: data/*.json

Output: Console data integrity report (OK or list of problems).
​

tools/llm_helper.py (optional)
Purpose: LM Studio / local LLM integration helper.
​

Inputs/Outputs: Repo files as needed; logs to logs/llm/.