import assert from "node:assert/strict";
import { solveSteelFatigueWasm } from "../solver/wasmSolver.ts";

const res4 = await solveSteelFatigueWasm(110, 90, 25, 450000, 4);
const res10 = await solveSteelFatigueWasm(110, 90, 25, 450000, 10);

assert.equal(res4.nodes.length, 4);
assert.equal(res10.nodes.length, 10);
assert.ok(res10.hotspotStressMpa > 110);
assert.ok(res10.nCyclesCapacity > 0);
assert.ok(res10.finalCrackMm > 1.2);
console.log(
  `SteelFatigue WASM test OK: sigma_hs=${res10.hotspotStressMpa.toFixed(1)} MPa, N_cap=${res10.nCyclesCapacity.toExponential(2)}, D=${res10.damageD.toFixed(3)}`
);
