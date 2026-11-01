import type { FatigueResult } from "../data-model.ts";

export function renderHotspotExtrapolationChart(canvas: HTMLCanvasElement, res: FatigueResult): void {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  const w = (canvas.width = canvas.clientWidth || 360);
  const h = (canvas.height = canvas.clientHeight || 205);
  ctx.clearRect(0, 0, w, h);

  ctx.strokeStyle = "rgba(148,163,184,0.25)";
  ctx.strokeRect(36, 16, w - 52, h - 38);

  const maxDist = Math.max(...res.nodes.map((n) => n.distFromToeMm), 1);
  const maxS = Math.max(res.hotspotStressMpa, ...res.nodes.map((n) => n.stressMpa), 10);

  ctx.strokeStyle = "#38bdf8";
  ctx.lineWidth = 2.2;
  ctx.beginPath();
  res.nodes.forEach((n, idx) => {
    const x = 36 + (n.distFromToeMm / maxDist) * (w - 56);
    const y = h - 22 - (n.stressMpa / maxS) * (h - 42);
    if (idx === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // Punto hot-spot extrapolado al pie del cordón (dist = 0)
  const yHs = h - 22 - (res.hotspotStressMpa / maxS) * (h - 42);
  ctx.fillStyle = "#f43f5e";
  ctx.beginPath();
  ctx.arc(36, yHs, 4.5, 0, 2 * Math.PI);
  ctx.fill();

  ctx.fillStyle = "#e2e8f0";
  ctx.font = "11px Inter, sans-serif";
  ctx.fillText(`Extrapolación IIW — σ_hs = ${res.hotspotStressMpa.toFixed(1)} MPa`, 42, 30);
}

export function renderDamageGaugeChart(canvas: HTMLCanvasElement, res: FatigueResult): void {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  const w = (canvas.width = canvas.clientWidth || 360);
  const h = (canvas.height = canvas.clientHeight || 205);
  ctx.clearRect(0, 0, w, h);

  ctx.strokeStyle = "rgba(148,163,184,0.25)";
  ctx.strokeRect(36, 16, w - 52, h - 38);

  const dRatio = Math.min(1.5, res.damageD);
  const bw = (Math.min(1.0, dRatio) / 1.0) * (w - 72);

  ctx.fillStyle = dRatio >= 1.0 ? "#ef4444" : "#10b981";
  ctx.fillRect(40, 60, bw, 32);

  ctx.strokeStyle = "rgba(255,255,255,0.4)";
  ctx.strokeRect(40, 60, w - 72, 32);

  ctx.fillStyle = "#e2e8f0";
  ctx.font = "11px Inter, sans-serif";
  ctx.fillText(`Daño acumulado de Miner D = ${res.damageD.toFixed(3)}`, 42, 45);
  ctx.fillText(`Vida N_R: ${res.nCyclesCapacity.toExponential(2)} ciclos`, 42, 125);
  ctx.fillText(`Tamaño final de grieta a_f: ${res.finalCrackMm.toFixed(2)} mm`, 42, 145);
}
