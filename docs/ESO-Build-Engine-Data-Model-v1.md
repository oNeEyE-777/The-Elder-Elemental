\# ESO Build Engine – v1 Data Model (Single‑Build Engine) \*\*docs/ESO-Build-Engine-Data-Model-v1.md\*\*



\## Goal



Define the minimal but general JSON schemas needed to represent the \*\*Permafrost Marshal\*\* build as if it were part of a full ESO database.\[file:2]\[file:1]



We use five core JSON files for v1:\[file:2]\[file:4]



\- `data/skills.json`

\- `data/effects.json`

\- `data/sets.json`

\- `data/cp-stars.json`

\- `builds/permafrost-marshal.json`



Each file is small for now (only entries used by this build) but uses schemas that can scale to full‑game coverage.\[file:2]



---



\## 1. Skills (data/skills.json)



```json

{

&nbsp; "skills": \[

&nbsp;   {

&nbsp;     "id": "skill.deep\_fissure",

&nbsp;     "name": "Deep Fissure",

&nbsp;     "class\_id": "warden",

&nbsp;     "skill\_line\_id": "warden\_animal\_companions",



&nbsp;     "type": "active",          // "active" | "ultimate" | "passive"

&nbsp;     "resource": "magicka",     // "magicka" | "stamina" | "ultimate" | "none"

&nbsp;     "cost": 2700,              // or null



&nbsp;     "cast\_time": "instant",    // "instant" | "cast" | "channeled"

&nbsp;     "target": "area",          // "self" | "enemy" | "area" | "ally" | "group"

&nbsp;     "duration\_seconds": 9,     // or null

&nbsp;     "radius\_meters": 20,       // or null



&nbsp;     "ability\_id": null,        // ESO abilityId (from ESOUI/UESP), optional

&nbsp;     "external\_ids": {          // optional external mappings

&nbsp;       "uesp": null

&nbsp;     },



&nbsp;     "tooltip\_effect\_text": "Short, human-readable effect description.",



&nbsp;     "effects": \[

&nbsp;       {

&nbsp;         "effect\_id": "debuff.major\_breach",

&nbsp;         "timing": "on\_hit",    // "on\_cast" | "on\_hit" | "slotted" | "while\_active" | "proc"

&nbsp;         "duration\_seconds": 10, // or null

&nbsp;         "target": "enemy",     // "self" | "ally" | "enemy" | "area" | "group"

&nbsp;         "notes": "Applied to enemies hit by the fissure."

&nbsp;       },

&nbsp;       {

&nbsp;         "effect\_id": "debuff.minor\_breach",

&nbsp;         "timing": "on\_hit",

&nbsp;         "duration\_seconds": 10,

&nbsp;         "target": "enemy",

&nbsp;         "notes": "Applied alongside Major Breach."

&nbsp;       }

&nbsp;     ]

&nbsp;   }



&nbsp;   // 11 more skills for Permafrost Marshal

&nbsp; ]

}



