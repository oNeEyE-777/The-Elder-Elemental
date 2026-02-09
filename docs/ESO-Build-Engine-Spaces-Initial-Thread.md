\# ESO Build Engine – Spaces Initial Thread Notes \*\*docs/ESO-Build-Engine-Spaces-Initial-Thread.md\*\*



\## 1. Attached project documents (by filename, in priority order)



For the initial alignment, the following docs were treated as primary, in this order:\[file:23]



1\. `docs/ESO-Build-Engine-Data-Center-Scope.md`

2\. `docs/ESO-Build-Engine-Overview.md`

3\. `docs/ESO-Build-Engine-Data-Model-v1.md`

4\. `docs/ESO-Build-Engine-Global-Rules.md`

5\. `docs/ESO Build Database Project Specification.md`

6\. `docs/ESO Build Engine – Data Center Tool Checklist.md`

7\. `docs/ESO Build Engine – Copilot Bootstrap.md`\[file:1]\[file:2]\[file:3]\[file:4]\[file:5]\[file:6]\[file:7]



The rest of this document follows that priority, with the Data Center scope treated as the active focus.\[file:23]\[file:4]



---



\## 2. Purpose and role of each document (relative to Data Center)



\### 1) ESO-Build-Engine-Data-Center-Scope.md (current focus) \[highest priority]



\*\*Purpose (2–3 sentences)\*\*  

Defines the complete data center for the ESO Build Engine: repo structure, data storage, Python tools, backend API, frontend, testing, deployment, and maintenance workflows.\[file:4]  

Describes what must exist in `data/`, `builds/`, `tools/`, `backend/`, `frontend/`, `logs/`, and `docs/`, and sets success criteria for the pipeline from `test-dummy` to Permafrost Marshal.\[file:4]



\*\*Fit in ESO Build Engine\*\*  

The Data Center scope is the operational contract between architecture ideas and real running code, describing how JSON, validators, API, and UI interact as a system.\[file:4]\[file:23]  

All other docs (Overview, Data Model, Global Rules, Database Spec) either feed into it (what to implement) or sit on top of it (what to build once the data center is stable).\[file:1]\[file:2]\[file:3]\[file:5]\[file:23]



---



\### 2) ESO-Build-Engine-Overview.md



\*\*Purpose (2–3 sentences)\*\*  

Defines what the ESO Build Engine is and lays out non‑negotiable rules for architecture, data/logic separation, AI usage, and Git as the single source of truth.\[file:1]  

Explains the three-layer design (JSON data, Python logic, selector-only UI) and states that Markdown build grids are generated views, never sources of truth.\[file:1]



\*\*Fit in ESO Build Engine (relative to Data Center)\*\*  

The Overview defines the constraints the Data Center scope must obey: JSON in `data/` and `builds/`, tools in `tools/`, no external runtime dependencies, and selector-only frontends.\[file:1]\[file:4]  

The Data Center doc operationalizes this by specifying concrete files, tools, and workflows that implement those non‑negotiables.\[file:4]\[file:23]



---



\### 3) ESO-Build-Engine-Data-Model-v1.md



\*\*Purpose (2–3 sentences)\*\*  

Defines the minimal JSON schemas for v1: `data/skills.json`, `data/effects.json`, `data/sets.json`, `data/cp-stars.json`, and `builds/permafrost-marshal.json`.\[file:2]  

Includes detailed example objects and key principles (IDs not free text, centralized effects, scalable shapes) for the Permafrost Marshal build.\[file:2]



\*\*Fit in ESO Build Engine (relative to Data Center)\*\*  

The v1 Data Model is the schema contract that the Data Center must enforce through validators, backend types, and frontend typing.\[file:2]\[file:4]  

The Data Center scope refers to “schema conformance” and TypeScript types; those derive directly from this document and must be kept in sync.\[file:2]\[file:4]\[file:23]



---



\### 4) ESO-Build-Engine-Global-Rules.md



\*\*Purpose (2–3 sentences)\*\*  

Defines structural rules (bars, gear, CP layout), set/CP constraints, and effect stacking logic, plus Python function contracts for validators and helpers.\[file:3]  

Specifies expected behaviors for `validate\_build\_structure`, `aggregate\_effects`, `validate\_effect\_stack\_rules`, and `create\_empty\_build\_template`.\[file:3]



\*\*Fit in ESO Build Engine (relative to Data Center)\*\*  

Global Rules describe what Python validators and effect math must do, while the Data Center scope describes where those tools live and how they’re run (`tools/\*.py`, logs, CLI usage).\[file:3]\[file:4]  

The Data Center’s tools list (`validate\_build.py`, `aggregate\_effects.py`, `compute\_pillars.py`) must be implemented to satisfy the contracts in Global Rules.\[file:3]\[file:4]\[file:7]\[file:23]



---



\### 5) ESO Build Database Project Specification.md



\*\*Purpose (2–3 sentences)\*\*  

Describes a larger ESO build database project: canonical ESO data keyed by official IDs, meta-layer tables for builds/rotations/gear, an API layer, frontend, and potential addon.\[file:5]  

Lays out a phased roadmap (data center validation, schema design, meta layer, API, frontend, addon) and detailed data extraction requirements from ESO.\[file:5]



\*\*Fit in ESO Build Engine (relative to Data Center)\*\*  

The Database Project is a downstream consumer of the Data Center: it explicitly begins only after the “data center” validation phase is complete and stable.\[file:4]\[file:5]\[file:23]  

Its canonical-layer and meta-layer ideas can inform future expansions of `data/` and `builds/`, but for now it should be treated as a future phase built on top of the current Data Center pipeline.\[file:4]\[file:5]\[file:23]



---



\### 6) ESO Build Engine – Data Center Tool Checklist.md



\*\*Purpose (2–3 sentences)\*\*  

Distills the Data Center scope into a status-tracked list of required software, JSON data files, and Python tools, tagged as \[DONE], \[PLANNED], or \[LATER].\[file:7]  

Enumerates filenames in `data/`, `builds/`, and `tools/`, and describes each tool’s purpose, inputs, and outputs.\[file:4]\[file:7]



\*\*Fit in ESO Build Engine (relative to Data Center)\*\*  

The checklist is a progress tracker and thin implementation layer for the Data Center plan, confirming which pieces of the scope are already implemented locally.\[file:4]\[file:7]\[file:23]  

As the Data Center spec evolves, this file must be updated in lockstep to keep the operational picture accurate (especially as tools move from PLANNED to DONE).\[file:4]\[file:7]\[file:23]



---



\### 7) ESO Build Engine – Copilot Bootstrap.md



\*\*Purpose (2–3 sentences)\*\*  

Tells AI assistants how to work in the repo: obey architecture rules, provide full-file outputs, prefer validators, and never rely on hidden state or external services.\[file:6]  

Restates the three-layer architecture and expected repository structure in a way tailored to AI tooling.\[file:6]\[file:24]



\*\*Fit in ESO Build Engine (relative to Data Center)\*\*  

The Bootstrap doc governs how AI may modify Data Center components (JSON, tools, backend, frontend), ensuring all work respects the Overview and Data Center scope.\[file:1]\[file:4]\[file:6]\[file:24]  

Any updates to the Data Center (new tools, new data files) should be reflected in this bootstrap so AI helpers stay aligned with the current structure.\[file:4]\[file:6]\[file:23]



---



\## 3. Why the Data Center scope must be first



\- It defines the repo skeleton and execution pipeline.  

&nbsp; The Data Center doc specifies the tree (`data/`, `builds/`, `tools/`, `backend/`, `frontend/`, `logs/`, `docs/`) and which minimal files must exist to call the system “operational.”\[file:4]\[file:23]



\- It is the prerequisite for downstream projects.  

&nbsp; The Build Database spec explicitly states its project begins only after the “data center” validation phase is complete and stable.\[file:4]\[file:5]\[file:23]



\- It connects control docs to real tools.  

&nbsp; Overview, Data Model, and Global Rules describe design and rules, but the Data Center scope translates them into concrete tools and workflows.\[file:1]\[file:2]\[file:3]\[file:4]



\- It defines success criteria and phases.  

&nbsp; The Data Center doc declares when the pipeline is “operational” for Phase 1 (test-dummy), Phase 2 (Permafrost Marshal), and Phase 3 (full functionality).\[file:4]



Because of these dependencies, no other document can be “complete” in practice until the Data Center scope is implemented well enough to run validators and exporters on real builds.\[file:4]\[file:23]



---



\## 4. Gaps, TODOs, and missing clarifications in the Data Center scope



These items were identified as needing clarification or tightening before downstream implementation.\[file:23]\[file:4]



\### Schema coupling to Data Model v1



\- The Data Center mentions “schema conformance” and TypeScript types but originally did not explicitly state that backend `types/` and Python validators must follow Data Model v1.\[file:2]\[file:4]\[file:23]  

\- Clarification: Data Center now explicitly calls Data Model v1 the schema source of truth; any schema changes must update that doc first, then code.\[file:2]\[file:4]



\### Backend vs Python authority for math and validation



\- Backend `lib/math.ts` is described as doing effect aggregation and pillar computation, while Python tools also own `aggregate\_effects.py` and `compute\_pillars.py`.\[file:3]\[file:4]\[file:23]  

\- Clarification needed: Python remains the single source for math/validation and backend either wraps Python outputs or shares JSON-configurable math; avoid duplicating ESO math in independent implementations.\[file:3]\[file:4]\[file:23]



\### How frontend writes builds safely



\- The Data Center describes frontend sending build JSON to backend, which writes `builds/\*.json` after validation.\[file:4]\[file:23]  

\- Clarify:

&nbsp; - Whether backend is allowed to modify repo files directly or only produce artifacts that the human later commits.

&nbsp; - How conflicts with local Git state are handled, given Git is the single source of truth.\[file:1]\[file:4]\[file:23]



\### Logs structure and retention



\- `logs/` and `logs/llm/` are mentioned but log naming, rotation, and commit policy are not fully defined.\[file:4]\[file:23]  

\- Clarify:

&nbsp; - Whether logs are always `.gitignore`d.

&nbsp; - Expected log format (JSON vs text) for validators and exporters.\[file:4]\[file:23]



\### Tool invocation API (CLI flags and conventions)



\- Example commands exist for `validate\_build.py`, but a single normative section for CLI interfaces across tools is missing.\[file:4]\[file:7]\[file:23]  

\- Clarify:

&nbsp; - Standard CLI interface and required flags for all tools (`validate\_build.py`, `export\_build\_md.py`, `aggregate\_effects.py`, `compute\_pillars.py`, `validate\_data\_integrity.py`) so scripts and CI can call them consistently.\[file:4]\[file:7]\[file:23]



\### “Test-dummy” build specification



\- `builds/test-dummy.json` is used as a pipeline smoke test but not fully specified.\[file:4]\[file:23]  

\- Clarify:

&nbsp; - A small, explicit spec for `test-dummy` (for example, at least one front bar skill, one set, one CP star, and required IDs), possibly via a dedicated `docs/test-dummy-spec.md` referenced by the Data Center.\[file:4]\[file:23]



\### Versioning strategy across docs and code



\- The Data Center mentions versioning via Git and phases but not how breaking changes in `data/` schemas or rules coordinate with backend types and validators.\[file:4]\[file:23]  

\- Clarify:

&nbsp; - How schema changes are proposed (update docs first vs code first).

&nbsp; - Whether any schema version fields appear in JSON or docs.\[file:2]\[file:4]\[file:23]



Addressing these clarifications in the Data Center scope keeps Python tools, backend TypeScript, and control docs in sync as the project grows.\[file:4]\[file:23]



---



\## 5. Ordered work plan (Data Center first, aligned with repo structure)



Below is the work plan captured in the initial thread, structured by phases and aligned to `The-Elder-Elemental/` layout.\[file:23]\[file:4]



\### Phase A – Finalize and lock the Data Center scope



\- Resolve clarifications in `docs/ESO-Build-Engine-Data-Center-Scope.md`:

&nbsp; - Declare Python tools as math/validation authority or define shared config with backend.

&nbsp; - Tie backend TS types and validators explicitly to Data Model v1.

&nbsp; - Define standard CLI flags for core tools.

&nbsp; - Clarify logging policy for `logs/` and `logs/llm/`.\[file:2]\[file:3]\[file:4]\[file:23]

\- Align Copilot Bootstrap to match Data Center structure and tool list.

\- Ensure the Data Center Tool Checklist mirrors the scope (tools and data).\[file:4]\[file:6]\[file:7]\[file:23]



\### Phase B – Implement Data Center Phase 1 (test-dummy pipeline)



\- Implement minimal data JSONs consistent with Data Model v1:

&nbsp; - `data/skills.json`, `data/effects.json`, `data/sets.json`, `data/cp-stars.json` with at least one test entry each.\[file:2]\[file:4]\[file:7]

\- Create `builds/test-dummy.json` as a structurally valid build per Global Rules.\[file:3]\[file:4]\[file:7]

\- Run:

&nbsp; - `python tools/validate\_build\_test.py`

&nbsp; - `python tools/export\_build\_test\_md.py`

&nbsp; - Confirm `builds/test-dummy.md` is generated and valid.\[file:4]\[file:7]\[file:23]



\### Phase C – Implement Data Center Phase 2 (Permafrost Marshal build)



\- Populate real data for Permafrost Marshal in `data/\*.json` following Data Model v1.\[file:2]\[file:4]

\- Author `builds/permafrost-marshal.json` using IDs and numeric configs, respecting Global Rules.\[file:2]\[file:3]\[file:4]

\- Implement or refine Phase 2 tools:

&nbsp; - `tools/validate\_build.py`

&nbsp; - `tools/export\_build\_md.py`

&nbsp; - `tools/aggregate\_effects.py`

&nbsp; - `tools/compute\_pillars.py`

&nbsp; - `tools/validate\_data\_integrity.py`\[file:3]\[file:4]\[file:7]\[file:23]

\- Update Tool Checklist statuses from \[PLANNED] to \[DONE] as tools are implemented.\[file:7]\[file:23]



\### Phase D – Backend and frontend wiring



\- Implement backend skeleton (`backend/`) to load JSON, validate builds, and expose data/build endpoints per Data Center scope.\[file:4]\[file:23]

\- Implement frontend skeleton (`frontend/`) with selector-only UI, reading from backend and never duplicating core ESO data.\[file:1]\[file:4]\[file:23]

\- Verify Phase 2 success criteria from Data Center:

&nbsp; - Validators and exporters pass.

&nbsp; - Permafrost Marshal loads via backend and displays correctly in frontend.\[file:4]\[file:23]



\### Phase E – Refine control docs and expand toward ESO Build Database



\- Reconcile Global Rules and Data Model v1 with actual tool behavior; update docs first when discrepancies appear.\[file:2]\[file:3]\[file:23]

\- Refresh Overview and Copilot Bootstrap to reflect any implementation-driven constraints or adjustments.\[file:1]\[file:6]\[file:23]

\- Once Data Center meets Phase 3 criteria, use ESO Build Database Project Specification to design gradual expansion to a canonical DB and richer API.\[file:4]\[file:5]\[file:23]



This document is a snapshot of that initial planning and alignment; newer docs now encode the refined decisions directly.\[file:1]\[file:2]\[file:3]\[file:4]\[file:6]\[file:7]



