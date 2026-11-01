export interface SemanticWeldToe {
  id: string;
  plateThicknessMm: number;
  detailCategoryMpa: number;
  nominalStressRangeMpa: number;
}

export interface HotspotMeshMapping {
  weldToeToPoints: Map<string, number[]>;
  pointToWeld: Map<number, string>;
  crackToSegments: Map<string, number[]>;
}

export interface SurfaceStressNode {
  index: number;
  weldId: string;
  distFromToeMm: number;
  stressMpa: number;
}

export interface FatigueResult {
  nodes: SurfaceStressNode[];
  mapping: HotspotMeshMapping;
  hotspotStressMpa: number;
  nCyclesCapacity: number;
  damageD: number;
  finalCrackMm: number;
}
