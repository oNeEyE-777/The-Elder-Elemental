# ESO Build Engine – Data Center Scope & Implementation Plan **docs/ESO-Build-Engine-Data-Center-Scope.md**

## Purpose

Define the complete “data center” infrastructure needed to support the ESO Build Engine: tools, services, configuration, testing, validation, and deployment components that make the system operational.[file:4]

This document covers:

* Local development environment
* Data storage and management
* Automation tools (Python scripts)
* Backend API service
* Frontend application
* Testing and validation framework
* Deployment and hosting
* Monitoring and maintenance

> **Schema source of truth**  
> All JSON shapes for `data/*.json` and `builds/*.json` are defined by `docs/ESO-Build-Engine-Data-Model-v1.md`. Backend TypeScript types and Python validators must follow this Data Model v1 schema, and any schema changes must be reflected in that doc first before code is updated.[file:2][file:4]

---

## 1. Local Development Environment

**Required software**

* Git – Version control for the entire repo
* Python 3.10+ – Automation scripts and validators
* Node.js 18+ – Backend API and frontend build tooling
* VS Code (or preferred editor) – Primary editing environment
* LM Studio (optional, later) – Local LLM for AI‑assisted tasks[file:4]

**Repository structure**

```text
The-Elder-Elemental/

├── data/                    # Global JSON "database"
│   ├── skills.json
│   ├── effects.json
│   ├── sets.json
│   ├── cp-stars.json
│   ├── mundus.json          # (future)
│   ├── food.json            # (future)
│   └── enchants.json        # (future)

├── builds/                  # Build records
│   ├── test-dummy.json      # Test build for pipeline validation
│   ├── test-dummy.md        # Generated MD export (test)
│   ├── permafrost-marshal.json  # Real build (after test passes)
│   └── permafrost-marshal.md    # Generated MD export (real)

├── tools/                   # Python automation scripts
│   ├── validate_build_test.py      # Test validator
│   ├── export_build_test_md.py     # Test MD exporter
│   ├── validate_build.py           # Real validator (after test)
│   ├── export_build_md.py          # Real MD exporter (after test)
│   ├── aggregate_effects.py        # Buff/debuff aggregation logic
│   ├── compute_pillars.py          # Pillar validation (resist/speed/etc.)
│   ├── validate_data_integrity.py  # Data integrity checks
│   └── llm_helper.py               # (optional) LM Studio integration

├── backend/                 # Node.js/Express API
│   ├── src/
│   │   ├── index.ts         # Main server entry
│   │   ├── routes/
│   │   │   ├── data.ts      # /api/data/* endpoints
│   │   │   └── builds.ts    # /api/builds/* endpoints
│   │   ├── lib/
│   │   │   ├── loader.ts    # JSON file loading
│   │   │   ├── validator.ts # Build validation logic
│   │   │   └── math.ts      # Effect aggregation and pillar computation
│   │   └── types/
│   │       └── index.ts     # TypeScript types for data schemas
│   ├── package.json
│   └── tsconfig.json

├── frontend/                # React/Vite UI
│   ├── src/
│   │   ├── App.tsx          # Main app component
│   │   ├── components/
│   │   │   ├── BuildEditor.tsx     # Main build editing UI
│   │   │   ├── SkillSelector.tsx   # Skill selection dropdown/search
│   │   │   ├── GearSlot.tsx        # Gear slot editor
│   │   │   ├── CPSelector.tsx      # CP star selection
│   │   │   └── EffectDisplay.tsx   # Buff/debuff display
│   │   ├── lib/
│   │   │   ├── api.ts        # API client for backend
│   │   │   └── types.ts      # TypeScript types (shared with backend)
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts

├── logs/                    # Tool execution logs
│   └── llm/                 # LLM interaction logs (if used)

├── docs/                    # Control documentation
│   ├── ESO-Build-Engine-Overview.md
│   ├── ESO-Build-Engine-Data-Model-v1.md
│   ├── ESO-Build-Engine-Global-Rules.md
│   └── ESO-Build-Engine-Data-Center-Scope.md

├── .gitignore
├── README.md
└── package.json             # (optional) root workspace config
