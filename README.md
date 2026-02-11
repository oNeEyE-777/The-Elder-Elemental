# The Elder Elemental – ESO Build Engine

This repository implements the ESO Build Engine for the **Permafrost Marshal** build, using a strict data-first architecture: all core ESO data lives in `data/`, builds live in `builds/`, Python tools in `tools/`, and a TypeScript/Node backend in `backend/` that exposes read-only APIs over the JSON data.

## Repo layout (high level)

- `data/` – Canonical ESO data JSON: skills, effects, sets, CP stars, etc.
- `builds/` – Build JSON definitions that only reference IDs and numeric config (e.g. `permafrost-marshal.json`).
- `tools/` – Python validators, exporters, and analyzers (no game logic hidden elsewhere).
- `backend/` – Node + TypeScript API that reads from `data/` and `builds/` and serves read-only views for the UI.
- `docs/` – Control documents that define rules and structure (non-negotiable source of truth for behavior).

Git is the single source of truth; Markdown build grids and UI outputs are generated views only and are never edited by hand.

## Backend (Node + TypeScript)

The backend lives in `backend/` and exposes read-only JSON APIs for the ESO Build Engine data and the Permafrost Marshal build.

### Prerequisites

- Node.js and npm installed on your machine.

### First-time backend setup

From the repo root:

```bash
cd backend
npm install
```

This installs backend dependencies into `backend/node_modules` using the pinned versions from `backend/package-lock.json`, ensuring deterministic installs across machines.

### Backend scripts

All commands below are run from the `backend/` directory.

- `npm run dev` – Start the TypeScript development server with automatic restart on code changes.
- `npm run build` – Compile the backend TypeScript to JavaScript into `dist/` using `tsc`.
- `npm start` – Run the compiled backend from `dist/index.js` (after `npm run build`).
- `npm run typecheck` – Run TypeScript’s `tsc --noEmit` to check for type errors without generating output files.

The development workflow is:

```bash
cd backend
npm install       # first time or when dependencies change
npm run dev       # day-to-day development
```

For a production-style run:

```bash
cd backend
npm install
npm run build
npm start
```

### Backend behavior (summary)

The backend is a read-only API; it does not mutate JSON files and does not maintain its own database. It reads from the JSON data under `data/` and `builds/` and exposes endpoints that the frontend can use to:

- List available ESO data entities (skills, sets, effects, CP stars).
- Retrieve specific builds (starting with `permafrost-marshal`) by ID.
- Provide health/status endpoints for tooling and UI integration.

All logic and math remain in JSON/Python tools; the backend is a thin, typed access layer that respects the global rules and v1 data model.


Next commands (from repo root):

```powershell
# overwrite or create README.md with this content
# (paste the block above into README.md via VS Code)

git add README.md
git commit -m "Add unified README for ESO Build Engine and backend workflow"
git push origin main

