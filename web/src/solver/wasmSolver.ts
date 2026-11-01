import type { FatigueResult, SemanticWeldToe } from "../data-model.ts";
import { getHotspotMesh } from "../mesh/getMesh.ts";

// Binario WebAssembly compilado desde fatigueKernel.cpp
const WASM_B64 =
  "AGFzbQEAAAABDgJgAnx8AXxgA3x8fAF8AwMCAAEFAwEAAQcjAg5zbkN5Y2xlc1Nsb3BlMwAADnBhcmlzQ3JhY2tTdGVwAAEKKgIdAEQAAAAAgIQ+QSAAIAGjIAAgAaOiIAAgAaOiogsKACAAIAGiIAKiCw==";

function decodeBase64(b64: string): Uint8Array {
  if (typeof Buffer !== "undefined") {
    return new Uint8Array(Buffer.from(b64, "base64"));
  }
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

export interface FatigueWasmExports {
  snCyclesSlope3: (deltaSigmaC: number, deltaSigma: number) => number;
  parisCrackStep: (cVal: number, deltaKCubed: number, dN: number) => number;
}

let cachedExports: FatigueWasmExports | null = null;

export async function initFatigueWasm(): Promise<FatigueWasmExports> {
  if (cachedExports) return cachedExports;
  const { instance } = await WebAssembly.instantiate(decodeBase64(WASM_B64));
  cachedExports = instance.exports as unknown as FatigueWasmExports;
  return cachedExports;
}

export async function solveSteelFatigueWasm(
  nominalStressRangeMpa: number,
  detailCategoryMpa: number,
  plateThicknessMm: number,
  appliedCycles: number,
  pointsPerZone: number
): Promise<FatigueResult> {
  const wasm = await initFatigueWasm();
  const weld: SemanticWeldToe = {
    id: "WELD-TOE-1",
    plateThicknessMm,
    detailCategoryMpa,
    nominalStressRangeMpa,
  };
  const { nodes, mapping } = getHotspotMesh(weld, pointsPerZone);
  const t = plateThicknessMm;

  function stressAt(dist: number): number {
    const norm = Math.max(dist / t, 0.03);
    return nominalStressRangeMpa * (1.0 + 0.65 / Math.sqrt(norm));
  }

  for (const n of nodes) {
    n.stressMpa = stressAt(n.distFromToeMm);
  }

  // IIW tipo "a" extrapolación lineal: σ_hs = 1.67*σ(0.5t) - 0.67*σ(1.5t)
  const sHalf = stressAt(0.5 * t);
  const sThreeHalf = stressAt(1.5 * t);
  const hotspotStressMpa = 1.67 * sHalf - 0.67 * sThreeHalf;

  const nCyclesCapacity = wasm.snCyclesSlope3(detailCategoryMpa, hotspotStressMpa);
  const damageD = appliedCycles / Math.max(nCyclesCapacity, 1.0);

  // Ley de Paris paso a paso
  const cParis = 3.0e-13;
  let aCurr = 1.2;
  const dN = appliedCycles / 10;
  for (let i = 0; i < 10; i++) {
    const deltaK = 1.12 * hotspotStressMpa * Math.sqrt(Math.PI * aCurr);
    const dK3 = Math.pow(deltaK, 3.0);
    const da = wasm.parisCrackStep(cParis, dK3, dN);
    aCurr += Math.min(da, 5.0);
  }

  return {
    nodes,
    mapping,
    hotspotStressMpa,
    nCyclesCapacity,
    damageD,
    finalCrackMm: aCurr,
  };
}
