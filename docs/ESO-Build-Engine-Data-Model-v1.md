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
