import type { HotspotMeshMapping, SemanticWeldToe, SurfaceStressNode } from "../data-model.ts";

export function getHotspotMesh(
  weld: SemanticWeldToe,
  pointsPerZone: number
): { nodes: SurfaceStressNode[]; mapping: HotspotMeshMapping } {
  const div = Math.max(2, Math.floor(pointsPerZone));
  const weldToeToPoints = new Map<string, number[]>();
  const pointToWeld = new Map<number, string>();
  const crackToSegments = new Map<string, number[]>();
  const nodes: SurfaceStressNode[] = [];

  const t = weld.plateThicknessMm;
  const indices: number[] = [];

  for (let i = 0; i < div; i++) {
    const idx = nodes.length;
    const d = 0.2 * t + (i / (div - 1)) * (2.2 * t);
    nodes.push({
      index: idx,
      weldId: weld.id,
      distFromToeMm: d,
      stressMpa: 0,
    });
    indices.push(idx);
    pointToWeld.set(idx, weld.id);
  }

  weldToeToPoints.set(weld.id, indices);
  crackToSegments.set("CRACK_PATH", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);

  return {
    nodes,
    mapping: { weldToeToPoints, pointToWeld, crackToSegments },
  };
}
