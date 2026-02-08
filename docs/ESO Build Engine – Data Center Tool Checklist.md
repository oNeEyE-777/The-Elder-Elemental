\# ESO Build Engine – Data Center Tool Checklist



Source: Derived from docs/ESO-Build-Engine-Data-Center-Scope.md (Doc 4).



\## Status Legend



\- \[DONE] – Implemented and tested locally.

\- \[PLANNED] – Agreed but not implemented yet.

\- \[LATER] – Future / optional work.



---



\## Core Software Stack



These must be installed and working:



\- \[DONE] Git – Version control for the entire repo.

\- \[DONE] Python 3.10+ – Automation scripts and validators (your environment: Python 3.14.3 as python).

\- \[PLANNED] Node.js 18+ – Backend API and frontend build tooling.

\- \[DONE] VS Code (or preferred editor) – Primary editing environment.

\- \[DONE] GitHub Desktop – Local Git workflow (clone, commit, push, “open in terminal”).

\- \[LATER] LM Studio – Optional, later, for local LLM integration.



---



\## Data Files Required for Tools



All ESO data lives in JSON under `data/`, and builds under `builds/`.



\### Global data JSONs



\- \[DONE] `data/skills.json`  

&nbsp; Skills with metadata, costs, durations, effect IDs.  

&nbsp; Used by: frontend selectors, validators, MD exporter.



\- \[DONE] `data/effects.json`  

&nbsp; Buffs/debuffs with math (types, values, stacking).  

&nbsp; Used by: effect aggregation, pillars, tooltip display.



\- \[DONE] `data/sets.json`  

&nbsp; Sets with bonuses per piece count.  

&nbsp; Used by: gear selectors, set bonus calculation.



\- \[DONE] `data/cp-stars.json`  

&nbsp; CP stars with tree, slot type, effect IDs.  

&nbsp; Used by: CP selectors, effect aggregation.



\### Build records



\- \[DONE] `builds/test-dummy.json`  

&nbsp; Test build for pipeline validation.



\- \[DONE] `builds/test-dummy.md`  

&nbsp; Generated Markdown export for test build (tool output only).



\- \[PLANNED] `builds/permafrost-marshal.json`  

&nbsp; Real build (after test pipeline passes).



\- \[PLANNED] `builds/permafrost-marshal.md`  

&nbsp; Generated Markdown export for real build (tool output only).



\*\*Data integrity requirements:\*\* valid JSON syntax, unique IDs per file, valid references into `data/effects.json`, and schema conformance to the Data Model doc.



---



\## Python Tools – Phase 1 (Test Pipeline)



Minimum viable tool set to prove the pipeline before real data.



\- \[DONE] `tools/validate\_build\_test.py`  

&nbsp; Purpose: Validate `test-dummy` build structure and references.  

&nbsp; Inputs: `data/\*.json`, `builds/test-dummy.json`  

&nbsp; Output: Console OK or list of violations (file, field, description).



\- \[DONE] `tools/export\_build\_test\_md.py`  

&nbsp; Purpose: Generate Markdown grid for `test-dummy` build.  

&nbsp; Inputs: `data/\*.json`, `builds/test-dummy.json`  

&nbsp; Output: `builds/test-dummy.md` (generated, never hand-edited).



---



\## Python Tools – Phase 2 (Real Build)



Expanded tools used once the test pipeline is proven.



\- \[PLANNED] `tools/validate\_build.py`  

&nbsp; Purpose: Validate any build (structure, IDs, global rules).  

&nbsp; Inputs: `data/\*.json`, `builds/<build\_id>.json`  

&nbsp; Output: Console violations list or OK.



\- \[PLANNED] `tools/export\_build\_md.py`  

&nbsp; Purpose: Generate Markdown grid for any build.  

&nbsp; Inputs: `data/\*.json`, `builds/<build\_id>.json`  

&nbsp; Output: `builds/<build\_id>.md`.



\- \[PLANNED] `tools/aggregate\_effects.py`  

&nbsp; Purpose: Compute all active buffs/debuffs for a build.  

&nbsp; Inputs: `data/\*.json`, `builds/<build\_id>.json`  

&nbsp; Output: JSON aggregated effect instances list.



\- \[PLANNED] `tools/compute\_pillars.py`  

&nbsp; Purpose: Validate pillar requirements (resist, health, speed, HoTs, shields, core combo).  

&nbsp; Inputs: `data/\*.json`, `builds/<build\_id>.json`  

&nbsp; Output: JSON pillar status per pillar.



\- \[PLANNED] `tools/validate\_data\_integrity.py`  

&nbsp; Purpose: Check data file consistency (unique IDs, valid references).  

&nbsp; Inputs: `data/\*.json`  

&nbsp; Output: Console data integrity report (OK or list of problems).



\- \[PLANNED] `tools/llm\_helper.py` (optional)  

&nbsp; Purpose: LM Studio / local LLM integration helper.  

&nbsp; Inputs/Outputs: Repo files as needed; logs to `logs/llm/`.



