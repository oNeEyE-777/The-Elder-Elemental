1. Attached project documents (by filename, in priority order)
ESO-Build-Engine-Data-Center-Scope.md
​

ESO-Build-Engine-Overview.md
​

ESO-Build-Engine-Data-Model-v1.md
​

ESO-Build-Engine-Global-Rules.md
​

ESO Build Database Project Specification.md
​

ESO Build Engine – Data Center Tool Checklist.md
​

ESO Build Engine – Copilot Bootstrap.md
​

The rest of this answer follows that priority, with the Data Center scope treated as the active focus.

2. Purpose and role of each document (relative to Data Center)
1) ESO-Build-Engine-Data-Center-Scope.md (current focus) [highest priority]
Purpose (2–3 sentences)
This document defines the complete data center for the ESO Build Engine: repo structure, data storage, Python tools, backend API, frontend, testing, deployment, and maintenance workflows. It describes what must exist in data/, builds/, tools/, backend/, frontend/, logs/, and docs/, and sets success criteria for the pipeline from test-dummy to Permafrost Marshal.
​

Fit in ESO Build Engine
The Data Center scope is the operational contract between architecture ideas and real running code, describing how JSON, validators, API, and UI actually interact as a system. All other docs (overview, data model, global rules, database spec) either feed into it (what to implement) or sit on top of it (what to build once the data center is stable).

2) ESO-Build-Engine-Overview.md
Purpose (2–3 sentences)
This document defines what the ESO Build Engine is and lays out non‑negotiable rules for architecture, data/logic separation, AI usage, and Git as the single source of truth. It explains the three-layer design (JSON data, Python logic, selector-only UI) and explicitly states that Markdown build grids are generated views, never sources of truth.
​

Fit in ESO Build Engine (relative to Data Center)
The Overview defines the constraints the Data Center scope must obey: JSON in data/ and builds/, tools in tools/, no external runtime dependencies, and selector-only frontends. The Data Center doc operationalizes this by specifying concrete files, tools, and workflows that implement those non‑negotiables.

3) ESO-Build-Engine-Data-Model-v1.md
Purpose (2–3 sentences)
This document defines the minimal JSON schemas for v1: data/skills.json, data/effects.json, data/sets.json, data/cp-stars.json, and builds/permafrost-marshal.json. It includes detailed example objects and key principles (IDs not free text, centralized effects, scalable shapes) for the Permafrost Marshal build.
​

Fit in ESO Build Engine (relative to Data Center)
The v1 Data Model is the schema contract that the Data Center must enforce through validators, backend types, and frontend typing. The Data Center scope refers to “schema conformance” and TypeScript types; those derive directly from this document and must be kept in sync.

4) ESO-Build-Engine-Global-Rules.md
Purpose (2–3 sentences)
This document defines structural rules (bars, gear, CP layout), set/CP constraints, and effect stacking logic, plus Python function contracts for validators and helpers. It specifies expected behaviors and signatures for validate_build_structure, aggregate_effects, validate_effect_stack_rules, and create_empty_build_template.
​

Fit in ESO Build Engine (relative to Data Center)
Global Rules describe what Python validators and effect math must do, while the Data Center scope describes where those tools live and how they’re run (tools/*.py, logs, CLI usage). The Data Center’s tools list (validate_build.py, aggregate_effects.py, compute_pillars.py) must be implemented to satisfy the contracts in Global Rules.

5) ESO Build Database Project Specification.md
Purpose (2–3 sentences)
This spec describes a larger ESO build database project: canonical ESO data keyed by official IDs, meta-layer tables for builds/rotations/gear, an API layer, frontend, and potential addon. It lays out a phased roadmap (data center validation, schema design, meta layer, API, frontend, addon) and detailed data extraction requirements from ESO.
​

Fit in ESO Build Engine (relative to Data Center)
The Database Project is a downstream consumer of the Data Center: it explicitly starts “after the data center validation phase is complete and proven stable.” Its canonical-layer and meta-layer ideas can inform future expansions of data/ and builds/, but for now it should be treated as a future phase built on top of the current Data Center pipeline.

6) ESO Build Engine – Data Center Tool Checklist.md
Purpose (2–3 sentences)
This checklist distills the Data Center scope into a status-tracked list of required software, JSON data files, and Python tools, tagged as [DONE], [PLANNED], or [LATER]. It enumerates actual filenames in data/, builds/, and tools/, and describes each tool’s purpose, inputs, and outputs.
​

Fit in ESO Build Engine (relative to Data Center)
The checklist is a progress tracker and thin implementation layer for the Data Center plan, confirming which pieces of the scope are already implemented locally. As the Data Center spec evolves, this file must be updated in lockstep to keep the operational picture accurate (especially as tools move from PLANNED to DONE).

7) ESO Build Engine – Copilot Bootstrap.md
Purpose (2–3 sentences)
This document tells AI assistants how to work in the repo: obey architecture rules, provide full-file outputs, prefer validators, and never rely on hidden state or external services. It restates the three-layer architecture and expected repository structure in a way tailored to AI tooling.
​

Fit in ESO Build Engine (relative to Data Center)
The Bootstrap doc governs how AI may modify Data Center components (JSON, tools, backend, frontend), ensuring all work respects the Overview and Data Center scope. Any updates to the Data Center (new tools, new data files) should be reflected in this bootstrap so AI helpers stay aligned with the current structure.

3. Why the Data Center scope must be first
It defines the repo skeleton and execution pipeline.
The Data Center doc specifies the top-level tree (data/, builds/, tools/, backend/, frontend/, logs/, docs/) and exactly which minimal files must exist to call the system “operational.” Without this skeleton, the Data Model, Global Rules, and Overview are not wired into runnable code paths.
​

It is the prerequisite for downstream projects.
The Build Database spec explicitly states its project begins only after the “data center” validation phase is complete and stable. That dependency means the Data Center is the critical path before any broader database, API, or addon work is meaningful.
​

It connects control docs to real tools.
Overview, Data Model, and Global Rules describe design and rules, but the Data Center scope translates them into concrete tools (validate_build*_test.py, validate_build.py, aggregate_effects.py, compute_pillars.py) and CI-like workflows. Implementing other docs without the Data Center’s execution plan risks drift and partial, unvalidated features.

It defines success criteria and phases.
The Data Center doc declares when the pipeline is “operational” in Phase 1 (test-dummy), Phase 2 (Permafrost Marshal), and Phase 3 (full functionality). These milestones are essential to sequencing the rest of the work and avoiding premature expansion into the full database or addon.
​

Because of these dependencies, no other document can be “complete” in practice until the Data Center scope is implemented well enough to run validators and exporters on real builds.

4. Gaps, TODOs, and missing clarifications in the Data Center scope
Here are key items in the Data Center scope that need clarification or tightening before downstream implementation:

Schema coupling to Data Model v1

The Data Center mentions “schema conformance” and TypeScript types but does not explicitly state that backend types/ and Python validators are generated from, or strictly aligned to, the v1 Data Model schemas.

Clarify: whether schemas will be hand-maintained in TS and Python or derived from a single JSON-schema-like source (and where that lives under docs/ or data/).

Backend vs Python authority for math and validation

The backend lib/math.ts is described as doing effect aggregation and pillar computation, while Python tools also own aggregate_effects.py and compute_pillars.py.

Clarify: whether Python remains the single source for math/validation and the backend simply calls Python outputs, or whether math is duplicated in TS (which would violate “no duplicate ESO math” unless carefully managed).

How frontend writes builds safely

The Data Center describes a workflow where the frontend sends build JSON to the backend, which writes to builds/*.json after validation.
​

Clarify:

Is the backend allowed to modify files directly in the repo, or does it only emit artifacts that the human later commits?

How conflicts with local Git state are handled (since Overview insists Git is the single source of truth and all I/O is local).

Logs structure and retention

The doc mentions logs/ and logs/llm/ but doesn’t define log file naming, rotation, or whether logs are committed.
​

Clarify:

Are logs always .gitignored?

Expected log format (JSON vs text) for validators and exporters.

Tool invocation API (CLI flags and conventions)

Example commands are given for validate_build.py but the argument patterns (e.g., --build) are not fully specified in a single normative section.
​

Clarify: standard CLI interface and required flags for all tools (validate_build.py, export_build_md.py, aggregate_effects.py, compute_pillars.py, validate_data_integrity.py) so scripts and CI can call them consistently.
​

“Test-dummy” build specification

The doc relies on builds/test-dummy.json as a pipeline smoke test but doesn’t normatively define its required content beyond “references test data IDs.”
​

Clarify: a small, explicit spec for test-dummy (e.g., at least one front bar skill, at least one set, one CP star, and which specific IDs must appear), possibly in the Data Model or a small docs/test-dummy-spec.md referenced by the Data Center.

Versioning strategy across docs and code

The Data Center mentions versioning via Git and phases, but not how breaking changes in data/ schemas or rules will be coordinated with backend types and validators.
​

Clarify:

How schema changes are proposed (update docs first vs code first).

Whether any semantic versioning or “schema version” fields will be included in JSON or docs.

Addressing these clarifications in the Data Center scope will prevent divergence between Python tools, backend TS, and the control docs as the project grows.

5. Ordered work plan (Data Center first, aligned with repo structure)
Below is a concrete, step‑by‑step plan that prioritizes the Data Center scope, then the other docs, always referencing how they depend on the Data Center. Paths assume the repo root The-Elder-Elemental/ and docs/ as described.
​

Phase A – Finalize and lock the Data Center scope (docs/ESO-Build-Engine-Data-Center-Scope.md)
Resolve Data Center clarifications (edit doc)

Update docs/ESO-Build-Engine-Data-Center-Scope.md to:

Declare that Python tools are the single source of truth for math and validation, and backend math.ts either wraps Python outputs or uses shared JSON-configurable math (no divergence).

Specify the canonical place for schemas (Data Model v1) and how backend TS types and Python validators must follow it.

Define standard CLI flags and usage for all tools (including --build and default locations).
​

Clarify logging policy for logs/ and logs/llm/ (format and .gitignore expectations).
​

Save the full updated doc under docs/ESO-Build-Engine-Data-Center-Scope.md.

Align Data Center with Copilot Bootstrap

Ensure docs/ESO Build Engine – Copilot Bootstrap.md reflects the same repository tree and tool list described in the Data Center scope, especially for tools/ and builds/.

If any paths differ, update both docs in the same commit (full-file edits).

Confirm Data Center Tool Checklist matches the scope

Review docs/ESO Build Engine – Data Center Tool Checklist.md and add any tools or data files that appear in the updated scope but not in the checklist (or mark removed items as obsolete).

This yields a consistent high-level plan (scope doc) and operational status view (checklist).

Phase B – Implement Data Center Phase 1 (test-dummy pipeline)
Implement minimal data JSONs consistent with Data Model v1

Use docs/ESO-Build-Engine-Data-Model-v1.md to create or verify:

data/skills.json with at least one test skill following the schema.
​

data/effects.json with at least one test effect.
​

data/sets.json with at least one test set.
​

data/cp-stars.json with at least one test CP star.
​

Treat these as test-only entries that can later be expanded for Permafrost Marshal.

Create builds/test-dummy.json and MD export

Define builds/test-dummy.json as a structurally valid build JSON, satisfying Global Rules (bars, gear, CP) but using test IDs from the minimal data JSONs.

Run python tools/validate_build_test.py and python tools/export_build_test_md.py to generate builds/test-dummy.md, ensuring the Phase 1 success criteria in the Data Center doc are met.

Wire logs and execution examples

Confirm validators and exporters log execution into logs/ according to the clarified logging conventions.
​

Update the Data Center doc if needed with the exact example commands you use (e.g., python tools/validate_build_test.py from repo root).

Phase C – Implement Data Center Phase 2 (Permafrost Marshal build)
Populate real data for Permafrost Marshal

Expand data/skills.json, data/effects.json, data/sets.json, and data/cp-stars.json to include all entries required for Permafrost Marshal as per Data Model v1.

Ensure each new effect respects Global Rules semantics (Major/Minor, stacking) in data/effects.json.
​

Create builds/permafrost-marshal.json aligned to Global Rules

Author builds/permafrost-marshal.json using only IDs and numeric configs, matching the example structure in Data Model v1.
​

Validate it structurally against Global Rules using tools/validate_build.py (once implemented).

Implement Phase 2 tools per Data Center scope

Implement or refine:

tools/validate_build.py using contracts from Global Rules.

tools/export_build_md.py to generate builds/permafrost-marshal.md as a pure view.
​

tools/aggregate_effects.py and tools/compute_pillars.py, aligning behaviors to the functions described in Global Rules.

tools/validate_data_integrity.py for ID uniqueness and reference sanity across data/*.json.

Update the Tool Checklist statuses (PLANNED → DONE) as each one is implemented.
​

Phase D – Backend and frontend wiring to the Data Center
Implement backend skeleton using Data Center scope

Create backend/ with src/index.ts, routes/data.ts, routes/builds.ts, lib/loader.ts, lib/validator.ts, lib/math.ts, and types/index.ts as described.
​

Ensure loader reads from data/ and builds/, validator lib mirrors Python validate_build.py behavior (or delegates to Python outputs), and types align with Data Model v1.

Implement frontend skeleton with selector-only UI

Create frontend/ structure per Data Center doc, including App.tsx, BuildEditor.tsx, SkillSelector.tsx, GearSlot.tsx, CPSelector.tsx, EffectDisplay.tsx and shared lib/types.ts.
​

Ensure UI only uses selectors backed by global JSON via the backend API and never allows free-text editing of core entities, respecting the Overview doc.

Verify Phase 2 success criteria

Use the commands defined in the Data Center doc to verify:

Validators pass, exporters generate accurate Markdown, Permafrost Marshal loads via the backend and displays correctly in the frontend editor.
​

Update the Data Center scope’s success-criteria section with any necessary corrections discovered in implementation.

Phase E – Refine control docs and then expand toward the full database
Tighten Global Rules and Data Model against actual tools

After tools and backend are working, reconcile docs/ESO-Build-Engine-Global-Rules.md and docs/ESO-Build-Engine-Data-Model-v1.md with the implemented behavior: where there’s mismatch, update the docs first or adjust code accordingly.

Add any missing edge cases found during Permafrost Marshal implementation (e.g., specific stacking exceptions) into data/effects.json and Global Rules text.
​

Refine Overview and Copilot Bootstrap

Update docs/ESO-Build-Engine-Overview.md if implementation revealed any practical constraints (e.g., how external IDs are used in practice).
​

Refresh docs/ESO Build Engine – Copilot Bootstrap.md so AI helpers fully reflect the current set of tools and patterns (especially new validators or pipeline scripts you add).
​

Plan transition into ESO Build Database project

Once the Data Center passes Phase 3 success criteria, use ESO Build Database Project Specification.md to design a gradual expansion from JSON-based data center to a canonical database and richer API.

Keep the Data Center scope as the base layer; treat database work as an upper layer, ensuring no duplication of core logic and respecting the “data center validation first” requirement.
​

This plan keeps the Data Center scope as the active focus and ensures every other document is implemented or updated as a consumer or constraint of that central definition.