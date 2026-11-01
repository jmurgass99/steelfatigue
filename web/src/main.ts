import van from "vanjs-core";
import { solveSteelFatigueWasm } from "./solver/wasmSolver.ts";
import { fetchSteelfatigueHealthApi } from "./solver/apiClient.ts";
import { createFatigueViewer3D } from "./viewer/getViewer3D.ts";
import { renderHotspotExtrapolationChart, renderDamageGaugeChart } from "./ui/getFatigueCharts.ts";

const { div, h2, h3, label, input, span, strong, canvas, button } = van.tags;

const nomStress = van.state(110);
const detailCat = van.state(90);
const thickness = van.state(25);
const cycles = van.state(450000);

const hsStressText = van.state("0.0 MPa");
const capCyclesText = van.state("0.0e+0");
const damageText = van.state("0.000");
const crackText = van.state("0.0 mm");
const apiStatus = van.state("Modo WASM local");

const viewerWrap = div({ class: "viewer-wrap" });
const hsCanvas = canvas({ class: "chart" });
const dmgCanvas = canvas({ class: "chart" });
const viewer = createFatigueViewer3D(viewerWrap);

async function recompute() {
  const res = await solveSteelFatigueWasm(
    nomStress.val,
    detailCat.val,
    thickness.val,
    cycles.val,
    10
  );
  hsStressText.val = `${res.hotspotStressMpa.toFixed(1)} MPa`;
  capCyclesText.val = res.nCyclesCapacity.toExponential(2);
  damageText.val = res.damageD.toFixed(3);
  crackText.val = `${res.finalCrackMm.toFixed(2)} mm`;
  viewer.update(res, thickness.val);
  renderHotspotExtrapolationChart(hsCanvas, res);
  renderDamageGaugeChart(dmgCanvas, res);
}

van.derive(() => {
  void recompute();
});

const app = div(
  { class: "layout" },
  div(
    { class: "panel" },
    h2("SteelFatigue 3D"),
    div(
      { class: "control-row" },
      label(() => `Rango de tensión nominal Δσ_nom = ${nomStress.val} MPa`),
      input({
        type: "range",
        min: "40",
        max: "220",
        step: "5",
        value: nomStress,
        oninput: (e: Event) => (nomStress.val = Number((e.target as HTMLInputElement).value)),
      })
    ),
    div(
      { class: "control-row" },
      label(() => `Categoría de detalle EN 1993-1-9 Δσ_c = ${detailCat.val} MPa`),
      input({
        type: "range",
        min: "36",
        max: "160",
        step: "5",
        value: detailCat,
        oninput: (e: Event) => (detailCat.val = Number((e.target as HTMLInputElement).value)),
      })
    ),
    div(
      { class: "control-row" },
      label(() => `Espesor de placa t = ${thickness.val} mm`),
      input({
        type: "range",
        min: "10",
        max: "50",
        step: "2",
        value: thickness,
        oninput: (e: Event) => (thickness.val = Number((e.target as HTMLInputElement).value)),
      })
    ),
    div(
      { class: "control-row" },
      label(() => `Ciclos aplicados N = ${cycles.val.toLocaleString()}`),
      input({
        type: "range",
        min: "50000",
        max: "2000000",
        step: "50000",
        value: cycles,
        oninput: (e: Event) => (cycles.val = Number((e.target as HTMLInputElement).value)),
      })
    ),
    div(
      { class: "kpi-grid" },
      div({ class: "kpi" }, span("Tensión Hot-Spot σ_hs"), strong(hsStressText)),
      div({ class: "kpi" }, span("Capacidad N_R"), strong(capCyclesText)),
      div({ class: "kpi" }, span("Daño Miner D"), strong(damageText)),
      div({ class: "kpi" }, span("Grieta final a_f"), strong(crackText))
    ),
    button(
      {
        onclick: async () => {
          const ok = await fetchSteelfatigueHealthApi("http://localhost:8000");
          apiStatus.val = ok ? "FastAPI sincronizado OK" : "FastAPI offline (usando WASM local)";
        },
      },
      "Sincronizar con FastAPI"
    ),
    span({ style: "font-size:0.75rem;color:#94a3b8" }, apiStatus)
  ),
  viewerWrap,
  div(
    { class: "panel" },
    h3("Extrapolación Hot-Spot IIW (t/2, 3t/2)"),
    hsCanvas,
    h3("Daño Acumulado y Propagación Paris"),
    dmgCanvas
  )
);

document.getElementById("app")?.appendChild(app);
