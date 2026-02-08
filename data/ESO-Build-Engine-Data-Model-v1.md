# ESO Build Engine – v1 Data Model (Single‑Build Engine) **docs/ESO-Build-Engine-Data-Model-v1.md**

## Goal

Define the minimal but general JSON schemas needed to represent the **Permafrost Marshal** build as if it were part of a full ESO database.​

We use five core JSON files for v1:

* data/skills.json
* data/effects.json
* data/sets.json
* data/cp-stars.json
* builds/permafrost-marshal.json

Each file is small for now (only entries used by this build) but uses schemas that can scale to full‑game coverage.

## 1. Skills (data/skills.json)

json

{

"skills": [

{

"id": "skill.deep\_fissure",

"name": "Deep Fissure",

"class\_id": "warden",

"skill\_line\_id": "warden\_animal\_companions",

"type": "active", // "active" | "ultimate" | "passive"

"resource": "magicka", // "magicka" | "stamina" | "ultimate" | "none"

"cost": 2700, // or null

"cast\_time": "instant", // "instant" | "cast" | "channeled"

"target": "area", // "self" | "enemy" | "area" | "ally" | "group"

"duration\_seconds": 9, // or null

"radius\_meters": 20, // or null

"ability\_id": null, // ESO abilityId (from ESOUI/UESP), optional

"external\_ids": { // optional external mappings

"uesp": null

},

"tooltip\_effect\_text": "Short, human-readable effect description.",

"effects": [

{

"effect\_id": "debuff.major\_breach",

"timing": "on\_hit", // "on\_cast" | "on\_hit" | "slotted" | "while\_active" | "proc"

"duration\_seconds": 10, // or null

"target": "enemy", // "self" | "ally" | "enemy" | "area" | "group"

"notes": "Applied to enemies hit by the fissure."

},

{

"effect\_id": "debuff.minor\_breach",

"timing": "on\_hit",

"duration\_seconds": 10,

"target": "enemy",

"notes": "Applied alongside Major Breach."

}

]

}

// 11 more skills for Permafrost Marshal

]

}

**Key principles:**

* Skills never hard‑code buff numbers; they reference effects.id via effect\_id.
* All tooltip and machine‑readable fields live here; builds only store skill\_id per slot.​
* External fields (ability\_id, external\_ids) are optional metadata and never primary keys.

## 2. Effects (data/effects.json)

json

{

"effects": [

{

"id": "buff.major\_resolve",

"name": "Major Resolve",

"category": "buff", // "buff" | "debuff"

"scope": "self", // "self" | "target" | "group" | "area"

"stat": "resist", // e.g. "resist", "damage\_taken", "healing\_received", "movement\_speed"

"type": "major", // "major" | "minor" | "base" | "unique"

"value": 5948, // flat or fractional (e.g. 0.10 for +10% damage taken)

"stacks\_with": [], // effect IDs that can stack; usually [] for Major/Minor

"description": "Increases Physical and Spell Resistance by 5948."

}

// More effects for: Minor Resolve, Major/Minor Breach, Major/Minor Vulnerability, Major Protection,

// speed buffs (Adept Rider, Wild Hunt, Celerity, etc.), Pariah scaling, HoTs, shields, etc.

]

}

**Key principles:**

* All Major/Minor and named buffs/debuffs live here once.
* Skills, sets, and CP stars only refer to effects.id via effect\_id.
* All math (values, stacking rules) is centralized in this file.

## 3. Sets (data/sets.json)

json

{

"sets": [

{

"id": "set.adept\_rider",

"name": "Adept Rider",

"type": "armor", // "armor" | "jewelry" | "weapon" | "mythic"

"source": "crafted", // e.g. "crafted" | "overland" | "dungeon" | "arena" | "mythic"

"tags": ["pvp", "speed"],

"set\_id": null, // external numeric setId (e.g. from eso-sets-api), optional

"external\_ids": {

"eso\_sets\_api": null

},

"bonuses": [

{

"pieces": 2,

"tooltip\_raw": "Minor effect description or placeholder.",

"effects": []

},

{

"pieces": 3,

"tooltip\_raw": "Movement speed bonuses.",

"effects": [

"buff.adept\_rider\_speed\_in\_combat",

"buff.adept\_rider\_speed\_out\_of\_combat",

"buff.major\_gallop" // if you choose to track Gallop separately

]

}

]

}

// set.mark\_of\_the\_pariah, set.nibenay, set.ring\_of\_the\_wild\_hunt, etc.

]

}

**Key principles:**

* Sets define bonuses per piece count via **effect IDs**, not inline math.
* External set IDs (e.g. set\_id, external\_ids) are optional and never used as primary keys.​
* Build gear records reference set.id only (e.g. "set\_id": "set.adept\_rider").

## 4. CP stars (data/cp-stars.json)

json

{

"cp\_stars": [

{

"id": "cp.ironclad",

"name": "Ironclad",

"tree": "warfare", // "warfare" | "fitness" | "craft"

"slot\_type": "slottable", // "slottable" | "passive"

"tooltip\_raw": "Reduces damage taken from direct damage attacks.",

"effects": [

"buff.damage\_taken\_direct\_minor"

]

}

// 11 more stars used in Permafrost Marshal

]

}

**Key principles:**

* CP stars are just IDs + metadata + lists of effect\_ids.
* Only stars with slot\_type: "slottable" may appear in build.cp\_slotted.​

## 5. Build record (builds/permafrost-marshal.json)

json

{

"id": "build.permafrost\_marshal",

"name": "Permafrost Marshal",

"class\_core": "warden",

"subclasses": ["necromancer", "dragonknight"],

"cp\_total": 1804,

"role\_tags": ["pvp", "tank", "high\_speed"],

"attributes": {

"health": 64,

"magicka": 0,

"stamina": 0

},

"pillars": {

"resist": { "target\_resist\_shown": 43000 },

"health": { "focus": "health\_first" },

"speed": { "profile": "extreme\_speed" },

"hots": { "min\_active\_hots": 2 },

"shield": { "min\_active\_shields": 2 },

"core\_combo": {

"skills": [

"skill.deep\_fissure",

"skill.unnerving\_boneyard",

"skill.glacial\_colossus"

]

}

},

"bars": {

"front": [

{ "slot": 1, "skill\_id": "skill.deep\_fissure" },

{ "slot": 2, "skill\_id": "skill.unnerving\_boneyard" },

{ "slot": 3, "skill\_id": "skill.hardened\_armor" },

{ "slot": 4, "skill\_id": "skill.green\_dragon\_blood" },

{ "slot": 5, "skill\_id": "skill.blinding\_flare\_front" },

{ "slot": "ULT", "skill\_id": "skill.reviving\_barrier" }

],

"back": [

{ "slot": 1, "skill\_id": "skill.ulfsilds\_contingency" },

{ "slot": 2, "skill\_id": "skill.resolving\_vigor" },

{ "slot": 3, "skill\_id": "skill.bull\_netch" },

{ "slot": 4, "skill\_id": "skill.wield\_soul" },

{ "slot": 5, "skill\_id": "skill.soul\_burst" },

{ "slot": "ULT", "skill\_id": "skill.glacial\_colossus" }

]

},

"gear": [

{ "slot": "head", "set\_id": "set.nibenay", "weight": "heavy", "trait": "reinforced", "enchant": "glyph.max\_magicka" },

{ "slot": "shoulder", "set\_id": "set.adept\_rider", "weight": "heavy", "trait": "impenetrable", "enchant": "glyph.max\_magicka" },

{ "slot": "chest", "set\_id": "set.mark\_of\_the\_pariah", "weight": "heavy", "trait": "reinforced", "enchant": "glyph.max\_magicka" },

{ "slot": "hands", "set\_id": "set.adept\_rider", "weight": "medium", "trait": "impenetrable", "enchant": "glyph.max\_magicka" },

{ "slot": "waist", "set\_id": "set.adept\_rider", "weight": "light", "trait": "impenetrable", "enchant": "glyph.max\_magicka" },

{ "slot": "legs", "set\_id": "set.adept\_rider", "weight": "heavy", "trait": "impenetrable", "enchant": "glyph.max\_magicka" },

{ "slot": "feet", "set\_id": "set.adept\_rider", "weight": "heavy", "trait": "impenetrable", "enchant": "glyph.max\_magicka" },

{ "slot": "neck", "set\_id": "set.mark\_of\_the\_pariah", "weight": null, "trait": "swift", "enchant": "glyph.magicka\_recovery" },

{ "slot": "ring1", "set\_id": "set.mark\_of\_the\_pariah", "weight": null, "trait": "swift", "enchant": "glyph.magicka\_recovery" },

{ "slot": "ring2", "set\_id": "set.ring\_of\_the\_wild\_hunt", "weight": null, "trait": "swift", "enchant": "glyph.magicka\_recovery" },

{ "slot": "front\_weapon", "set\_id": "set.mark\_of\_the\_pariah", "weight": null, "trait": "defending", "enchant": "glyph.absorb\_magicka" },

{ "slot": "back\_weapon", "set\_id": "set.mark\_of\_the\_pariah", "weight": null, "trait": "defending", "enchant": "glyph.absorb\_magicka" }

],

"cp\_slotted": {

"warfare": [

"cp.ironclad",

"cp.duelists\_rebuff",

"cp.bulwark",

"cp.resilience"

],

"fitness": [

"cp.celerity",

"cp.pains\_refuge",

"cp.sustained\_by\_suffering",

"cp.gifted\_rider"

],

"craft": [

"cp.steeds\_blessing",

"cp.war\_mount",

null,

null

]

}

}

**Key principles:**

* The build record stores only IDs and numeric configuration, never tooltip text or buff math.​
* Bars, gear, and CP layout follow the global rules in the Global Rules doc.
* Pillars are structured targets and constraints; actual pass/fail is computed by validators using data/\*.json and effect math.​

This data model is deliberately minimal for a single build, but the shapes are designed to scale to a full ESO database without structural changes.
