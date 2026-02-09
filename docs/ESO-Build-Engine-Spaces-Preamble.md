# ESO Build Engine – Spaces Preamble (Reusable Control Snippet)

> PURPOSE  
> This snippet defines how AI assistants must behave when working on the **ESO Build Engine – Permafrost Marshal** project, across any Perplexity Spaces thread.

## Project and repo ground rules

- The Git repo **The-Elder-Elemental** is the single source of truth.
- All ESO data lives in `data/*.json`.
- All builds live in `builds/*.json`.
- All validation, effect math, and pillar checks live in `tools/*.py`.
- The backend (`backend/`) and frontend (`frontend/`) read JSON from `data/` and `builds/` and must not invent their own rules.
- Markdown build grids are generated views only; never edited by hand.

## Author and expectations

- The human owner is a technical systems engineer (not a full-time coder).
- AI assistance must:
  - Produce clear, explicit, full-file outputs ready to paste into the repo.
  - Avoid partial edits (“insert X above Y”); always give complete file contents.
  - Prefer adding/updating Python tools in `tools/` over ad-hoc scripts.

## Canonical control documents (docs/)

AI must treat these as authoritative:

- `docs/ESO-Build-Engine-Overview.md`
- `docs/ESO-Build-Engine-Data-Model-v1.md`
- `docs/ESO-Build-Engine-Global-Rules.md`
- `docs/ESO-Build-Engine-Data-Center-Scope.md`
- `docs/ESO Build Database Project Specification.md` (future / downstream)
- `docs/ESO Build Engine – Data Center Tool Checklist.md`
- `docs/ESO Build Engine – Copilot Bootstrap.md`

If code and docs disagree, **the docs win** until we explicitly update them.

## Architecture that must always be respected

- `data/*.json`  
  Canonical ESO data (skills, effects, sets, CP, etc.).

- `builds/*.json`  
  Build records that only reference IDs and numeric configuration.

- `tools/*.py`  
  Python validators, exporters, effect aggregation, pillar checks, and support tools.

- `backend/`  
  Node/Express/TypeScript API that reads JSON from `data/` and `builds/`.

- `frontend/`  
  React/Vite UI with selector-only inputs; no free-text editing of core entities.

- `docs/`  
  Control documents that define rules, structure, and workflows (including this preamble).

## AI behavior requirements

When responding in this Space, AI assistants must:

1. Align with the v1 Data Model for all skills/effects/sets/CP/builds JSON.
2. Treat `builds/permafrost-marshal.json` as the canonical Permafrost Marshal build, following the v1 model.
3. Prefer:
   - Adding/updating Python tools in `tools/` over throwaway scripts.
   - Updating docs when making structural or rule changes.
4. When proposing code or data:
   - Specify exact file paths.
   - Provide full final file content.
   - Include example commands to run validators/tools (e.g., `python tools/validate_build.py`).
5. When adding new data or formats:
   - Also propose or update validators and tests under `tools/`.

## How to use this snippet

- Paste this preamble at the top of any new Perplexity Spaces thread for this project.
- Then add any thread-specific context (e.g., “Today we are working on X tool”).
- The AI must treat this preamble as binding for that thread.
