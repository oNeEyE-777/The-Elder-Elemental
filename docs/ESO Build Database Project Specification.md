\# ESO Build Database Project — Data Sourcing \& Implementation Specification \*\*docs/ESO-Build-Database-Project-Specification.md\*\*



\## Executive Summary



This document outlines the requirements, data sourcing workflow, and implementation roadmap for building a comprehensive ESO (Elder Scrolls Online) build database and potential addon.\[file:5]  

The system will leverage official in-game IDs as canonical parent keys, with all custom metadata (builds, rotations, annotations, tags) stored as child records that reference those IDs.\[file:5]



\*\*Core principle:\*\* Anchor everything to ESO's existing ID system (`abilityId`, `itemId`, `setId`, etc.) and build meta-layers on top, rather than recreating raw game data.\[file:5]



\*\*Timeline:\*\* This project begins \*\*after\*\* the JSON-based Data Center validation phase is complete and proven stable.\[file:4]\[file:5]



---



\## Project Scope



\### Primary Objectives



1\. \*\*Canonical data layer\*\*  

&nbsp;  Maintain authoritative tables of ESO game objects (abilities, items, sets, buffs, debuffs) keyed by official ESO IDs.\[file:5]



2\. \*\*Meta-layer\*\*  

&nbsp;  Build custom tables for builds, rotations, skill bars, gear configurations, and player annotations that reference canonical IDs.\[file:5]



3\. \*\*API/query interface\*\*  

&nbsp;  Enable efficient lookups, filtering, and relationship traversal (for example, “show all builds using Deep Fissure + Major Breach sources”).\[file:5]



4\. \*\*Future addon support\*\*  

&nbsp;  Design schema to support eventual in-game addon integration with minimal refactoring.\[file:5]



\### Out of Scope (Initial Phase)



\- Real-time game data sync (manual periodic updates acceptable).

\- Automated build optimization or theorycrafting AI.

\- Public web API hosting (internal/local use first).

\- Player account integration or cloud sync.\[file:5]



---



\## Data Architecture Overview



\### Parent-Child Relationship Model



ESO Official IDs (Parents)  

↓  

Items (`itemId`)  

Abilities (`abilityId`)  

Sets (`setId`)  

Buffs/Debuffs (`effectId`)  

↓  

Custom Metadata (Children – Foreign Keys)  

↓  

Builds (`buildId`)  

├─ BuildSkills (fk: `abilityId`)  

├─ BuildGear (fk: `itemId`, `setId`)  

├─ BuildRotations (fk: `abilityId`)  

└─ BuildTags (fk: `tagId`)\[file:5]



\*\*Key decision:\*\* Official ESO IDs are \*\*parent keys\*\* at the base data layer. All custom data references them as \*\*foreign keys (children)\*\*.\[file:5]



---



\## Core Database Tables (Simplified Schema)



\### Canonical Layer (ESO Data)



\*\*Table: Abilities\*\*



\- Primary Key: `abilityId` (integer, official ESO ID)

\- Fields: `name`, `description`, `skillLine`, `morphBase`, `duration`, `cost`, `range`, `effectType`

\- Source: ESO Lua API or UESP dumps.\[file:5]



\*\*Table: Items\*\*



\- Primary Key: `itemId` (integer, official ESO ID)

\- Fields: `name`, `quality`, `equipSlot`, `itemType`, `trait`, `setId` (fk if part of set)

\- Source: ESO Lua API or UESP dumps.\[file:5]



\*\*Table: Sets\*\*



\- Primary Key: `setId` (integer, official ESO ID)

\- Fields: `name`, `location`, `type`, `bonuses` (JSON array of 2/3/4/5-piece effects)

\- Source: ESO Lua API, LibSets, or community dumps.\[file:5]



\*\*Table: Buffs\*\*



\- Primary Key: `effectId` (integer, official ESO ID for named buffs/debuffs)

\- Fields: `name`, `type` (Major/Minor), `category` (buff/debuff), `description`, `magnitude`

\- Source: ESO Lua API or buff database dumps.\[file:5]



\### Meta Layer (Custom Data)



\*\*Table: Builds\*\*



\- Primary Key: `buildId` (integer, auto-increment)

\- Fields: `name`, `class`, `subclasses`, `role`, `cpTotal`, `authorId`, `created`, `updated`, `description`.\[file:5]



\*\*Table: BuildSkills\*\*



\- Primary Key: `buildSkillId`

\- Foreign Keys: `buildId`, `abilityId`

\- Fields: `bar` (front/back), `slot` (1–5 or ult), `scriptFocus`, `scriptSignature`, `scriptAffix` (nullable for scribing).\[file:5]



\*\*Table: BuildGear\*\*



\- Primary Key: `buildGearId`

\- Foreign Keys: `buildId`, `setId`, `itemId`

\- Fields: `slot` (head/chest/legs/etc.), `trait`, `enchant`, `quality`.\[file:5]



\*\*Table: BuildRotations\*\*



\- Primary Key: `rotationId`

\- Foreign Keys: `buildId`

\- Fields: `name` (for example, “Full Bring-Up”, “Panic Escape”), `sequence` (JSON array of `abilityId` + timing), `notes`.\[file:5]



\*\*Table: BuildTags\*\*



\- Junction table for many-to-many taxonomy

\- Foreign Keys: `buildId`, `tagId`.\[file:5]



\*\*Table: Tags\*\*



\- Primary Key: `tagId`

\- Fields: `name`, `category` (for example, “PvP”, “Tank”, “Solo”, “Speed”).\[file:5]



---



\## Data Sourcing Requirements



\### What You Need to Provide



To populate the canonical layer, you will need to extract and deliver the following data from ESO.\[file:5]



\#### 1. Abilities Data



\- Source: ESO Lua API via custom addon or UESP API dump.\[file:5]

\- Required fields per ability:

&nbsp; - `abilityId` (integer) — official ESO ID

&nbsp; - `name` (string)

&nbsp; - `description` (string) — tooltip text

&nbsp; - `skillLine` (string)

&nbsp; - `morphBase` (integer, nullable)

&nbsp; - `duration` (float, nullable) — seconds

&nbsp; - `cost` (integer)

&nbsp; - `range` (float) — meters

&nbsp; - `effectType` (string) — for example, `Damage`, `Heal`, `Buff`, `Debuff`, `CC`\[file:5]



Delivery format: JSON or CSV.\[file:5]



\#### 2. Items \& Sets Data



\- Source: ESO Lua API or UESP item database / community dumps.\[file:5]

\- Required fields per item:

&nbsp; - `itemId`, `name`, `quality`, `equipSlot`, `itemType`, `trait`, `setId` (nullable).\[file:5]

\- Required fields per set:

&nbsp; - `setId`, `name`, `location`, `type`, `bonuses` (JSON array).\[file:5]



Delivery format: JSON or CSV.\[file:5]



\#### 3. Buffs \& Debuffs Data



\- Source: ESO Lua API or community buff databases.\[file:5]

\- Required fields per buff/debuff:

&nbsp; - `effectId`, `name`, `type` (Major/Minor), `category` (Buff/Debuff), `description`, `magnitude`.\[file:5]



Delivery format: JSON or CSV.\[file:5]



---



\## Data Delivery Checklist



For each data type, provide:\[file:5]



\- \[ ] Format: JSON or CSV (JSON preferred for nested structures like set bonuses)

\- \[ ] Encoding: UTF-8 without BOM

\- \[ ] Structure: Consistent field names matching this specification

\- \[ ] Validation: No duplicate IDs, no missing required fields

\- \[ ] Version: ESO patch/API version number the data was extracted from

\- \[ ] Timestamp: When the data was extracted



Delivery method: Shared cloud storage or downloadable link; split files by category if large.\[file:5]



---



\## Implementation Roadmap



\### Phase 0: Data Center Validation (Prerequisite)



\*\*Status:\*\* Must be completed before starting this project.\[file:4]\[file:5]



Objective: Validate that core JSON-based Data Center infrastructure (data files, Python tools, backend, frontend) is stable and operational.\[file:4]\[file:5]



---



\### Phase 1: Schema Design \& Canonical Layer



Objective: Design and implement base database schema with canonical ESO data tables.\[file:5]



Tasks (summarized):



\- Finalize DB schema (DDL scripts for Abilities, Items, Sets, Buffs tables).

\- Define foreign keys and indexes.

\- Create data import scripts (JSON/CSV → database).

\- Import initial dataset.

\- Validate data integrity.\[file:5]



---



\### Phase 2: Meta Layer \& Build Tables



Objective: Implement custom metadata tables for builds, rotations, gear, and tags.\[file:5]



Tasks:



\- Create Builds, BuildSkills, BuildGear, BuildRotations, BuildTags, Tags tables.

\- Define relationships and constraints.

\- Insert sample builds (e.g., Permafrost Marshal).

\- Test representative queries (for example, “find all abilities used in tank builds with Major Breach”).\[file:5]



---



\### Phase 3: API \& Query Interface



Objective: Build API layer for querying and manipulating build data.\[file:5]



Tasks (high level):



\- Design REST endpoints (GET/POST builds, abilities, sets, buffs).

\- Implement API (e.g., Node/Express or Python/FastAPI).

\- Add filtering, sorting, pagination, and search.

\- Document API (OpenAPI/Swagger).\[file:5]



---



\### Phase 4: Frontend Prototype



Objective: Create basic web interface for browsing and creating builds.\[file:5]



Tasks:



\- Implement build browser and detail view.

\- Implement build editor (skill bars, gear, tags).

\- Connect to API.

\- Iterate based on usability.\[file:5]



---



\### Phase 5: Addon Development



Objective: Develop ESO Lua addon for in-game integration.\[file:5]



Tasks:



\- Design in-game build viewer/switcher UI.

\- Implement Lua code to read local build data.

\- Implement skill bar application from saved builds.

\- Test and package addon.\[file:5]



---



\### Phase 6: Iteration \& Polish



Objective: Refine the system based on testing and feedback.\[file:5]



Tasks:



\- Add more builds.

\- Improve query performance.

\- Enhance UI/UX.

\- Add export/import features.

\- Integrate ESO patch updates.\[file:5]



---



\## Relationship to the ESO Build Engine Data Center



\- This database project \*\*depends on\*\* a stable JSON Data Center pipeline (data files, Python tools, backend, frontend) described in `docs/ESO-Build-Engine-Data-Center-Scope.md`.\[file:4]\[file:5]\[file:23]

\- The Data Center remains the authoritative source for build definitions (`builds/\*.json`) and ESO math rules; this project adds a relational mirror and richer query capabilities on top.\[file:2]\[file:3]\[file:4]\[file:5]

\- No database work should start before Data Center Phase 2/3 success criteria are met.\[file:4]\[file:5]\[file:23]



