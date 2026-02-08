**ESO Build Database Project — Data Sourcing & Implementation Specification**

**Executive Summary**

This document outlines the requirements, data sourcing workflow, and implementation roadmap for building a comprehensive ESO (Elder Scrolls Online) build database and potential addon. The system will leverage official in-game IDs as canonical parent keys, with all custom metadata (builds, rotations, annotations, tags) stored as child records that reference those IDs.

**Core principle**: Don't recreate the wheel—anchor everything to ESO's existing ID system (abilityId, itemId, setId, etc.) and build intelligent meta-layers on top.

**Timeline**: This project begins after the "data center" validation phase is complete and proven stable.

**Project Scope**

**Primary Objectives**

1. **Canonical data layer**: Maintain authoritative tables of ESO game objects (abilities, items, sets, buffs, debuffs) keyed by official ESO IDs.
2. **Meta-layer**: Build custom tables for builds, rotations, skill bars, gear configurations, and player annotations that reference canonical IDs.
3. **API/query interface**: Enable efficient lookups, filtering, and relationship traversal (e.g., "show all builds using Deep Fissure + Major Breach sources").
4. **Future addon support**: Design schema to support eventual in-game addon integration with minimal refactoring.

**Out of Scope (Initial Phase)**

* Real-time game data sync (manual periodic updates acceptable)
* Automated build optimization or theorycrafting AI
* Public web API hosting (internal/local use first)
* Player account integration or cloud sync

**Data Architecture Overview**

**Parent-Child Relationship Model**

ESO Official IDs (Parents)
↓
Items (itemId)
Abilities (abilityId)
Sets (setId)
Buffs/Debuffs (effectId)
↓
Custom Metadata (Children - Foreign Keys)
↓
Builds (buildId)
├─ BuildSkills (fk: abilityId)
├─ BuildGear (fk: itemId, setId)
├─ BuildRotations (fk: abilityId)
└─ BuildTags (custom taxonomy)

**Key decision**: Official ESO IDs are **parent keys** at the base data layer. All our custom data references them as **foreign keys (children)**.

**Core Database Tables (Simplified Schema)**

**Canonical Layer (ESO Data)**

**Table: Abilities**

* Primary Key: abilityId (integer, official ESO ID)
* Fields: name, description, skillLine, morphBase, duration, cost, range, effectType
* Source: ESO Lua API or UESP dumps

**Table: Items**

* Primary Key: itemId (integer, official ESO ID)
* Fields: name, quality, equipSlot, itemType, trait, setId (fk if part of set)
* Source: ESO Lua API or UESP dumps

**Table: Sets**

* Primary Key: setId (integer, official ESO ID)
* Fields: name, location, type, bonuses (JSON array of 2/3/4/5-piece effects)
* Source: ESO Lua API, LibSets, or community dumps

**Table: Buffs**

* Primary Key: effectId (integer, official ESO ID for named buffs/debuffs)
* Fields: name, type (Major/Minor), category (buff/debuff), description, magnitude
* Source: ESO Lua API or buff database dumps

**Meta Layer (Custom Data)**

**Table: Builds**

* Primary Key: buildId (integer, auto-increment)
* Fields: name, class, subclasses, role, cpTotal, authorId, created, updated, description

**Table: BuildSkills**

* Primary Key: buildSkillId
* Foreign Keys: buildId, abilityId
* Fields: bar (front/back), slot (1-5 or ult), scriptFocus, scriptSignature, scriptAffix (nullable for scribing)

**Table: BuildGear**

* Primary Key: buildGearId
* Foreign Keys: buildId, setId, itemId
* Fields: slot (head/chest/legs/etc.), trait, enchant, quality

**Table: BuildRotations**

* Primary Key: rotationId
* Foreign Keys: buildId
* Fields: name (e.g., "Full Bring-Up", "Panic Escape"), sequence (JSON array of abilityId + timing), notes

**Table: BuildTags**

* Junction table for many-to-many taxonomy
* Foreign Keys: buildId, tagId

**Table: Tags**

* Primary Key: tagId
* Fields: name, category (e.g., "PvP", "Tank", "Solo", "Speed")

**Data Sourcing Requirements**

**What You Need to Provide**

To populate the canonical layer, you will need to extract and deliver the following data from ESO:

**1. Abilities Data**

**Source**: ESO Lua API via custom addon or UESP API dump[web:263][web:271]

**Required fields per ability**:

* abilityId (integer) — official ESO ID
* name (string) — ability display name
* description (string) — tooltip text
* skillLine (string) — e.g., "Animal Companions", "Draconic Power", "Grave Lord"
* morphBase (integer, nullable) — base ability ID if this is a morph
* duration (float, nullable) — effect duration in seconds
* cost (integer) — magicka/stamina cost
* range (float) — ability range in meters
* effectType (string) — e.g., "Damage", "Heal", "Buff", "Debuff", "CC"

**Delivery format**: JSON or CSV

**Example JSON structure**:
[
{
"abilityId": 86019,
"name": "Deep Fissure",
"description": "Stir a group of shalk...",
"skillLine": "Animal Companions",
"morphBase": 86015,
"duration": 9.0,
"cost": 2700,
"range": 28.0,
"effectType": "Damage"
},
{
"abilityId": 115572,
"name": "Unnerving Boneyard",
"description": "Desecrate the ground...",
"skillLine": "Grave Lord",
"morphBase": 115093,
"duration": 10.0,
"cost": 2984,
"range": 28.0,
"effectType": "Damage"
}
]

**How to extract**:

* Option A: Use UESP ESO API[web:263] (pre-dumped data, updated per patch)
* Option B: Write a Lua addon using GetAbilityName(), GetAbilityDescription(), GetAbilityCost(), etc.[web:275][web:278]
* Option C: Use existing community dumps (LibSets-style libraries)[web:283]

**2. Items & Sets Data**

**Source**: ESO Lua API or UESP item database[web:263][web:271]

**Required fields per item**:

* itemId (integer)
* name (string)
* quality (integer, 0-5)
* equipSlot (string) — e.g., "Head", "Chest", "MainHand"
* itemType (string) — e.g., "Armor", "Weapon", "Jewelry"
* trait (string, nullable)
* setId (integer, nullable) — if part of a set

**Required fields per set**:

* setId (integer)
* name (string)
* location (string) — where obtained (e.g., "Crafted", "Cyrodiil", "Trial")
* type (string) — "Light", "Medium", "Heavy", "Jewelry", "Weapon"
* bonuses (JSON array) — 2/3/4/5-piece effects

**Delivery format**: JSON or CSV

**Example JSON structure**:
{
"sets": [
{
"setId": 399,
"name": "Pariah's Pinnacle",
"location": "Wrothgar",
"type": "Heavy",
"bonuses": [
{"pieces": 2, "effect": "Max Health"},
{"pieces": 3, "effect": "Max Health"},
{"pieces": 4, "effect": "Max Health"},
{"pieces": 5, "effect": "Armor and Spell Resist scale with missing Health"}
]
}
],
"items": [
{
"itemId": 12345,
"name": "Pariah's Cuirass",
"quality": 4,
"equipSlot": "Chest",
"itemType": "Armor",
"trait": "Reinforced",
"setId": 399
}
]
}

**How to extract**:

* Option A: UESP item/set database queries[web:263][web:277]
* Option B: Lua addon using GetItemLink(), GetItemLinkName(), GetItemLinkSetInfo()[web:275][web:278][web:282]
* Option C: LibSets library for set data[web:283]

**3. Buffs & Debuffs Data**

**Source**: ESO Lua API or community buff databases

**Required fields per buff/debuff**:

* effectId (integer) — official ESO ID for named effect
* name (string) — e.g., "Major Breach", "Minor Expedition"
* type (string) — "Major" or "Minor"
* category (string) — "Buff" or "Debuff"
* description (string) — effect description
* magnitude (float) — numerical effect (e.g., 15% for Minor Expedition)

**Delivery format**: JSON or CSV

**Example JSON structure**:
[
{
"effectId": 61742,
"name": "Major Breach",
"type": "Major",
"category": "Debuff",
"description": "Reduces Physical and Spell Resistance by 5948",
"magnitude": 5948
},
{
"effectId": 61693,
"name": "Minor Expedition",
"type": "Minor",
"category": "Buff",
"description": "Increases Movement Speed by 15%",
"magnitude": 0.15
}
]

**How to extract**:

* Option A: Community buff/debuff lists (reddit, UESP wiki compiled data)
* Option B: Lua addon tracking effect IDs from combat events
* Option C: Manual curation from known game data

**Data Delivery Checklist**

For each data type, provide:

* [ ] **Format**: JSON or CSV (JSON preferred for nested structures like set bonuses)
* [ ] **Encoding**: UTF-8 without BOM
* [ ] **Structure**: Consistent field names matching specification above
* [ ] **Validation**: No duplicate IDs, no missing required fields
* [ ] **Version**: ESO patch/API version number the data was extracted from
* [ ] **Timestamp**: When the data was extracted

**Delivery method**: Upload to shared cloud storage (Google Drive, Dropbox) or provide as downloadable link. If files exceed 10MB, split by category (abilities, items, sets, buffs).

**Implementation Roadmap**

**Phase 0: Data Center Validation (Prerequisite)**

**Status**: Must be completed before starting this project

**Objective**: Validate that core data center infrastructure (database, API, authentication) is stable and operational.

**Deliverables**:

* [ ] Database server operational and accessible
* [ ] Basic CRUD operations tested and performant
* [ ] Schema versioning and migration system in place
* [ ] Backup and recovery procedures documented

**Phase 1: Schema Design & Canonical Layer (Weeks 1-2)**

**Objective**: Design and implement base database schema with canonical ESO data tables.

**Tasks**:

1. Finalize database schema (SQL DDL scripts for Abilities, Items, Sets, Buffs tables)
2. Define foreign key constraints and indexes
3. Create data import scripts (JSON/CSV → database)
4. Import initial dataset provided by you
5. Validate data integrity (ID uniqueness, referential integrity)

**Deliverables**:

* [ ] Database schema v1.0 deployed
* [ ] Canonical tables populated with ESO data
* [ ] Data import pipeline documented

**Phase 2: Meta Layer & Build Tables (Weeks 3-4)**

**Objective**: Implement custom metadata tables for builds, rotations, gear, and tags.

**Tasks**:

1. Create Builds, BuildSkills, BuildGear, BuildRotations, BuildTags, Tags tables
2. Define relationships and constraints
3. Write sample data insertion scripts
4. Manually enter 1-2 test builds (e.g., Permafrost Marshal)
5. Test complex queries (e.g., "find all abilities used in Tank builds with Major Breach")

**Deliverables**:

* [ ] Meta layer tables deployed
* [ ] Sample builds entered and validated
* [ ] Query patterns documented

**Phase 3: API & Query Interface (Weeks 5-6)**

**Objective**: Build API layer for querying and manipulating build data.

**Tasks**:

1. Design RESTful API endpoints (GET /builds, POST /builds, GET /abilities, etc.)
2. Implement API using preferred framework (Node.js + Express, Python + Flask, etc.)
3. Add filtering, sorting, pagination
4. Implement search (full-text search on ability/item names)
5. Write API documentation (Swagger/OpenAPI spec)

**Deliverables**:

* [ ] API v1.0 deployed locally
* [ ] API documentation published
* [ ] Postman/Insomnia collection for testing

**Phase 4: Frontend Prototype (Weeks 7-8)**

**Objective**: Create basic web interface for browsing and creating builds.

**Tasks**:

1. Build simple frontend (React, Vue, or static HTML+JS)
2. Implement build browser (list, filter, search)
3. Implement build detail view (skills, gear, rotations displayed)
4. Implement build editor (drag-drop skills to bar slots)
5. Connect frontend to API

**Deliverables**:

* [ ] Web UI prototype deployed locally
* [ ] Build browser functional
* [ ] Build editor functional (create/edit builds)

**Phase 5: Addon Development (Weeks 9-12)**

**Objective**: Develop ESO Lua addon for in-game integration.

**Tasks**:

1. Design addon UI (in-game build viewer/switcher)
2. Implement Lua code for reading local build data
3. Implement skill bar application (auto-slot skills from saved build)
4. Test addon in-game
5. Package and document addon for distribution

**Deliverables**:

* [ ] ESO addon v1.0 functional in-game
* [ ] Addon published to ESOUI or GitHub
* [ ] Installation and usage guide

**Phase 6: Iteration & Polish (Ongoing)**

**Objective**: Refine based on testing and feedback.

**Tasks**:

* Add more builds to database
* Improve query performance (indexing, caching)
* Enhance UI/UX
* Add export/import features (build sharing)
* Integrate with ESO API updates (new patches)

**Technical Requirements**

**Database**

**Recommendation**: PostgreSQL 14+ or MySQL 8+

**Why**: Strong relational integrity, JSON column support, full-text search, mature tooling.

**Alternatives**: SQLite (for local/prototype), MongoDB (if preferring document model, but relational is better for this use case).

**API Framework**

**Options**:

* Node.js + Express (JavaScript/TypeScript)
* Python + Flask or FastAPI (Python)
* Ruby on Rails (Ruby)
* [ASP.NET](http://ASP.NET/) Core (C#)

**Recommendation**: Python + FastAPI (excellent type safety, auto-generated docs, fast development).

**Frontend**

**Options**:

* React (most popular, large ecosystem)
* Vue (simpler learning curve, good for smaller projects)
* Svelte (modern, minimal boilerplate)
* Static HTML + Vanilla JS (simplest, no build step)

**Recommendation**: Start with static HTML + vanilla JS for prototype; migrate to React if complexity grows.

**Addon Development**

**Language**: Lua (ESO's scripting language)

**Tools**:

* ESO Lua API documentation[web:263][web:271]
* ESOUI addon repository[web:272][web:283]
* Text editor with Lua support (VS Code + Lua extension)

**Resources**:

* UESP ESO API documentation[web:263]
* Community addon examples[web:271][web:276]
* ESO addon programming guides[web:284]

**Data Update Strategy**

**Patch Cycle Workflow**

When ESO releases a new patch:

1. **Extract updated data** using your Lua addon or UESP dumps
2. **Identify changes**: new abilities, item ID shifts, set bonus changes
3. **Update canonical tables**: INSERT new records, UPDATE changed records
4. **Validate builds**: check if any builds reference deprecated IDs
5. **Notify users**: flag builds that may need updates

**Automation Potential**

**Future enhancement**: Write scheduled script to:

* Fetch latest UESP API dump
* Diff against current database
* Auto-apply non-breaking changes
* Flag breaking changes for manual review

**Success Metrics**

**Phase 1-2 (Data Layer)**

* [ ] 100% of provided ESO data imported without errors
* [ ] All foreign key relationships valid
* [ ] Complex queries return results in <100ms

**Phase 3-4 (API & Frontend)**

* [ ] API handles 100+ requests/second without errors
* [ ] Frontend loads build list in <2 seconds
* [ ] Build editor allows creating complete build in <5 minutes

**Phase 5 (Addon)**

* [ ] Addon loads in-game without errors or lag
* [ ] Skill bar swapping works in <1 second
* [ ] No conflicts with other popular addons

**Risk Assessment**

**High Risk**

**Data staleness**: ESO patches can invalidate IDs or change ability mechanics.

**Mitigation**: Establish regular update cadence; version control data dumps; maintain patch history.

**Medium Risk**

**Schema changes**: As project evolves, schema may need refactoring.

**Mitigation**: Use database migration tools (Alembic, Flyway); version schema; test migrations on staging DB.

**Low Risk**

**Addon conflicts**: Other addons may use overlapping global variables.

**Mitigation**: Follow ESO addon best practices (namespace all globals, use LibStub for library management).

**Next Steps**

1. **You**: Complete data center validation phase
2. **You**: Extract and deliver initial ESO data dumps (abilities, items, sets, buffs) in JSON format
3. **Me**: Design detailed database schema (SQL scripts)
4. **Both**: Review schema together, iterate based on feedback
5. **Me**: Implement Phase 1 (canonical layer) and provide progress updates
6. **Iterate**: Continue through phases 2-6 with regular check-ins

**Appendix: Sample Queries**

**Query 1: Find all abilities that grant Major Breach**

SELECT a.abilityId, [a.name](http://a.name/), a.skillLine
FROM Abilities a
WHERE a.description LIKE '%Major Breach%';

**Query 2: List all builds using Pariah's Pinnacle set**

SELECT b.buildId, [b.name](http://b.name/), b.class
FROM Builds b
JOIN BuildGear bg ON b.buildId = bg.buildId
JOIN Sets s ON bg.setId = s.setId
WHERE [s.name](http://s.name/) = 'Pariah''s Pinnacle';

**Query 3: Show skill bar for a specific build**

SELECT bs.bar, bs.slot, [a.name](http://a.name/) AS abilityName, a.skillLine
FROM BuildSkills bs
JOIN Abilities a ON bs.abilityId = a.abilityId
WHERE bs.buildId = 1
ORDER BY bs.bar, bs.slot;

**Query 4: Find all Tank builds with speed > 30% bonus**

SELECT b.buildId, [b.name](http://b.name/), COUNT(DISTINCT bt.tagId) AS speedSources
FROM Builds b
JOIN BuildTags bt ON b.buildId = bt.buildId
JOIN Tags t ON bt.tagId = t.tagId
WHERE t.category = 'Speed'
GROUP BY b.buildId, [b.name](http://b.name/)
HAVING speedSources >= 2;

**References**

[1] UESP ESO API Documentation. (2025). ESO Data for API v101047. [https://esoapi.uesp.net](https://esoapi.uesp.net/)

[2] UESP ESO Log Project. (2020). GitHub repository for ESO data collection. <https://github.com/uesp/uesp-esolog>

[3] ESOUI Forums. (2024). ESO Lua API autocompletion resources. <https://www.esoui.com/downloads/info2654>

[4] LibSets. (2019). Library for ESO set data and item IDs. <https://esoui.com/downloads/info2241>

[5] ESO Data Dumper. (2015). Addon for exporting ESO data. <https://github.com/sevenseacat/eso_data_dumper>

I've created a comprehensive project specification document that outlines exactly what data you need to source, how to format it, and the full implementation roadmap. Key highlights:

**What you need to provide**:

* Abilities data (abilityId, name, description, skillLine, duration, cost, etc.) in JSON/CSV
* Items & Sets data (itemId, setId, bonuses, traits, etc.)
* Buffs & Debuffs data (effectId, Major/Minor classification, magnitude)

**How to provide it**:

* JSON preferred (handles nested structures like set bonuses)
* UTF-8 encoding
* Include ESO patch version and extraction timestamp
* Deliver via shared cloud link

**Architecture decision**: Official ESO IDs are parent keys at the canonical layer; all our custom build/rotation/tag data are children that reference those IDs via foreign keys.

The document includes sample data formats, SQL query examples, a phased roadmap (6 phases over ~12 weeks), and risk mitigation strategies. This is designed to start after your data center validation is complete.
