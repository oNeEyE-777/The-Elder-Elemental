export interface BuildPillars {
  resist: {
    targetresistshown: number;
  };
  health: {
    focus: string;
  };
  speed: {
    profile: string;
  };
  hots: {
    minactivehots: number;
  };
  shield: {
    minactiveshields: number;
  };
  corecombo: {
    skills: string[];
  };
}

export interface BuildAttributes {
  health: number;
  magicka: number;
  stamina: number;
}

export interface BuildPermafrost {
  id: string;
  name: string;
  classcore: string;
  subclasses: string[];
  cptotal: number;
  roletags: string[];
  attributes: BuildAttributes;
  pillars: BuildPillars;
}
