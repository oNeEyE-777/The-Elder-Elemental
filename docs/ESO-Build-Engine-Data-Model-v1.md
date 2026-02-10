# ESO Build Engine – v1 Data Model (Single-Build Engine)
**docs/ESO-Build-Engine-Data-Model-v1.md**

## Goal

Define the minimal but general JSON schemas needed to represent the **Permafrost Marshal** build as if it were part of a full ESO database. [file:15]

We use five core JSON files for v1: [file:15]

- `data/skills.json`
- `data/effects.json`
- `data/sets.json`
- `data/cp-stars.json`
- `builds/permafrost-marshal.json`

Each file is small for now (only entries used by this build) but uses schemas that can scale to full-game coverage. [file:15]

---

## ID naming convention

All core entities (skills, effects, sets, CP stars, etc.) use a consistent, machine-friendly ID scheme: [file:15]

- All IDs are lowercase.
- Words are separated with underscores.
- A short type prefix is used to distinguish domains:
  - Skills: `skill.<name>` (for example, `skill.deep_fissure`).
  - Sets: `set.<name>` (for example, `set.adept_rider`, `set.mark_of_the_pariah`).
  - CP stars: `cp.<name>` (for example, `cp.duelists_rebuff`, `cp.steeds_blessing`).
  - Effects: `buff.<name>` / `debuff.<name>` (for example, `buff.major_resolve`, `debuff.major_breach`). [file:15]

These IDs are internal keys only. ESO’s numeric ability IDs or external set IDs are stored separately in `ability_id` or `external_ids` fields and are never used as primary keys. [file:15]

---

## 1. Skills (data/skills.json)

```json
{
  "skills": [
    {
      "id": "skill.deep_fissure",
      "name": "Deep Fissure",
      "class_id": "warden",
      "skill_line_id": "warden_animal_companions",

      "type": "active",          // "active" | "ultimate" | "passive"
      "resource": "magicka",     // "magicka" | "stamina" | "ultimate" | "none"
      "cost": 2700,              // or null

      "cast_time": "instant",    // "instant" | "cast" | "channeled"
      "target": "area",          // "self" | "enemy" | "area" | "ally" | "group"
      "duration_seconds": 9,     // or null
      "radius_meters": 20,       // or null

      "ability_id": null,        // ESO abilityId (from ESOUI/UESP), optional
      "external_ids": {          // optional external mappings
        "uesp": null
      },

      "tooltip_effect_text": "Short, human-readable effect description.",

      "effects": [
        {
          "effect_id": "debuff.major_breach",
          "timing": "onhit",           // "oncast" | "onhit" | "slotted" | "whileactive" | "proc"
          "duration_seconds": 10,      // or null
          "target": "enemy",           // "self" | "ally" | "enemy" | "area" | "group"
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

    // 11 more skills for Permafrost Marshal
  ]
}
