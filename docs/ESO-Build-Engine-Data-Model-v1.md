File: docs/ESO-Build-Engine-Data-Model-v1.md
Last-Updated: 2026-02-13 05:45:00Z

# ESO Build Engine Data Model v1

## 1. Purpose

This document defines the **v1 JSON data model** for the ESO Build Engine:

- Canonical schemas for ESO skills, effects, sets, Champion Points, and builds.
- ID conventions and namespace prefixes.
- External mapping appendices showing how ESO-Hub snapshot fields (and optionally other sources) map into the canonical model.

It must remain consistent with:

- `ESO-Build-Engine-Overview.md`
- `ESO-Build-Engine-Global-Rules.md`
- `ESO-Build-Engine-External-Data-Scope.md`
- `ESO-Build-Engine-External-Data-Runbook.md`
- `ESO-Build-Engine-ESO-Hub-Integration.md`
- `ESO-Build-Engine-Alignment-Control.md` [file:1024][file:1026][file:1022][file:1023][file:1021][file:1018]


## 2. ID conventions and namespaces

All IDs in canonical JSON must:

- Be strings.
- Use a **namespace prefix** that identifies the entity type.

Canonical prefixes:

- Skills: `skill.` (e.g. `skill.deepfissure`)
- Effects: `buff.`, `debuff.`, `hot.`, `shield.` (e.g. `buff.majorresolve`, `hot.resolvingvigor`)
- Sets: `set.` (e.g. `set.markofthepariah`)
- Champion Points: `cp.` (e.g. `cp.ironclad`)
- Builds: `build.` (e.g. `build.permafrostmarshal`) [file:1018]

Rules:

- Tools must not add or strip prefixes dynamically; IDs are stored fully prefixed in JSON and referenced as such.
- No alternate or alias key names for IDs are allowed in canonical files; use `id` consistently. [file:1018]


## 3. Canonical schemas

This section defines the canonical schema for each core file under `data/` and `builds/`.

### 3.1 Skills (`data/skills.json`)

Top-level:

- Either a bare array of skill objects, or
- An object:

  ```json
  {
    "skills": [ ... ]
  }
