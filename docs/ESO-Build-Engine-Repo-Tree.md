# ESO Build Engine – Repo Tree (Working Copy)

## Repository identity

- Local path (primary dev machine):  
  `C:\Projects\The-Elder-Elemental`

- Canonical GitHub repository:  
  `https://github.com/oNeEyE-777/The-Elder-Elemental`

- Mirror repository:  
  `https://github.com/oNeEyE-777/The-Elder-Elemental-mirror`

## Top-level layout

- .github/
  - workflows/
    - mirror.yml
- builds/
  - permafrost-marshal-effects.json
  - permafrost-marshal.json
  - permafrost-marshal.md
  - test-dummy.json
  - test-dummy.md
- data/
  - cp-stars.json
  - effects.json
  - sets.json
  - skills.json
- docs/
  - ESO Build Database Project Specification.md
  - ESO Build Engine – Copilot Bootstrap.md
  - ESO Build Engine – Data Center Tool Checklist.md
  - ESO-Build-Engine-Data-Center-Scope.md
  - ESO-Build-Engine-Data-Model-v1.md
  - ESO-Build-Engine-Global-Rules.md
  - ESO-Build-Engine-Overview.md
  - ESO-Build-Engine-Repo-Tree.md
  - ESO-Build-Engine-Spaces-Initial-Thread.md
  - ESO-Build-Engine-Spaces-Preamble.md
  - ESO-Build-Engine-Spaces-Session-01-Preamble.md
  - index.md
- tools/
  - aggregate_effects.py
  - compute_pillars.py
  - export_build_md.py
  - export_build_test_md.py
  - validate_build_test.py
  - validate_build.py
- README.md
- root-test.md

## Current Python tools (summary)

- `tools/aggregate_effects.py`  
  - Aggregates active effects for a build prior to stacking and pillar math.[file:19][file:20]
- `tools/compute_pillars.py`  
  - Evaluates pillar requirements (resist, health focus, speed, HoTs, shields, core combo) against aggregated effects.[file:19][file:20]
- `tools/export_build_md.py`  
  - Exports a Markdown grid for a real build.
- `tools/export_build_test_md.py`  
  - Exports a Markdown grid for the test-dummy build.
- `tools/validate_build_test.py`  
  - Validates `builds/test-dummy.json` structure and references.[file:10]
- `tools/validate_build.py`  
  - Validates any build structure, IDs, and global rules (primary validator).[file:10][file:19]

## Local development tooling (host environment)

These are the tools used to work with this repo on your machine (not enforced by code, but important context):[file:10][file:20]

- **Code editor / IDE**
  - Visual Studio Code (VS Code) as the primary editor and terminal host.
- **Version control**
  - Git (CLI) for commits, branching, and history.
  - GitHub as the remote repository host (`The-Elder-Elemental` and its mirror).
  - GitHub Desktop as a GUI client for Git operations.
- **Runtimes**
  - Python 3.x (for all scripts under `tools/`).
  - Node.js 18+ planned for backend and frontend (per Data Center Scope, even if not yet present as folders).[file:20]
- **GitHub automation**
  - `.github/workflows/mirror.yml` for repository mirroring / CI-related automation.

The authoritative, intended stack (Python, Node.js, VS Code, Git) remains documented in `docs/ESO-Build-Engine-Data-Center-Scope.md`; this file mirrors the **actual** current state of your local repo and tools so new threads and contributors have a concrete baseline.[file:20]

## Space file → repo path mapping (Python tools)

Because `.py` files cannot be uploaded directly into Spaces, the following uploaded text files mirror the actual Python tools in `tools/`:

- `aggregate_effects.txt` → `tools/aggregate_effects.py`
- `compute_pillars.txt` → `tools/compute_pillars.py`
- `export_build_md.txt` → `tools/export_build_md.py`
- `export_build_test_md.txt` → `tools/export_build_test_md.py`
- `validate_build.txt` → `tools/validate_build.py`
- `validate_build_test.txt` → `tools/validate_build_test.py`
