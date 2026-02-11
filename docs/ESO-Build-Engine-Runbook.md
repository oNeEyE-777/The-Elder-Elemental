# ESO Build Engine Runbook

## Intro

This runbook explains how to run the ESO Build Engine locally, including the backend API server and the React/Vite frontend UI. It focuses on starting services, verifying health checks, and confirming that the Permafrost Marshal build flows correctly from JSON through the API into the UI, without covering how to edit the underlying JSON data.

## Prerequisites

- Git installed and available on your PATH.
- Node.js (LTS version) and npm installed (Node 18.x is recommended for this project).
- VS Code (or a similar editor) installed for working with the repo.
- Local clone path for examples in this runbook:  
  `C:\Projects\The-Elder-Elemental`.

## Backend: API server

The backend API server lives under `backend/` in the repo and exposes REST endpoints that read from `data/*.json` and `builds/*.json` without modifying them.

To start the backend dev server, open a PowerShell terminal and run:

```powershell
cd C:\Projects\The-Elder-Elemental\backend
npm install
npm run dev
```

When the backend is running correctly, you should see ts-node-dev (or a similar TypeScript dev runner) start up and log that it is listening on `http://localhost:3001`. The console output typically includes a compiled successfully message, a watcher notice, and a line indicating the port, for example: `Server listening on http://localhost:3001`.

### Backend health endpoint

The backend exposes a simple health check you can use to confirm the service is up:

- Method and URL:  
  `GET http://localhost:3001/api/health`.
- Expected JSON response:

```json
{
  "status": "ok",
  "service": "eso-build-engine-backend"
}
```

If you see this response in a browser or tool like curl/Postman, the backend API server is running and reachable locally.

### Permafrost Marshal build endpoint

The backend also exposes the Permafrost Marshal build via a dedicated endpoint that reads from `builds/permafrost-marshal.json`.

- Method and URL:  
  `GET http://localhost:3001/api/builds/permafrost-marshal`.

The JSON response represents the Permafrost Marshal PvP tank build as defined in the v1 Data Model and associated build file. Key fields you should expect to see include:

- `id`: `"permafrost-marshal"` — the stable build identifier.
- `name`: `"Permafrost Marshal"` — human-readable build name.
- `classcore`: an object describing the primary class, typically Warden, with ESO-agnostic fields following the v1 Data Model.
- `subclasses`: a list including Necromancer and Dragonknight, reflecting the flex skills incorporated into the build.
- `roletags`: tags indicating that this is a PvP high-speed tank build (for example, values like `"tank"`, `"pvp"`, `"high-speed"`).
- `cptotal`: the total Champion Points budgeted for the build (for Permafrost Marshal, this is configured around a high CP total consistent with a late-game PvP tank).
- `attributes`: numeric allocations for Health, Magicka, and Stamina, with health-biased distribution appropriate for a tank.
- `pillars.*`: nested fields summarizing pillar targets and evaluations, including:
  - Resist target and actual resist values for achieving high effective resistance.
  - Speed profile indicating the build’s movement speed focus (e.g., leveraging Adept Rider and Ring of the Wild Hunt).
  - Health focus capturing whether the build meets or exceeds its health pillar goals.

These fields are read-only from the perspective of the API; all game rules and math are driven by JSON and Python tools, not by hand-edited backend code.

## Frontend: React/Vite UI

The frontend application lives under `frontend/` and is implemented as a React + Vite + TypeScript UI. It is **read-only** for core game entities and uses selector-style inputs only; users select skills, sets, and CP stars by ID, and the UI never allows free-text editing of canonical data such as tooltips or effect math.

To start the frontend dev server, open a second PowerShell terminal and run:

```powershell
cd C:\Projects\The-Elder-Elemental\frontend
npm install
npm run dev
```

Vite will start a dev server listening on `http://localhost:5173` and will proxy requests matching `/api/*` to `http://localhost:3001`, which is where the backend runs. When the server starts, you should see a Vite banner similar to:

- `VITE v6.x.x  ready in X ms`
- `Local:  http://localhost:5173/`
- A notice that it is watching files for HMR (hot module replacement).

This indicates that the frontend is ready and is wired to forward API calls to the backend.

## Running backend and frontend together

To run the full ESO Build Engine stack locally (backend + frontend), follow these steps in order:

1. **Start the backend API server (terminal 1)**  
   - In the first PowerShell window:

     ```powershell
     cd C:\Projects\The-Elder-Elemental\backend
     npm install
     npm run dev
     ```

   - Wait until the server logs that it is listening on `http://localhost:3001` and the health endpoint responds with status `ok`.

2. **Start the frontend dev server (terminal 2)**  
   - In a second PowerShell window:

     ```powershell
     cd C:\Projects\The-Elder-Elemental\frontend
     npm install
     npm run dev
     ```

   - Confirm that Vite reports a local URL at `http://localhost:5173` and that it is ready.

3. **Open the UI in a browser**  
   - Navigate to `http://localhost:5173` in your browser.

When everything is working correctly, the UI should show:

- Page title in the browser:  
  `The Elder Elemental – ESO Build Engine UI`.
- A backend health section that calls `GET /api/health` and displays a status of `ok`, reflecting `{ "status": "ok", "service": "eso-build-engine-backend" }`.
- A Permafrost Marshal section that:
  - Shows the build name `Permafrost Marshal`.
  - Lists role tags such as tank/PvP/high-speed.
  - Displays the configured CP total for the build.
  - Shows attribute allocations (Health, Magicka, Stamina) consistent with a high-health tank setup.
  - Provides a pillar summary including:
    - Resist target vs. actual resist (indicating whether the build is on track for its defensive goals).
    - Speed profile based on the active speed effects and sets.
    - Health focus, confirming whether the build meets its health pillar target.

The UI reads all of this via the backend API; it does not directly manipulate `data/*.json` or `builds/*.json` files.

## Troubleshooting

### Frontend loads, API calls fail (500 or 404)

If the UI loads at `http://localhost:5173` but API calls return HTTP 500 or 404:

- Confirm the backend server is running in the first terminal and still listening on `http://localhost:3001` (no crash or exit).
- Double-check that you started the backend from `C:\Projects\The-Elder-Elemental\backend` and not from another folder.
- Look at the backend terminal for stack traces or error logs; schema or JSON loading errors can cause 500 responses.
- Verify that the requested endpoint exists, for example:
  - `GET /api/health`
  - `GET /api/builds/permafrost-marshal`.

### Frontend cannot reach backend (network error)

If the frontend shows network errors (e.g., `Failed to fetch` or CORS/proxy errors):

- Ensure both servers are running:
  - Backend: `npm run dev` in `backend/` with port 3001.
  - Frontend: `npm run dev` in `frontend/` with port 5173.
- Check that `frontend/vite.config.ts` is configured to proxy `/api` to `http://localhost:3001` (as required by the Data Center scope).
- Refresh the page and watch the browser dev tools console and Network tab for failing requests to `/api/health` or `/api/builds/permafrost-marshal`.
- If you changed ports, update the proxy target in `vite.config.ts` to match the actual backend port.

### Ports already in use

If `npm run dev` reports that port 3001 or 5173 is already in use:

- Close any previous dev server terminals still running the backend or frontend and retry the command.
- Check for other processes using those ports (browser dev tools, another Node process) and stop them before starting the servers again.
- As a last resort, adjust the configured ports:
  - For the backend, change the listen port in `backend/src/index.ts` and update any references.
  - For the frontend, change the dev server port in `frontend/vite.config.ts` and ensure the proxy target reflects the backend port.

## Git workflow notes

The ESO Build Engine repo is strictly data-driven with Git as the single source of truth. Keep these rules in mind when working with the project:

- All ESO game data lives in `data/*.json` (skills, effects, sets, CP stars, and future expansion files).
- All builds live in `builds/*.json`, including `builds/permafrost-marshal.json` for the Permafrost Marshal build.
- The backend and frontend **read** JSON from `data/` and `builds/`; they do not write or mutate these canonical files at runtime.
- Markdown build grids such as `permafrost-marshal.md` are generated by Python tools and must **not** be hand-edited.

A basic Git workflow from the repo root looks like this:

```powershell
cd C:\Projects\The-Elder-Elemental
git status
git add <files>
git commit -m "Your message here"
git push
```

Always ensure validators and exports pass before committing changes to data or builds, and treat generated Markdown as outputs, not as sources of truth.
