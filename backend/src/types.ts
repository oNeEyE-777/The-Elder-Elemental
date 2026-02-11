// Minimal TypeScript types aligned with docs/ESO-Build-Engine-Data-Model-v1.md
// These will be extended as we expose more fields via the API.

export interface EffectRef {
  effect_id: string;
  timing: string;
  target: string;
  duration_seconds?: number | null;
}

export interface Skill {
  id: string;
  name: string;
  line: string;
  role: string;
  cost_type: string;
  tooltip: string;
  effects: EffectRef[];
}

export interface Effect {
  id: string;
  name: string;
  stat: string;
  type: string;
  magnitude: number;
  unit: string;
  stacks_with?: string[] | null;
  description: string;
}

export interface SetBonusEffectRef {
  effect_id: string;
}

export interface SetBonus {
  pieces: number;
  effects: SetBonusEffectRef[];
}

export interface SetItem {
  id: string;
  name: string;
  type: string;
  mythic: boolean;
  bonuses: SetBonus[];
}

export interface CpEffectRef {
  effect_id: string;
}

export interface CpStar {
  id: string;
  tree: string;
  name: string;
  slot_type: string;
  tooltip: string;
  effects: CpEffectRef[];
}

// Permafrost Marshal build – minimal shape used for backend wiring.
// This mirrors the v1 schema but only includes fields needed immediately.
export interface BuildBarSlot {
  slot: string;
  skill_id: string | null;
}

export interface BuildBars {
  front: BuildBarSlot[];
  back: BuildBarSlot[];
}

export interface BuildGearItem {
  slot: string;
  set_id: string | null;
  weight?: string | null;
}

export interface BuildCpTreeSlots {
  slotted: Array<string | null>;
}

export interface BuildCpSlotted {
  warfare: BuildCpTreeSlots;
  fitness: BuildCpTreeSlots;
  craft: BuildCpTreeSlots;
}

export interface Build {
  id: string;
  name: string;
  class: string;
  role: string;
  bars: BuildBars;
  gear: BuildGearItem[];
  cp_slotted: BuildCpSlotted;
}