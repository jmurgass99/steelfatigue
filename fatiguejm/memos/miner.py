"""
Memoria de cálculo handcalcs — daño acumulado de Palmgren-Miner por
bloques de espectro de tensiones (EN 1993-1-9).

Produce LaTeX/Markdown paso-a-paso del cálculo:

    D = Σ_i n_i / N_i ≤ 1.0

donde N_i = N_c · (Δσ_c / Δσ_i)^m con m=3 para N < 5·10⁶ y m=5 para
5·10⁶ ≤ N ≤ 10⁸ (curva bilineal EN 1993-1-9).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    from handcalcs.decorator import handcalc
    _HAS_HANDCALCS = True
except ImportError:  # pragma: no cover
    _HAS_HANDCALCS = False

    def handcalc(*args, **kwargs):
        def deco(f):
            return f
        return deco


@dataclass(frozen=True)
class MinerMemoInput:
    detail_category: float        # Δσ_C [MPa]
    gamma_mf: float = 1.35        # factor parcial fatiga
    spectrum: list[dict[str, float]] = field(default_factory=list)
    # cada bloque: {"label": str, "stress_range_MPa": float, "cycles": float}


@dataclass(frozen=True)
class BlockBreakdown:
    label: str
    stress_range_MPa: float
    cycles: float
    N_endurance: float
    damage: float


@dataclass(frozen=True)
class MinerMemoResult:
    total_damage: float
    pass_check: bool
    blocks: list[BlockBreakdown]
    latex: str
    markdown: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_damage": self.total_damage,
            "pass_check": self.pass_check,
            "blocks": [
                {"label": b.label, "stress_range_MPa": b.stress_range_MPa,
                 "cycles": b.cycles, "N_endurance": b.N_endurance,
                 "damage": b.damage}
                for b in self.blocks
            ],
        }


def _n_endurance(delta_sigma: float, delta_sigma_c_d: float) -> float:
    """N a partir de Δσ_i (curva bilineal EN 1993-1-9)."""
    if delta_sigma <= 0:
        return float("inf")
    # Tramo m=3 para N ≤ 5e6
    Nc = 2.0e6
    N = Nc * (delta_sigma_c_d / delta_sigma) ** 3
    if N > 5e6:
        # Cambio a m=5 — refinar usando límite a 5e6
        delta_sigma_D = (Nc / 5e6) ** (1.0 / 3.0) * delta_sigma_c_d
        N = 5e6 * (delta_sigma_D / delta_sigma) ** 5
    return N


def render_miner_memo(data: MinerMemoInput) -> MinerMemoResult:
    """Genera la memoria. Devuelve resultado + LaTeX + Markdown."""
    delta_sigma_c_d = data.detail_category / data.gamma_mf

    blocks: list[BlockBreakdown] = []
    total_D = 0.0
    md_rows: list[str] = []
    for blk in data.spectrum:
        label = str(blk.get("label", "?"))
        ds = float(blk["stress_range_MPa"])
        n = float(blk["cycles"])
        N = _n_endurance(ds, delta_sigma_c_d)
        d = n / N if N > 0 else 0.0
        blocks.append(BlockBreakdown(label=label, stress_range_MPa=ds,
                                      cycles=n, N_endurance=N, damage=d))
        total_D += d
        md_rows.append(
            f"| {label} | {ds:.1f} | {n:.2e} | {N:.2e} | {d:.4f} |"
        )

    md = (
        "# Memoria — Daño acumulado Palmgren-Miner (EN 1993-1-9)\n\n"
        f"**Categoría de detalle:** Δσ_C = {data.detail_category:.1f} MPa\n"
        f"**Factor parcial:** γ_Mf = {data.gamma_mf:.2f}\n"
        f"**Resistencia de diseño:** Δσ_C,d = "
        f"{delta_sigma_c_d:.1f} MPa\n\n"
        "## Espectro de tensiones\n\n"
        "| Bloque | Δσ [MPa] | n_i | N_i | D_i |\n"
        "|---|---|---|---|---|\n"
        + "\n".join(md_rows) +
        f"\n\n**Daño total:** D = {total_D:.3f}\n"
        f"**Verificación:** D ≤ 1.0 → "
        f"{'✅ PASS' if total_D <= 1.0 else '❌ FAIL'}\n"
    )

    latex = (
        r"\Delta\sigma_{C,d} = \frac{\Delta\sigma_C}{\gamma_{Mf}} = "
        rf"\frac{{{data.detail_category:.1f}}}{{{data.gamma_mf:.2f}}}"
        rf" = {delta_sigma_c_d:.1f}\;\text{{MPa}}\\"
        r"D = \sum_i \frac{n_i}{N_i} = "
        rf"{total_D:.4f}"
    )

    return MinerMemoResult(
        total_damage=total_D, pass_check=total_D <= 1.0,
        blocks=blocks, latex=latex, markdown=md,
    )


__all__ = ["MinerMemoInput", "MinerMemoResult", "BlockBreakdown",
           "render_miner_memo"]
