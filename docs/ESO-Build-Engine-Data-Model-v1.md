# ESO Build Engine – v1 Data Model (Single‑Build Engine)
**docs/ESO-Build-Engine-Data-Model-v1.md**

## Goal

Define the minimal but general JSON schemas needed to represent the **Permafrost Marshal** build using canonical ESO data files under `data/`, with build configuration stored under `builds/`.

We use five core JSON files for v1:

- `data/skills.json`
- `data/effects.json`
- `data/sets.json`
- `data/cp-stars.json`
- `builds/permafrost-marshal.json`

Each file is small for now (only entries used by this build) but uses schemas intended to scale to broader coverage without structural changes.

---

## ID naming convention

All primary IDs are internal, stable keys used for cross‑references between JSON files.

Rules:

- IDs are lowercase.
- Words are separated with underscores.
- IDs use a domain prefix and dot namespace.

Domains used in v1:

- Skills: `skill.*` (example: `skill.deep_fissure`)
- Effects: `buff.*`, `debuff.*`, `shield.*`, `hot.*` (examples: `buff.major_resolve`, `debuff.major_breach`, `shield.hardened_armor`, `hot.green_dragon_blood`)
- Sets: `set.*` (example: `set.mark_of_the_pariah`)
- CP stars: `cp.*` (example: `cp.ironclad`)
- Builds: `build.*` (example: `build.permafrost_marshal`)

External numeric IDs from ESO or third‑party sources are stored in explicit fields (such as `ability_id`, `set_id`, or `external_ids`) and are not used as primary keys.

---

## Skills (data/skills.json)

### Schema

Top-level object:

- `skills`: array of skill objects

Skill object:

- `id`: string, `skill.*`
- `name`: string (human-facing)
- `class_id`: string (example values used: `warden`, `necromancer`, `dragonknight`, `templar`, `universal`)
- `skill_line_id`: string (example values used: `warden_animal_companions`, `necromancer_grave_lord`, `dragonknight_draconic_power`, `support`, `alliance_war_support`, `alliance_war_assault`, `item_set_proc`, `soul_magic`)
- `type`: string (values used: `active`, `ultimate`, `passive`)
- `resource`: string (values used: `magicka`, `stamina`, `ultimate`, `none`)
- `cost`: number or null
- `cast_time`: string (values used: `instant`)
- `target`: string (values used: `area`, `self`, `enemy`, `group`)
- `duration_seconds`: number or null
- `radius_meters`: number or null
- `ability_id`: number or null
- `external_ids`: object
  - `uesp`: string or null
- `tooltip_effect_text`: string
- `effects`: array of effect application objects

Effect application object (within a skill’s `effects` array):

- `effect_id`: string (effect ID without extra namespacing; examples: `buff.major_resolve`, `debuff.major_breach`)
- `timing`: string (values used: `onhit`, `whileactive`)
- `duration_seconds`: number or null
- `target`: string (values used: `self`, `enemy`)
- `notes`: string

### JSON example (matches live structure)

```json
{
  "skills": [
    {
      "id": "skill.deep_fissure",
      "name": "Deep Fissure",
      "class_id": "warden",
      "skill_line_id": "warden_animal_companions",
      "type": "active",
      "resource": "magicka",
      "cost": 2700,
      "cast_time": "instant",
      "target": "area",
      "duration_seconds": 9,
      "radius_meters": 20,
      "ability_id": null,
      "external_ids": {
        "uesp": null
      },
      "tooltip_effect_text": "Unleash a fissure that opens after a short delay, applying Major and Minor Breach to enemies hit.",
      "effects": [
        {
          "effect_id": "debuff.major_breach",
          "timing": "onhit",
          "duration_seconds": 10,
          "target": "enemy",
          "notes": "Applied to enemies hit by the fissure."
        },
        {
          "effect_id": "debuff.minor_breach",
          "timing": "onhit",
          "duration_seconds": 10,
          "target": "enemy",
          "notes": "Applied alongside Major Breach."
        }
      ]
    }
  ]
}
```

---

## Effects (data/effects.json)

### Schema (must match file exactly)

Top-level object:

- `effects`: array of effect objects

Effect object fields (exact keys):

- `id`: string (examples include `buff.major_resolve`, `debuff.major_breach`, `shield.hardened_armor`, `hot.green_dragon_blood`)
- `name`: string (human-facing)
- `category`: string (values used: `modifier`, `shield`, `over_time`)
- `scope`: string (values used: `self`, `target`, `group`, `self_area`)
- `stat`: string (values used include `resistance_flat`, `damage_taken_scalar`, `movement_speed_scalar`, `movement_speed_out_of_combat_scalar`, `mounted_speed_scalar`, `healing_over_time_scalar`, `shield_scalar_max_health`, `shield_scalar_max_resource`, `resource_gain_scalar`)
- `magnitude_kind`: string (values used: `flat`, `multiplier_additive`, `scaling_function`)
- `magnitude_value`: number
- `stacking_rule`: string (values used: `exclusive_tier`, `unique_source`)
- `stacks_with`: array of effect ID strings
- `description`: string

### JSON example (matches live structure)

```json
{
  "effects": [
    {
      "id": "buff.major_resolve",
      "name": "Major Resolve",
      "category": "modifier",
      "scope": "self",
      "stat": "resistance_flat",
      "magnitude_kind": "flat",
      "magnitude_value": 5948,
      "stacking_rule": "exclusive_tier",
      "stacks_with": [],
      "description": "Increases Physical and Spell Resistance by 5948."
    },
    {
      "id": "debuff.major_breach",
      "name": "Major Breach",
      "category": "modifier",
      "scope": "target",
      "stat": "resistance_flat",
      "magnitude_kind": "flat",
      "magnitude_value": -5948,
      "stacking_rule": "exclusive_tier",
      "stacks_with": [],
      "description": "Reduces Physical and Spell Resistance by 5948."
    },
    {
      "id": "shield.hardened_armor",
      "name": "Hardened Armor Shield",
      "category": "shield",
      "scope": "self",
      "stat": "shield_scalar_max_health",
      "magnitude_kind": "scaling_function",
      "magnitude_value": 1.0,
      "stacking_rule": "unique_source",
      "stacks_with": [],
      "description": "Applies a damage shield scaling with max health."
    },
    {
      "id": "hot.green_dragon_blood",
      "name": "Green Dragon Blood HoT",
      "category": "over_time",
      "scope": "self",
      "stat": "healing_over_time_scalar",
      "magnitude_kind": "scaling_function",
      "magnitude_value": 1.0,
      "stacking_rule": "unique_source",
      "stacks_with": [],
      "description": "Self heal over time and recovery bonuses."
    }
  ]
}
```

---

## Sets (data/sets.json)

### Schema

Top-level object:

- `sets`: array of set objects

Set object:

- `id`: string, `set.*`
- `name`: string (human-facing)
- `type`: string (values used: `armor`, `mythic`)
- `source`: string (values used: `crafted`, `overland`, `mythic`)
- `tags`: array of strings
- `set_id`: number or null (external numeric ID placeholder)
- `external_ids`: object
  - `eso_sets_api`: string or null
- `bonuses`: array of bonus tier objects

Bonus tier object:

- `pieces`: number
- `tooltip_raw`: string
- `effects`: array of effect IDs as strings (note: effect IDs in sets use the same ID strings as `effects[].id`, such as `buff.wild_hunt_speed`)

### JSON example (matches live structure)

```json
{
  "sets": [
    {
      "id": "set.ring_of_the_wild_hunt",
      "name": "Ring of the Wild Hunt",
      "type": "mythic",
      "source": "mythic",
      "tags": [
        "pvp",
        "speed",
        "mythic"
      ],
      "set_id": null,
      "external_ids": {
        "eso_sets_api": null
      },
      "bonuses": [
        {
          "pieces": 1,
          "tooltip_raw": "Mythic movement speed bonus from Ring of the Wild Hunt (placeholder).",
          "effects": [
            "buff.wild_hunt_speed"
          ]
        }
      ]
    }
  ]
}
```

---

## CP stars (data/cp-stars.json)

### Schema

Top-level object:

- `cp_stars`: array of CP star objects

CP star object:

- `id`: string, `cp.*`
- `name`: string (human-facing)
- `tree`: string (values used: `warfare`, `fitness`, `craft`)
- `slot_type`: string (value used: `slottable`)
- `tooltip_raw`: string
- `effects`: array of effect IDs as strings (may be empty)

### JSON example (matches live structure)

```json
{
  "cp_stars": [
    {
      "id": "cp.ironclad",
      "name": "Ironclad",
      "tree": "warfare",
      "slot_type": "slottable",
      "tooltip_raw": "Reduces damage taken from direct damage attacks.",
      "effects": [
        "buff.damage_taken_direct_minor"
      ]
    }
  ]
}
```

---

## Build record (builds/permafrost-marshal.json)

### Schema

Top-level build object:

- `id`: string, `build.*`
- `name`: string (human-facing)
- `class_core`: string
- `subclasses`: array of strings
- `cp_total`: number
- `role_tags`: array of strings
- `attributes`: object
  - `health`: number
  - `magicka`: number
  - `stamina`: number
- `pillars`: object (build goals/targets; values are structured and build-specific)
  - `resist`: object
    - `target_resist_shown`: number
  - `health`: object
    - `focus`: string
  - `speed`: object
    - `profile`: string
  - `hots`: object
    - `min_active_hots`: number
  - `shield`: object
    - `min_active_shields`: number
  - `core_combo`: object
    - `skills`: array of `skill.*` IDs
- `bars`: object
  - `front`: array of bar slot objects
  - `back`: array of bar slot objects

Bar slot object:

- `slot`: number 1–5 or the string "ULT"
- `skillid`: string, `skill.*` (must exist in `data/skills.json`)

- `gear`: array of gear item objects

Gear item object:

- `slot`: string (values used include `head`, `shoulder`, `chest`, `hands`, `waist`, `legs`, `feet`, `neck`, `ring1`, `ring2`, `front_weapon`, `back_weapon`)
- `setid`: string, `set.*` (must exist in `data/sets.json`)
- `weight`: string or null (values used: `heavy`, `medium`, `light`, or null for jewelry/weapons)
- `trait`: string
- `enchant`: string

- `cpslotted`: object keyed by CP tree
  - `warfare`: array of 4 entries, each `cp.*` or null
  - `fitness`: array of 4 entries, each `cp.*` or null
  - `craft`: array of 4 entries, each `cp.*` or null

### JSON example (matches live structure)

```json
{
  "id": "build.permafrost_marshal",
  "name": "Permafrost Marshal",
  "class_core": "warden",
  "subclasses": ["necromancer", "dragonknight"],
  "cp_total": 1804,
  "role_tags": ["pvp", "tank", "high_speed"],
  "attributes": {
    "health": 64,
    "magicka": 0,
    "stamina": 0
  },
  "pillars": {
    "resist": { "target_resist_shown": 43000 },
    "health": { "focus": "health_first" },
    "speed": { "profile": "extreme_speed" },
    "hots": { "min_active_hots": 2 },
    "shield": { "min_active_shields": 2 },
    "core_combo": {
      "skills": [
        "skill.deep_fissure",
        "skill.unnerving_boneyard",
        "skill.glacial_colossus"
      ]
    }
  },
  "bars": {
    "front": [
      { "slot": 1, "skillid": "skill.deep_fissure" },
      { "slot": 2, "skillid": "skill.unnerving_boneyard" },
      { "slot": 3, "skillid": "skill.hardened_armor" },
      { "slot": 4, "skillid": "skill.green_dragon_blood" },
      { "slot": 5, "skillid": "skill.blinding_flare_front" },
      { "slot": "ULT", "skillid": "skill.reviving_barrier" }
    ],
    "back": [
      { "slot": 1, "skillid": "skill.ulfsilds_contingency" },
      { "slot": 2, "skillid": "skill.resolving_vigor" },
      { "slot": 3, "skillid": "skill.bull_netch" },
      { "slot": 4, "skillid": "skill.wield_soul" },
      { "slot": 5, "skillid": "skill.soul_burst" },
      { "slot": "ULT", "skillid": "skill.glacial_colossus" }
    ]
  },
  "gear": [
    {
      "slot": "head",
      "setid": "set.nibenay",
      "weight": "heavy",
      "trait": "reinforced",
      "enchant": "glyph.max_magicka"
    },
    {
      "slot": "ring2",
      "setid": "set.ring_of_the_wild_hunt",
      "weight": null,
      "trait": "swift",
      "enchant": "glyph.magicka_recovery"
    },
    {
      "slot": "back_weapon",
      "setid": "set.mark_of_the_pariah",
      "weight": null,
      "trait": "defending",
      "enchant": "glyph.absorb_magicka"
    }
  ],
  "cpslotted": {
    "warfare": [
      "cp.ironclad",
      "cp.duelists_rebuff",
      "cp.bulwark",
      "cp.resilience"
    ],
    "fitness": [
      "cp.celerity",
      "cp.pains_refuge",
      "cp.sustained_by_suffering",
      "cp.gifted_rider"
    ],
    "craft": [
      "cp.steeds_blessing",
      "cp.war_mount",
      null,
      null
    ]
  }
}
```

---

## Appendix A: Skills Import Mapping → `data/skills.json`

This appendix defines how external ESO skill data (for example, UESP or ESOUI exports) is normalized into the canonical `data/skills.json` schema used by the ESO Build Engine. [file:375][file:456]

The import pipeline must treat external data as **authoritative** for IDs and raw text only, while all mechanical math and stacking rules live in `data/effects.json` and Python tools, never inferred from tooltips. [file:375][file:459]

### A.1 External skill concepts

For any ESO-aligned source (UESP tables, ESOUI dumps, etc.), the importer assumes the following conceptual fields exist for each skill: [file:375][file:456]

- `abilityId`  
  - ESO’s numeric ability identifier (for example, 86112).  
- `internalName`  
  - Engine-facing or editor-facing name (for example, `Deep Fissure`, `Unnerving Boneyard`).  
- `classTag`  
  - ESO class association if any (for example, Warden, Necromancer, Dragonknight, Templar, or “none” for universal skills like Barrier or Resolving Vigor).  
- `skillLineTag`  
  - ESO skill line (for example, Warden: Animal Companions, Necromancer: Gravelord, Dragonknight: Draconic Power, Alliance War: Support, Alliance War: Assault, Soul Magic, or item/monster set proc lines).  
- `mechanicType`  
  - Resource mechanic used by the skill (Magicka, Stamina, Ultimate, or none for passives).  
- `baseCost`  
  - Nominal cost at a reference rank, expressed in ESO’s integer resource units.  
- `castTimeType`  
  - Casting behavior (instant, cast-time, channel, or passive).  
- `targetType`  
  - Primary targeting category (self, enemy, area, group, ally), matching how the skill is aimed in-game.  
- `baseDurationSeconds`  
  - Duration for persistent effects such as buffs, debuffs, damage-over-time, or ground effects, if applicable; otherwise null or zero.  
- `radiusMeters`  
  - Effective radius or ground area size, if applicable; otherwise null.  
- `isUltimate` / `isPassive` flags  
  - Booleans or similar markers indicating whether the skill is an ultimate or passive.  
- `rawTooltipText`  
  - Unformatted or minimally formatted tooltip text as presented in-game, including numbers and ESO-specific labels (Major/Minor, etc.).  
- `sourceTag`  
  - Origin of the record (for example, `uesp:2025Q4-snapshot`, `eso-ui-extract:patch-10.1`).  

If a particular upstream dataset uses different column names, the importer must map them onto these conceptual fields before normalizing into `data/skills.json`. [file:456]

### A.2 Canonical target fields in `data/skills.json`

The canonical skill schema is defined in the main Skills section of this document. [file:375] For imports, the following fields must be populated from external concepts, with any additional logic explicitly encoded in import tools under `tools/`. [file:439][file:456]

For each skill object in `data/skills.json`:

- `id` (string, `skill.`-prefixed, internal)  
  - Constructed internal ID in the form `skill.<normalized_name>`, where `<normalized_name>` is lowercase, snake_case, ESO-agnostic, and unique within the skills domain (for example, `skill.deep_fissure`, `skill.unnerving_boneyard`). [file:375]  
  - The importer must not use `abilityId` as this primary key; it may use `abilityId` and `internalName` as inputs to deterministic ID generation. [file:375][file:456]

- `name` (string, human-facing)  
  - Populated directly from `internalName` (for example, `Deep Fissure`).  
  - Minor normalization is allowed (trimming whitespace), but spelling and capitalization should follow ESO/UESP conventions. [file:375]

- `classid` (string)  
  - Mapped from `classTag`, normalized to lowercase, snake_case class identifiers already used in v1 (for example, `warden`, `necromancer`, `dragonknight`, `templar`, `universal`). [file:375]  
  - For skills that are not class-bound (for example, Barrier, Resolving Vigor), the importer must use `universal`. [file:375]

- `skilllineid` (string)  
  - Mapped from `skillLineTag`, normalized to lowercase, snake_case identifiers matching existing examples (for example, `warden_animal_companions`, `necromancer_gravelord`, `dragonknight_draconic_power`, `alliance_war_support`, `alliance_war_assault`, `item_set_proc`, `soul_magic`). [file:375]  
  - The mapping from ESO’s localized skill line names to these stable IDs must be implemented and maintained in Python under `tools/`, not inferred at runtime in the UI. [file:439][file:456]

- `type` (string: `active`, `ultimate`, `passive`)  
  - Derived from `isUltimate` / `isPassive` and ESO’s classification.  
  - Rules: if `isUltimate` is true, set `type: "ultimate"`; else if `isPassive` is true, set `type: "passive"`; otherwise set `type: "active"`. [file:375]

- `resource` (string: `magicka`, `stamina`, `ultimate`, `none`)  
  - Mapped from `mechanicType`, normalized into the v1 enumeration. [file:375]  
  - For ultimates, `resource` must be `ultimate` regardless of whether the source labels them as using Magicka or Stamina. [file:375]  
  - For purely passive skills with no cost, `resource` must be `none`. [file:375]

- `cost` (number or null)  
  - Populated from `baseCost` for active and ultimate skills, using the base cost at the build’s reference rank (or ESO’s max rank).  
  - Set to `null` for passives or costless mechanics. [file:375]

- `casttime` (string)  
  - Derived from `castTimeType`, normalized into the v1 values (for example, `instant`, `cast`, `channeled`, or a minimal set that the Data Model recognizes). [file:375]  
  - If external data uses numeric cast times, the importer should still choose a discrete cast type category rather than writing raw milliseconds into this field.

- `target` (string: `area`, `self`, `enemy`, `group`, `ally`)  
  - Mapped from `targetType` into the simplified v1 categories. [file:375]  
  - If ESO distinguishes multiple complex targeting modes, the importer may choose the closest canonical category, but should not introduce new enum values without updating this document first. [file:439]

- `durationseconds` (number or null)  
  - Populated from `baseDurationSeconds` for time-limited skills (for example, ground DoTs, HoTs, shields that last a fixed period).  
  - For instantaneous effects without duration (for example, burst damage or one-time debuff application), set to `null`. [file:375]

- `radiusmeters` (number or null)  
  - Populated from `radiusMeters` when a circular or spherical area is defined.  
  - For non-area skills, set to `null`. [file:375]

- `abilityid` (number or null)  
  - Populated directly from `abilityId` as provided by ESO/UESP. [file:375][file:456]  
  - This is an external reference only and must not be used as the primary JSON key.

- `externalids` (object)  
  - `uesp` (string or null) populated from a source-specific identifier such as UESP’s internal ability key or row ID, when present. [file:456]  
  - Additional external namespaces may be added later (for example, `eso_db`, `addon_id`) but must be documented here before use. [file:439]

- `tooltipeffecttext` (string)  
  - Populated from `rawTooltipText`, potentially normalized to strip markup while preserving ESO terms and numeric values (for example, “Unleash a fissure that opens after a short delay, applying Major and Minor Breach to enemies hit.”). [file:375]  
  - This field is **display** and context only; no math is derived from it. [file:375][file:459]

- `effects` (array of effect application objects)  
  - The importer **does not parse tooltips** to create new effects. Instead, it attaches effect references using curated mappings or explicit configuration under `tools/` or separate mapping JSONs. [file:375][file:459]  
  - Each element must follow the schema from the main Skills section:  
    - `effectid` (string) referencing an existing ID in `data/effects.json` (for example, `debuff.majorbreach`, `buff.majorresolve`). [file:375]  
    - `timing` (string) such as `onhit`, `oncast`, `whileactive`, `slotted`, `proc`, defined in Global Rules. [file:459]  
    - `durationseconds` (number or null) for this application instance; may match or differ from the skill’s top-level `durationseconds` when mechanics warrant it. [file:375]  
    - `target` (string) using the same categories as `effects.json` (for example, `self`, `enemy`, `group`, `area`). [file:375][file:462]  
    - `notes` (string) free-text explanation of how the effect is applied (for example, “Applied to enemies hit by the fissure.”). [file:375]

### A.3 Importer responsibilities and constraints

To keep the data center stable and patch-aligned, the skill import pipeline must follow these constraints: [file:439][file:456]

- All schema rules in this document are authoritative.  
  - If an external source requires new fields or enum values, update this document first, then adjust import tools and JSON. [file:375][file:439]
- No tooltip parsing for math.  
  - All numeric magnitudes, stacking rules, and mechanical semantics live in `data/effects.json` and Python tools, not inferred from `tooltipeffecttext`. [file:375][file:459]
- Deterministic ID generation.  
  - Given the same external skill record and ID-generation strategy, the importer must always produce the same `id` and `skilllineid` values, so builds and tools remain stable across imports. [file:375][file:456]
- Patch-aligned snapshots only.  
  - Import runs must work from frozen external snapshots (for example, `uesp:patch-XX.YY`) so that `data/skills.json` represents a coherent game patch, not a moving target. [file:456]

With this appendix in place, `data/skills.json` can be treated as the single canonical skill source for all builds, while import tools handle external ESO/UESP alignment without leaking schema or ID instability into the rest of the engine. [file:375][file:439]

---

## Appendix B: Sets Import Mapping → `data/sets.json`

This appendix defines how external ESO set data (for example, UESP SetItem tables) is normalized into the canonical `data/sets.json` schema used by the ESO Build Engine. [file:474][file:456]

The import pipeline must treat external data as authoritative for IDs, names, and raw bonus text, while all mechanical math lives in `data/effects.json` and Python tools, never inferred from set tooltips. [file:456][file:459]

### B.1 External set concepts

For any ESO-aligned source (UESP exports, ESO client-derived tables), the importer assumes the following conceptual fields exist for each set: [file:456]

- `setId`  
  - ESO’s numeric set identifier (for example, 404 for Mark of the Pariah).
- `setName`  
  - Human-facing set name (for example, `Mark of the Pariah`, `Ring of the Wild Hunt`).
- `setType`  
  - Broad type classification (armor set, weapon/jewelry set, mythic item, etc.).
- `setSource`  
  - Acquisition source (crafted, overland, dungeon, trial, arena, mythic, etc.).
- `setTags`  
  - Optional tags describing use cases (PvP, PvE, tank, speed, mythic).
- `bonusRows`  
  - Collection of bonus rows, each including:
  - `piecesRequired`: number of items required for the bonus.
  - `bonusTooltipRaw`: raw description text for the bonus.
  - `bonusEffectIdentifiers` (optional): any UESP/ESO identifiers that distinguish individual effects within the bonus, if present.

If the upstream dataset uses different column names, the importer must map them onto these concepts before normalizing into `data/sets.json`. [file:456]

### B.2 Canonical target fields in `data/sets.json`

The canonical set schema is defined in the main Sets section of this document. [file:474] For imports, the following fields must be populated from external concepts, with any additional logic explicitly encoded in import tools under `tools/`. [file:456]

For each set object in `data/sets.json`:

- `id` (string, `set.`-prefixed, internal)  
  - Constructed internal ID in the form `set.<normalized_name>`, where `<normalized_name>` is lowercase, snake_case, ESO-agnostic, and unique within the sets domain (for example, `set.mark_of_the_pariah`, `set.ring_of_the_wild_hunt`). [file:474]  
  - The importer must not use `setId` as this primary key; it may use `setId` and `setName` as inputs to deterministic ID generation. [file:456]

- `name` (string, human-facing)  
  - Populated directly from `setName` with minimal normalization (trim whitespace, preserve casing conventions). [file:474]

- `type` (string; values such as `armor`, `mythic`)  
  - Derived from `setType`, mapped into the v1 enumeration. [file:474]  
  - For mythic items, `type` must be `mythic` even if the source labels them as jewelry or mixed. [file:474]

- `source` (string; values such as `crafted`, `overland`, `mythic`)  
  - Mapped from `setSource` into normalized source categories used in v1. [file:474]  
  - If more granular categories are required later (for example, `dungeon`, `trial`), they must be added to this document before appearing in JSON. [file:456]

- `tags` (array of strings)  
  - Populated from `setTags` and/or derived from manual curation for roles (for example, `pvp`, `tank`, `speed`, `mythic`). [file:474]  
  - Tags are descriptive only and have no math semantics.

- `set_id` (number or null)  
  - Populated directly from ESO’s numeric `setId`. [file:474][file:456]  
  - This is an external reference only and must not be used as the primary JSON key.

- `external_ids` (object)  
  - `eso_sets_api` (string or null) populated from a UESP or ESO Sets API identifier, such as a canonical set key, when available. [file:474][file:456]  
  - Additional external namespaces must be documented here before use.

- `bonuses` (array of bonus tier objects)  
  - Each bonus tier corresponds to one entry in `bonusRows`. [file:474]

Bonus tier object fields:

- `pieces` (number)  
  - Populated from `piecesRequired`. [file:474]

- `tooltip_raw` (string)  
  - Populated from `bonusTooltipRaw`, preserving ESO wording and key terms as much as practical. [file:474]  
  - This field is descriptive only; no math is derived from it.

- `effects` (array of effect IDs as strings)  
  - The importer does not parse `tooltip_raw` to invent new effects. Instead, it attaches effect IDs from `data/effects.json` using curated mappings or explicit configuration under `tools/` or mapping JSONs. [file:474][file:459]  
  - Each entry must exactly match an `effects.id` value (for example, `buff.wild_hunt_speed`, `buff.pariah_resist_scaling`). [file:474][file:456]

### B.3 Importer responsibilities and constraints

To keep set data stable and patch-aligned, the set import pipeline must follow these constraints: [file:456]

- All schema rules in this document are authoritative.  
  - If external data requires new fields or enum values (for example, new set types), update this document first, then adjust import tools and JSON. [file:474][file:456]

- No tooltip parsing for math.  
  - All numeric magnitudes and stacking behavior for set bonuses live in `data/effects.json` and Python tools, not inferred from `tooltip_raw`. [file:474][file:459]

- Deterministic ID generation.  
  - Given the same upstream `setId` and `setName`, the importer must always produce the same `id` value so builds and tools remain stable across imports. [file:456]

- Patch-aligned snapshots only.  
  - Import runs must operate on frozen UESP snapshots for a specific ESO API version so that `data/sets.json` represents a coherent patch state. [file:456]

With this appendix in place, `data/sets.json` can be treated as the single canonical set source for gear configuration in `builds/*.json`, while import tools handle external ESO/UESP alignment. [file:474][file:456]

---

## Appendix C: CP Stars Import Mapping → `data/cp-stars.json`

This appendix defines how external ESO Champion Point star data is normalized into the canonical `data/cp-stars.json` schema. [file:474][file:456]

The import pipeline must treat external data as authoritative for IDs, names, tree membership, and raw tooltips, while all mechanical math is centralized in `data/effects.json` and Python tools. [file:456][file:459]

### C.1 External CP star concepts

For any ESO-aligned source (UESP CP tables or equivalent), the importer assumes the following conceptual fields exist for each CP star: [file:456]

- `cpId`  
  - ESO’s numeric or internal identifier for the CP star.
- `cpName`  
  - Human-facing name (for example, `Ironclad`, `Duelist's Rebuff`, `Steed's Blessing`).
- `cpTree`  
  - CP tree classification (Warfare, Fitness, Craft).
- `slotType`  
  - Whether the star is slottable or passive (for v1, we primarily use `slottable`). [file:474]
- `cpTooltipRaw`  
  - Raw tooltip text describing the star’s effect.
- `cpTags` (optional)  
  - Tags describing star type or role (defense, offense, mitigation, utility, movement, mount).
- `cpEffectIdentifiers` (optional)  
  - Any identifiers that distinguish the numeric effect attached to the star, if available.

If the upstream dataset labels trees or stars differently, the importer must map them onto these conceptual fields before normalizing into `data/cp-stars.json`. [file:456]

### C.2 Canonical target fields in `data/cp-stars.json`

The canonical CP star schema is defined in the main CP stars section of this document. [file:474] For imports, the following fields must be populated from external concepts, with logic encoded in import tools under `tools/`. [file:456]

For each CP star object in `data/cp-stars.json`:

- `id` (string, `cp.`-prefixed, internal)  
  - Constructed internal ID in the form `cp.<normalized_name>`, where `<normalized_name>` is lowercase, snake_case, ESO-agnostic, and unique within the CP domain (for example, `cp.ironclad`, `cp.duelists_rebuff`, `cp.steeds_blessing`). [file:474]  
  - The importer must not use `cpId` as this primary key; it may use `cpId` and `cpName` as inputs to deterministic ID generation. [file:456]

- `name` (string, human-facing)  
  - Populated directly from `cpName` with minimal normalization. [file:474]

- `tree` (string: `warfare`, `fitness`, `craft`)  
  - Mapped from `cpTree`, normalized into the v1 enumeration. [file:474]  
  - If future ESO updates add new trees, they must be added to this document before use.

- `slot_type` (string; typically `slottable`)  
  - Mapped from `slotType`, normalized to values used in v1. [file:474]  
  - Non-slottable stars may be supported later but must be documented here first.

- `tooltip_raw` (string)  
  - Populated from `cpTooltipRaw`, preserving ESO phrasing and numeric values as much as practical. [file:474]  
  - This field is descriptive only; numeric behavior is modeled via effects. [file:459]

- `effects` (array of effect IDs as strings)  
  - The importer does not parse `tooltip_raw` to generate math. Instead, it attaches references to effects already defined in `data/effects.json` using curated mappings or explicit configuration under `tools/` or mapping JSONs. [file:474][file:459]  
  - Each entry must exactly match an `effects.id` value (for example, `buff.damage_taken_direct_minor`, `buff.movement_speed_mount_minor`). [file:474]

- `external_ids` (optional object, if added later)  
  - If needed, may store `uesp_cp_id` or similar numeric keys to enable round-tripping to UESP or ESO sources; any such fields must be added to this document before appearing in JSON. [file:456]

### C.3 Importer responsibilities and constraints

To keep CP star data stable and patch-aligned, the CP import pipeline must follow these constraints: [file:456]

- All schema rules in this document are authoritative.  
  - If external data requires new fields (for example, non-slottable stars with different shapes), update this document first, then adjust import tools and JSON. [file:474][file:456]

- No tooltip parsing for math.  
  - All numeric magnitudes and stacking behavior for CP stars live in `data/effects.json` and Python tools, not inferred from `tooltip_raw`. [file:474][file:459]

- Deterministic ID generation.  
  - Given the same upstream `cpId` and `cpName`, the importer must always produce the same `id` value so builds and tools remain stable across imports. [file:456]

- Patch-aligned snapshots only.  
  - Import runs must operate on frozen UESP CP snapshots for a specific ESO API version so that `data/cp-stars.json` represents a coherent patch state. [file:456]

With this appendix in place, `data/cp-stars.json` can be treated as the single canonical CP star source for all builds, while import tools handle external ESO/UESP alignment without introducing schema or ID instability. [file:474][file:456]




