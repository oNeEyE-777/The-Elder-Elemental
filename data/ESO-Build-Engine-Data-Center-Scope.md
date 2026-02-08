# ESO Build Engine – Data Center Scope & Implementation Plan **docs/ESO-Build-Engine-Data-Center-Scope.md**

## Purpose

Define the complete “data center” infrastructure needed to support the ESO Build Engine: tools, services, configuration, testing, validation, and deployment components that make the system operational.​

This document covers:

* Local development environment
* Data storage and management
* Automation tools (Python scripts)
* Backend API service
* Frontend application
* Testing and validation framework
* Deployment and hosting
* Monitoring and maintenance

## 1. Local Development Environment

**Required software**

* Git – Version control for the entire repo
* Python 3.10+ – Automation scripts and validators
* Node.js 18+ – Backend API and frontend build tooling
* VS Code (or preferred editor) – Primary editing environment
* LM Studio (optional, later) – Local LLM for AI‑assisted tasks

**Repository structure**

text

The-Elder-Elemental/

├── data/ # Global JSON "database"

│ ├── skills.json

│ ├── effects.json

│ ├── sets.json

│ ├── cp-stars.json

│ ├── mundus.json # (future)

│ ├── food.json # (future)

│ └── enchants.json # (future)

├── builds/ # Build records

│ ├── test-dummy.json # Test build for pipeline validation

│ ├── test-dummy.md # Generated MD export (test)

│ ├── permafrost-marshal.json # Real build (after test passes)

│ └── permafrost-marshal.md # Generated MD export (real)

├── tools/ # Python automation scripts

│ ├── validate\_build\_test.py # Test validator

│ ├── export\_build\_test\_md.py # Test MD exporter

│ ├── validate\_build.py # Real validator (after test)

│ ├── export\_build\_md.py # Real MD exporter (after test)

│ ├── aggregate\_effects.py # Buff/debuff aggregation logic

│ ├── compute\_pillars.py # Pillar validation (resist/speed/etc.)

│ ├── validate\_data\_integrity.py# Data integrity checks

│ └── llm\_helper.py # (optional) LM Studio integration

├── backend/ # Node.js/Express API

│ ├── src/

│ │ ├── index.ts # Main server entry

│ │ ├── routes/

│ │ │ ├── data.ts # /api/data/\* endpoints

│ │ │ └── builds.ts # /api/builds/\* endpoints

│ │ ├── lib/

│ │ │ ├── loader.ts # JSON file loading

│ │ │ ├── validator.ts # Build validation logic

│ │ │ └── math.ts # Effect aggregation and pillar computation

│ │ └── types/

│ │ └── index.ts # TypeScript types for data schemas

│ ├── package.json

│ └── tsconfig.json

├── frontend/ # React/Vite UI

│ ├── src/

│ │ ├── App.tsx # Main app component

│ │ ├── components/

│ │ │ ├── BuildEditor.tsx # Main build editing UI

│ │ │ ├── SkillSelector.tsx # Skill selection dropdown/search

│ │ │ ├── GearSlot.tsx # Gear slot editor

│ │ │ ├── CPSelector.tsx # CP star selection

│ │ │ └── EffectDisplay.tsx # Buff/debuff display

│ │ ├── lib/

│ │ │ ├── api.ts # API client for backend

│ │ │ └── types.ts # TypeScript types (shared with backend)

│ │ └── main.tsx

│ ├── package.json

│ ├── tsconfig.json

│ └── vite.config.ts

├── logs/ # Tool execution logs

│ └── llm/ # LLM interaction logs (if used)

├── docs/ # Control documentation

│ ├── ESO-Build-Engine-Overview.md

│ ├── ESO-Build-Engine-Data-Model-v1.md

│ ├── ESO-Build-Engine-Global-Rules.md

│ └── ESO-Build-Engine-Data-Center-Scope.md

├── .gitignore

├── README.md

└── package.json # (optional) root workspace config

## 2. Data Storage & Management

**Data layer principles**

* Single source of truth: All ESO game data lives in data/\*.json.
* Normalized records: Skills, effects, sets, CP stored once with unique IDs.
* Build records reference IDs only: no duplicated text or math in build files.
* Versioning via Git: All data changes tracked in version control.
* No external dependencies at runtime: no reliance on third‑party APIs or databases.​

**Data file responsibilities**

| File | Contains | Used by |
| --- | --- | --- |
| data/skills.json | Skills with metadata, costs, durations, effect IDs | Frontend selectors, validators, MD exporter |
| data/effects.json | Buffs/debuffs with math (types, values, stacking) | Effect aggregation, pillars, tooltip display |
| data/sets.json | Sets with bonuses per piece count | Gear selectors, set bonus calculation |
| data/cp-stars.json | CP stars with tree, type, effects | CP selectors, effect aggregation |
| builds/\*.json | Individual build records (IDs + config only) | All tools, backend, frontend |

**Data integrity requirements**

* Valid JSON syntax: all data files must parse without errors.
* Unique IDs: no duplicate IDs within a data file.
* Valid references: all effect IDs referenced in skills/sets/CP must exist in effects.json.
* Schema conformance: all records match the schemas defined in the Data Model doc.​

## 3. Automation Tools (Python Scripts)

**Core tool categories**

* Validation tools – Check data integrity and build correctness
* Export tools – Generate derived outputs (Markdown, reports)
* Computation tools – Aggregate effects, compute pillars, calculate stats
* Utility tools – Data manipulation, bulk operations, testing helpers
* LLM integration tools (optional) – AI‑assisted audits and generation

**Minimum viable tool set – Phase 1 (Test)**

| Tool | Purpose | Inputs | Outputs |
| --- | --- | --- | --- |
| validate\_build\_test.py | Validate test build structure and refs | data/\*.json, builds/test-dummy.json | Console: OK or violations |
| export\_build\_test\_md.py | Generate Markdown grid for test build | data/\*.json, builds/test-dummy.json | builds/test-dummy.md |

**Expanded tool set – Phase 2 (Real Build)**

| Tool | Purpose | Inputs | Outputs |
| --- | --- | --- | --- |
| validate\_build.py | Validate any build (structure, IDs, rules) | data/\*.json, builds/<build\_id>.json | Console: violations list or OK |
| export\_build\_md.py | Generate Markdown grid for any build | data/\*.json, builds/<build\_id>.json | builds/<build\_id>.md |
| aggregate\_effects.py | Compute all active buffs/debuffs for a build | data/\*.json, builds/<build\_id>.json | JSON: aggregated effects list |
| compute\_pillars.py | Validate pillar requirements (resist/speed/etc.) | data/\*.json, builds/<build\_id>.json | JSON: pillar status per pillar |
| validate\_data\_integrity.py | Check data file consistency (unique IDs, refs) | data/\*.json | Console: data integrity report |

**Tool execution pattern**

All tools follow this pattern:

python

# tools/some\_tool.py

import json

import sys

from pathlib import Path

def load\_json(path):

with open(path, "r", encoding="utf-8") as f:

return json.load(f)

def main():

# 1. Load data files

skills = load\_json("data/skills.json")

effects = load\_json("data/effects.json")

# Optionally sets, cp-stars, build, etc.

# 2. Perform operation (validate, export, compute)

result = do\_work(skills, effects)

# 3. Output result (print, write file, exit code)

if result["status"] == "ok":

print("OK")

sys.exit(0)

else:

print(f"ERRORS: {result['errors']}")

sys.exit(1)

if \_\_name\_\_ == "\_\_main\_\_":

main()

**Tool execution requirements**

* No interactive prompts: tools run fully automated.
* Clear exit codes: 0 for success, non‑zero for failure.
* Structured output: JSON or clear text lists, never ambiguous messages.
* Logging: write detailed logs to logs/ for debugging.
* Idempotent: running the same tool twice produces identical results.​

## 4. Backend API Service

**Technology stack**

* Runtime: Node.js 18+
* Framework: Express.js
* Language: TypeScript
* Deployment: Render free tier

**API responsibilities**

* Serve global data files (/api/data/\*).
* Serve and update build records (/api/builds/\*).
* Validate build changes before saving.
* Compute derived stats (effect aggregation, pillar status).
* Never store state; all data comes from JSON files on disk.

**API endpoints (v1)**

| Method | Endpoint | Purpose | Returns |
| --- | --- | --- | --- |
| GET | /api/data/skills | Get all skills | { skills: [...] } |
| GET | /api/data/effects | Get all effects | { effects: [...] } |
| GET | /api/data/sets | Get all sets | { sets: [...] } |
| GET | /api/data/cp-stars | Get all CP stars | { cp\_stars: [...] } |
| GET | /api/builds/:id | Get specific build | { ...build } |
| PUT | /api/builds/:id | Update build (full replace) | { status: "ok" } or { errors: [...] } |
| POST | /api/builds/:id/validate | Validate build (no save) | { valid: boolean, violations: [...] } |
| POST | /api/builds/:id/compute-effects | Get aggregated effects | { effects: [...] } |
| POST | /api/builds/:id/compute-pillars | Get pillar status | { pillars: { ... } } |

**Backend configuration**

* Port: 3000 (configurable via env var).
* Data directory: ../data (relative to backend root).
* Builds directory: ../builds.
* CORS: allow frontend origin only.
* Error handling: structured JSON error responses.

**Deployment requirements**

* Platform: Render free tier Web Service.
* Build command: cd backend && npm install && npm run build
* Start command: npm start
* Environment variables:
  + NODE\_ENV=production
  + PORT=10000 (Render default)
  + DATA\_PATH=../data
  + BUILDS\_PATH=../builds
* Health check endpoint: GET /health → { status: "ok", timestamp: "..." }.

## 5. Frontend Application

**Technology stack**

* Framework: React 18+
* Build tool: Vite
* Language: TypeScript
* Styling: CSS (design system from Overview doc)
* Deployment: Vercel or Netlify free tier

**Frontend responsibilities**

* Display build editor UI with selector‑only inputs.
* Fetch global data from backend on load.
* Auto‑populate tooltip/detail fields from global data.
* Send build updates to backend for validation and saving.
* Display computed stats (effects, pillars, speed, resist).
* Never store or duplicate ESO game data in frontend code.

**Core UI components**

| Component | Purpose | Data source |
| --- | --- | --- |
| BuildEditor | Top‑level build editing interface | /api/builds/:id |
| SkillSelector | Skill dropdown/search | /api/data/skills |
| SkillTooltip | Read‑only skill details | Local skills data |
| GearSlot | Set/trait/enchant selector | /api/data/sets |
| CPSelector | CP star selection per tree/slot | /api/data/cp-stars |
| EffectDisplay | Show active buffs/debuffs | /api/builds/:id/compute-effects |
| PillarStatus | Show pillar pass/fail status | /api/builds/:id/compute-pillars |
| SpeedCalculator | Display speed breakdown | Computed from gear/CP/skills client‑side or via API |

**Frontend data flow**

* On mount:
  + GET /api/data/skills → populate skill dropdowns.
  + GET /api/data/sets → populate set dropdowns.
  + GET /api/data/cp-stars → populate CP dropdowns.
  + GET /api/builds/permafrost-marshal → load build state.
* On user selection (e.g. skill):
  + Update in‑memory build object.
  + Look up full skill record from loaded skills data.
  + Display tooltip fields (cost, duration, radius, effects).
  + Mark build as unsaved.
* On save:
  + PUT /api/builds/permafrost-marshal with updated build JSON.
  + Backend validates and writes file.
  + Frontend updates to saved state.
* On compute request:
  + POST /api/builds/permafrost-marshal/compute-effects → show aggregated buffs/debuffs.
  + POST /api/builds/permafrost-marshal/compute-pillars → show pillar status.

**Frontend configuration**

* API base URL: http://localhost:3000 (dev) or production URL.
* Build ID: configurable (starting with permafrost-marshal).
* Auto‑save: off by default; manual save button.

## 6. Testing & Validation Framework

**Testing phases**

* **Phase 1: Test build pipeline**
  + Use test-dummy build with minimal data.
  + Validate all tools run without errors.
  + Confirm MD export generates valid output.
  + No real ESO data involved.
* **Phase 2: Real build integration**
  + Add Permafrost Marshal data.
  + Run all validators on real build.
  + Confirm frontend displays real data correctly.
  + Test save/load cycle end‑to‑end.
* **Phase 3: Computation accuracy**
  + Verify effect aggregation matches expected buffs.
  + Validate pillar calculations (resist, speed, HoTs, shields, core).
  + Test Major/Minor stacking rules and set bonus math.

**Validation checklist (per build)**

* Build structure valid (bars, gear, CP layout).
* All skill\_id values exist in data/skills.json.
* All set\_id values exist in data/sets.json.
* All CP IDs exist in data/cp-stars.json.
* All effect\_id references exist in data/effects.json.
* At most 1 mythic equipped.
* All gear slots populated.
* CP trees have ≤ 4 slotted stars each.
* Attributes sum correctly.
* No duplicate skills per bar/slot.
* Effect stacking rules respected (Major/Minor uniqueness).

**Testing tools**

* tools/validate\_build\_test.py – Automated test validator.
* tools/validate\_build.py – Production validator.
* tools/validate\_data\_integrity.py – Data file consistency checker.
* Manual inspection: git diff before commits.

**Error handling requirements**

* All validators must:
  + Return structured error lists (not generic messages).
  + Include exact location of error (file, ID, field).
  + Suggest fixes when possible.
  + Never silently fail.

## 7. Deployment & Hosting

**Backend deployment (Render)**

* Service type: Web Service.
* Region: US (closest to you).
* Build command: cd backend && npm install && npm run build
* Start command: npm start
* Environment variables:
  + NODE\_ENV=production
  + PORT=10000
  + DATA\_PATH=../data
  + BUILDS\_PATH=../builds
* Auto‑deploy: optional on push to main.
* Health check: GET /health.

**Frontend deployment (Vercel/Netlify)**

* Framework preset: Vite.
* Build command: cd frontend && npm install && npm run build
* Output directory: frontend/dist
* Environment variables:
  + VITE\_API\_BASE\_URL=https://your-backend.onrender.com
* Auto‑deploy: optional on push to main.

**Deployment workflow**

1. Make changes locally.
2. Run validators: python tools/validate\_build.py.
3. Commit to Git: git add . && git commit -m "description".
4. Push: git push origin main.
5. Backend auto‑deploys to Render (if configured).
6. Frontend auto‑deploys to Vercel/Netlify (if configured).
7. Test production URLs.

**Free tier limitations** (sufficient for personal use/initial development):​

* Render: 750 hours/month, spins down after 15 min idle, cold start ~30s.
* Vercel: 100 GB bandwidth/month, generous build limits.
* Netlify: 100 GB bandwidth/month, 300 build minutes/month.

## 8. Monitoring & Maintenance

**Health checks**

* Backend: GET /health → { status: "ok", timestamp: "..." }.
* Frontend: manual smoke test after deployment.
* Data integrity: run validate\_data\_integrity.py weekly.

**Logging strategy**

* Backend: console logs to Render’s log viewer.
* Tools: write to logs/\*.log with timestamps.
* LLM interactions: separate logs under logs/llm/.
* Git history: clear commit messages for data changes.

**Backup strategy**

* Primary: Git repository (GitHub remote).
* Secondary: local clone on your machine.
* Tertiary: periodic exports to external storage (optional).
* All data is version‑controlled; no extra backup beyond Git is required.

**Update workflow**

* **For data updates (skills, effects, sets, CP):**
  + Edit JSON locally.
  + Run python tools/validate\_data\_integrity.py.
  + Run python tools/validate\_build.py.
  + Commit if valid and push.
* **For build updates:**
  + Edit via frontend UI (when available).
  + Frontend sends build JSON to backend for validation.
  + Backend writes to builds/\*.json.
  + Commit and push.

**Maintenance tasks**

* Weekly: run data integrity validator.
* After ESO patch: update affected skills/sets/CP in data files.
* Monthly: review logs for errors or warnings.
* Quarterly: review and refactor tools for efficiency.

## 9. Development Workflow (Standard Operating Procedure)

**Day‑to‑day workflow**

* Start local environment:

bash

# Terminal 1: Backend

cd backend

npm run dev

# Terminal 2: Frontend (when available)

cd frontend

npm run dev

* Make changes:
  + Edit JSON data files in VS Code.
  + Run validators: python tools/validate\_build.py.
  + Test in frontend (when available).
* Validate before commit:

bash

python tools/validate\_data\_integrity.py

python tools/validate\_build.py --build builds/permafrost-marshal.json

* Commit and push:

bash

git add .

git commit -m "Description of changes"

git push origin main

**AI interaction workflow (in new threads)**

* Start a new thread with AI.
* Paste one or more control docs:
  + docs/ESO-Build-Engine-Overview.md (always).
  + Relevant doc for the task (Data Model, Global Rules, or Data Center).
* Provide current state:
  + “Working on X feature”
  + “Need to add Y data”
  + “Tool Z is failing with error E”
* AI provides complete file contents or tool definitions.
* Save files locally, run tools, validate.
* Report results back to AI if issues.

**Critical rules (always follow)**

* Never edit build MD files by hand – always generated from JSON.
* Never duplicate data – IDs reference global data only.
* Validate before commit – run validators every time.
* Full file operations only – no copy/paste snippets.
* git diff before commit – review every change.
* Test with test-dummy first – validate pipeline before real data.

## 10. Success Criteria (Data Center Operational)

The data center is considered **operational** when:

**Phase 1: Test Build (Minimal Viable Pipeline)**

* data/skills.json contains at least one test skill.
* data/effects.json contains at least one test effect.
* data/sets.json contains at least one test set.
* data/cp-stars.json contains at least one test CP star.
* builds/test-dummy.json exists and references test data IDs.
* tools/validate\_build\_test.py runs and returns OK.
* tools/export\_build\_test\_md.py runs and generates builds/test-dummy.md.
* All generated files are valid (parseable JSON, readable MD).

**Phase 2: Real Build Integration**

* data/skills.json contains all 12 Permafrost Marshal skills.
* data/effects.json contains all buffs/debuffs used by those skills/sets/CP.
* data/sets.json contains all 4 sets (Adept Rider, Pariah, Nibenay, Wild Hunt).
* data/cp-stars.json contains all 12 slotted CP stars.
* builds/permafrost-marshal.json exists and is valid.
* tools/validate\_build.py runs on real build and returns OK.
* tools/export\_build\_md.py generates an accurate Markdown grid.
* Backend API serves all data endpoints correctly.
* Frontend loads and displays the build in the editor UI.

**Phase 3: Full Functionality**

* Effect aggregation tool computes correct active buffs/debuffs.
* Pillar computation validates resist/health/speed/HoTs/shields/core.
* Frontend auto‑populates all tooltip fields from global data.
* Frontend can save build changes via backend.
* All validators pass on production data.
* Backend and frontend deployed to free hosting.
* No manual copy/paste required for any workflow.

Each phase is independently testable and deployable, and all of them respect the core non‑negotiables defined in the Overview doc.
