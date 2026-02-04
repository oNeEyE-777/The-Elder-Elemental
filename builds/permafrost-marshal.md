# Permafrost Marshal — Live Build Grid
Use this as the canonical grid; reproduce it in full at the bottom of every reply

Core class: Warden (Animal Companions)  
Subclasses: Necromancer (Grave Lord); Dragonknight (Draconic Power)  
CP total: 1804

## Objectives (condensed)

| Pillar | Target | Notes | — | — | S |
|---|---|---|---|---|:--:|
| Resist | 43k+ shown (buffed, in-combat), so you stay 33k+ after debuffs | Pass/fail identity for the build | — | — | 🔒 |
| Health | Max Health-focused | Health-first stat profile | — | — | 🔒 |
| Speed | Extreme speed | Choose fights; disengage on demand | — | — | 🔒 |
| HoTs | Multiple HoTs running | Sustain baseline is HoTs | — | — | 🔒 |
| Shield | 2 running in combat | Baseline survivability layer | — | — | 🔒 |
| Core | Deep Fissure + Unnerving Boneyard + Glacial Colossus | Core use of the build | — | — | 🔒 |

## 12 Skills (Front/Back)

| Bar | Slot | Skill | Duration(s) | Line | Effects (Named) | S |
|---|---:|---|---|---|---|:--:|
| Front | 1 | Deep Fissure | 9s | Animal Companions | On hit: (Major Breach) (Minor Breach) | 🔒 |
| Front | 2 | Unnerving Boneyard | 10s | Grave Lord | On hit: (Major Breach) (Minor Vulnerability) | 🔒 |
| Front | 3 | Hardened Armor | 20s / 6s | Draconic Power | On cast: (Major Resolve) | 🔒 |
| Front | 4 | Green Dragon Blood | 20s / 5s | Draconic Power | On cast: (Minor Vitality) (Major Fortitude) (Major Endurance) | 🔒 |
| Front | 5 | Blinding Flare | 5s | Support | Slotted: (Major Protection) | 🔒 |
| Front | ULT | Reviving Barrier | 30s / 15s | Support | — | 🔒 |
| . | . | . | . | . | . | . |
| Back | 1 | Ulfsild's Contingency | 22s | Mages Guild (Focus: Shield; Signature: Damage reduction; Affix: Minor Expedition) | On cast: (Minor Expedition) | 🔒 |
| Back | 2 | Resolving Vigor | 5s / 20s | Assault | On cast: (Minor Resolve) | 🔒 |
| Back | 3 | Bull Netch / Blue Betty | 25s | Animal Companions | On cast: (Major Brutality) (Major Sorcery) | 🔒 |
| Back | 4 | Wield Soul | 10s | Soul Magic (Focus: Healing; Signature: Sustain; Affix: Vitality) | On cast: (Major Vitality) (Magicka sustain) | 🔒 |
| Back | 5 | Blinding Flare | 5s | Support | Slotted: (Major Protection) | 🔒 |
| Back | ULT | Glacial Colossus | 3s / 12s | Grave Lord | On hit: (Major Vulnerability) | 🔒 |

## 12 Gear (all slots)

| Gear slot | Set | Weight | Trait | Enchant | Effects (Named) | S |
|---|---|---|---|---|---|:--:|
| Head | Nibenay (1pc) | Heavy | Reinforced | Max Magicka | — | 🔒 |
| Shoulder | Adept Rider | Heavy | Impenetrable | Max Magicka | Passive (always): (Major Expedition) (Major Gallop) | 🔒 |
| Chest | Adept Rider | Heavy | Reinforced | Max Magicka | Passive (always): (Major Expedition) (Major Gallop) | 🔒 |
| Hands | Adept Rider | Medium | Impenetrable | Max Magicka | Passive (always): (Major Expedition) (Major Gallop) | 🔒 |
| Waist | Adept Rider | Light | Impenetrable | Max Magicka | Passive (always): (Major Expedition) (Major Gallop) | 🔒 |
| Legs | Adept Rider | Heavy | Reinforced | Max Magicka | Passive (always): (Major Expedition) (Major Gallop) | 🔒 |
| Feet | Mark of the Pariah | Heavy | Impenetrable | Max Magicka | — | 🔒 |
| Neck | Mark of the Pariah | — | Swift | Magicka Recovery | — | 🔒 |
| Ring 1 | Mark of the Pariah | — | Swift | Magicka Recovery | — | 🔒 |
| Ring 2 (Mythic/Alt) | Ring of the Wild Hunt | — | Swift | Magicka Recovery | Passive (always): (+15% Movement Speed IN) (+45% Movement Speed OUT) | 🔒 |
| Front weapon | Mark of the Pariah (Ice staff) | — | Defending | Absorb Magicka | — | 🔒 |
| Back weapon | Mark of the Pariah (Ice staff) | — | Defending | Absorb Magicka | — | 🔒 |

## Attributes

| Stat | Points | Unbuffed Total | Buffed Total | S |
|---|---:|---:|---:|:--:|
| Health | 64 |   |   | 🔒 |
| Magicka | 0 |   |   | 🔒 |
| Stamina | 0 |   |   | 🔒 |

## CP stars (slotted only)

| Tree | Slot 1 | Slot 2 | Slot 3 | Slot 4 | S |
|---|---|---|---|---|:--:|
| Warfare | Ironclad | Duelist's Rebuff | Bulwark | Resilience | 🔒 |
| Fitness | Celerity | Pain's Refuge | Sustained by Suffering | Bastion | 🔒 |
| Craft | Steed's Blessing | War Mount | Gifted Rider | Sustaining Shadows | 🔒 |

## Speed sources

| Source ID | Adept Rider | Wild Hunt | Celerity | Steed’s Blessing | Ulfsild | Swift (all jewelry) | Total | S |
|---|---|---|---|---|---|---|---|:--:|
| In-combat % | +30 | +15 | +10 | 0 | +15 | +19 | +89 | 🔒 |
| Out-of-combat % | +30 | +45 | +10 | +20 | +15 | +19 | +139 | 🔒 |

---

## Internal IDs (for tooling)

These tables are for scripts; they don’t need to be shown in any UI.

### Skill IDs

| Bar | Slot | Skill | skill_id |
|---|---:|---|---|
| Front | 1 | Deep Fissure | skill.deep_fissure |
| Front | 2 | Unnerving Boneyard | skill.unnerving_boneyard |
| Front | 3 | Hardened Armor | skill.hardened_armor |
| Front | 4 | Green Dragon Blood | skill.green_dragon_blood |
| Front | 5 | Blinding Flare | skill.blinding_flare |
| Front | ULT | Reviving Barrier | skill.reviving_barrier |
| Back | 1 | Ulfsild's Contingency | skill.ulfsilds_contingency |
| Back | 2 | Resolving Vigor | skill.resolving_vigor |
| Back | 3 | Bull Netch / Blue Betty | skill.bull_netch |
| Back | 4 | Wield Soul | skill.wield_soul |
| Back | 5 | Blinding Flare | skill.blinding_flare_back |
| Back | ULT | Glacial Colossus | skill.glacial_colossus |

### Gear set IDs

| Gear slot | Set | set_id |
|---|---|---|
| Head | Nibenay (1pc) | set.nibenay_bay_battlereeve |
| Shoulder | Adept Rider | set.adept_rider |
| Chest | Adept Rider | set.adept_rider |
| Hands | Adept Rider | set.adept_rider |
| Waist | Adept Rider | set.adept_rider |
| Legs | Adept Rider | set.adept_rider |
| Feet | Mark of the Pariah | set.mark_of_the_pariah |
| Neck | Mark of the Pariah | set.mark_of_the_pariah |
| Ring 1 | Mark of the Pariah | set.mark_of_the_pariah |
| Ring 2 (Mythic/Alt) | Ring of the Wild Hunt | set.ring_of_the_wild_hunt |
| Front weapon | Mark of the Pariah (Ice staff) | set.mark_of_the_pariah |
| Back weapon | Mark of the Pariah (Ice staff) | set.mark_of_the_pariah |

### CP star IDs

| Tree | Slot | Name | cp_id |
|---|---|---|---|
| Warfare | 1 | Ironclad | cp.ironclad |
| Warfare | 2 | Duelist's Rebuff | cp.duelists_rebuff |
| Warfare | 3 | Bulwark | cp.bulwark |
| Warfare | 4 | Resilience | cp.resilience |
| Fitness | 1 | Celerity | cp.celerity |
| Fitness | 2 | Pain's Refuge | cp.pains_refuge |
| Fitness | 3 | Sustained by Suffering | cp.sustained_by_suffering |
| Fitness | 4 | Bastion | cp.bastion |
| Craft | 1 | Steed's Blessing | cp.steeds_blessing |
| Craft | 2 | War Mount | cp.war_mount |
| Craft | 3 | Gifted Rider | cp.gifted_rider |
| Craft | 4 | Sustaining Shadows | cp.sustaining_shadows |
