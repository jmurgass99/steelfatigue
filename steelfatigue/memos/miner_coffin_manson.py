"""
Memoria de calculo handcalcs -- dano acumulado combinado
HCF (Palmgren-Miner) + LCF (Coffin-Manson).

Produce LaTeX/Markdown paso-a-paso del calculo unificado:

    D_total = D_HCF + D_LCF

donde:
    D_HCF = Sigma_i (n_i / N_i)          (Palmgren-Miner, EN 1993-1-9)
    epsilon_a = sigma_f'/E * (2Nf)^b      (Basquin, termino elastico)
                + epsilon_f' * (2Nf)^c    (Coffin-Manson, termino plastico)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

from .miner import MinerMemoInput, MinerMemoResult, render_miner_memo


# ------------------------------------------------------------------
# Inputs
# ------------------------------------------------------------------

@dataclass(frozen=True)
class CoffinMansonMemoInput:
    """Parametros del modelo Basquin + Coffin-Manson completo.

    Args:
        sigma_f: coeficiente de resistencia a fatiga sigma_f' [MPa].
        b: exponente de resistencia a fatiga (Basquin), tipicamente -0.06 a -0.14.
        eps_f: coeficiente de ductilidad a fatiga epsilon_f' (adimensional).
        c: exponente de ductilidad a fatiga, tipicamente -0.5 a -0.7.
        E: modulo de Young [MPa].
        strain_amplitudes: secuencia de amplitudes de deformacion total
            (epsilon_a) para cada semi-ciclo o ciclo contado.
    """
    sigma_f: float = 900.0          # MPa, tipico A992
    b: float = -0.10
    eps_f: float = 0.30
    c: float = -0.60
    E: float = 200_000.0            # MPa
    strain_amplitudes: list[float] = field(default_factory=list)


# ------------------------------------------------------------------
# Results
# ------------------------------------------------------------------

@dataclass(frozen=True)
class LCFCycleBreakdown:
    """Desglose por ciclo LCF."""
    cycle_index: int
    strain_amplitude: float
    N_f: float
    damage: float


@dataclass(frozen=True)
class CombinedFatigueMemoResult:
    """Resultado de la memoria combinada HCF + LCF."""
    D_HCF: float
    D_LCF: float
    D_total: float
    pass_check: bool
    hcf_result: MinerMemoResult | None
    lcf_cycles: list[LCFCycleBreakdown]
    latex: str
    markdown: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "D_HCF": self.D_HCF,
            "D_LCF": self.D_LCF,
            "D_total": self.D_total,
            "pass_check": self.pass_check,
            "hcf_result": self.hcf_result.to_dict() if self.hcf_result else None,
            "lcf_cycles": [
                {
                    "cycle_index": c.cycle_index,
                    "strain_amplitude": c.strain_amplitude,
                    "N_f": c.N_f,
                    "damage": c.damage,
                }
                for c in self.lcf_cycles
            ],
        }


# ------------------------------------------------------------------
# LCF helpers
# ------------------------------------------------------------------

def _nf_coffin_manson(
    strain_amp: float,
    sigma_f: float,
    b: float,
    eps_f: float,
    c: float,
    E: float,
) -> float:
    """Resuelve N_f desde la ecuacion de Basquin + Coffin-Manson.

        epsilon_a = (sigma_f'/E)*(2*N_f)^b + epsilon_f'*(2*N_f)^c

    Se resuelve numericamente mediante busqueda de biseccion,
    dado que la funcion es monotona decreciente en N_f.
    """
    if strain_amp <= 0:
        return float("inf")

    def residual(log_nf: float) -> float:
        nf = 10.0 ** log_nf
        two_nf = 2.0 * nf
        eps_calc = (sigma_f / E) * two_nf ** b + eps_f * two_nf ** c
        return eps_calc - strain_amp

    # Bisection in log10(N_f) space, from 0.1 to 1e12
    lo, hi = -1.0, 12.0
    if residual(lo) < 0:
        # strain is above the curve even at N_f=0.1 -> extremely short life
        return 10.0 ** lo
    if residual(hi) > 0:
        # strain is below the curve even at N_f=1e12 -> essentially infinite
        return float("inf")

    for _ in range(80):  # ~24 digits of precision in log space
        mid = (lo + hi) / 2.0
        if residual(mid) > 0:
            lo = mid
        else:
            hi = mid

    return 10.0 ** ((lo + hi) / 2.0)


def _compute_lcf_damage(
    lcf_input: CoffinMansonMemoInput,
) -> tuple[float, list[LCFCycleBreakdown]]:
    """Calcula dano LCF y devuelve desglose por ciclo."""
    cycles: list[LCFCycleBreakdown] = []
    total_d = 0.0

    for i, eps_a in enumerate(lcf_input.strain_amplitudes):
        nf = _nf_coffin_manson(
            eps_a,
            lcf_input.sigma_f,
            lcf_input.b,
            lcf_input.eps_f,
            lcf_input.c,
            lcf_input.E,
        )
        d = 1.0 / nf if np.isfinite(nf) and nf > 0 else 0.0
        cycles.append(LCFCycleBreakdown(
            cycle_index=i + 1,
            strain_amplitude=eps_a,
            N_f=nf,
            damage=d,
        ))
        total_d += d

    return total_d, cycles


# ------------------------------------------------------------------
# LaTeX / Markdown rendering
# ------------------------------------------------------------------

def _render_lcf_latex(lcf_input: CoffinMansonMemoInput, D_LCF: float) -> str:
    """Genera fragmento LaTeX de la seccion LCF."""
    p = lcf_input
    return (
        r"\varepsilon_a = \frac{\sigma'_f}{E}\,(2N_f)^{b}"
        r" + \varepsilon'_f\,(2N_f)^{c}" "\\\\"
        rf"\sigma'_f = {p.sigma_f:.1f}\;\text{{MPa}},\;"
        rf"b = {p.b},\;"
        rf"\varepsilon'_f = {p.eps_f},\;"
        rf"c = {p.c},\;"
        rf"E = {p.E:.0f}\;\text{{MPa}}" "\\\\"
        rf"D_{{\text{{LCF}}}} = \sum_j \frac{{1}}{{N_{{f,j}}}} = {D_LCF:.4f}"
    )


def _render_lcf_markdown(
    lcf_input: CoffinMansonMemoInput,
    cycles: list[LCFCycleBreakdown],
    D_LCF: float,
) -> str:
    """Genera fragmento Markdown de la seccion LCF."""
    p = lcf_input
    header = (
        "## Fatiga oligociclica -- Coffin-Manson (LCF)\n\n"
        r"$$\varepsilon_a = \frac{\sigma'_f}{E}(2N_f)^b"
        r" + \varepsilon'_f (2N_f)^c$$" "\n\n"
        f"**Parametros del material:**\n"
        f"- sigma_f' = {p.sigma_f:.1f} MPa\n"
        f"- b = {p.b}\n"
        f"- epsilon_f' = {p.eps_f}\n"
        f"- c = {p.c}\n"
        f"- E = {p.E:.0f} MPa\n\n"
    )

    if not cycles:
        return (
            "## Fatiga oligociclica -- Coffin-Manson (LCF)\n\n"
            "Sin datos de deformacion LCF. D_LCF = 0.0000\n"
        )

    table = (
        "| Ciclo | epsilon_a | N_f | D_j |\n"
        "|---|---|---|---|\n"
    )
    for cyc in cycles:
        nf_str = f"{cyc.N_f:.2e}" if np.isfinite(cyc.N_f) else "inf"
        table += f"| {cyc.cycle_index} | {cyc.strain_amplitude:.6f} | {nf_str} | {cyc.damage:.6f} |\n"

    table += f"\n**Dano LCF:** D_LCF = {D_LCF:.4f}\n"
    return header + table


# ------------------------------------------------------------------
# Main render function
# ------------------------------------------------------------------

def render_combined_fatigue_memo(
    hcf_input: MinerMemoInput | None = None,
    lcf_input: CoffinMansonMemoInput | None = None,
) -> CombinedFatigueMemoResult:
    """Genera la memoria combinada HCF + LCF.

    Cualquiera de los dos inputs puede ser None; en ese caso
    el dano de esa rama es 0.0 y la seccion se marca como N/A.

    Returns:
        CombinedFatigueMemoResult con LaTeX, Markdown y metricas.
    """
    # --- HCF ---
    hcf_result: MinerMemoResult | None = None
    D_HCF = 0.0
    if hcf_input is not None and len(hcf_input.spectrum) > 0:
        hcf_result = render_miner_memo(hcf_input)
        D_HCF = hcf_result.total_damage

    # --- LCF ---
    lcf_cycles: list[LCFCycleBreakdown] = []
    D_LCF = 0.0
    lcf_for_render = lcf_input or CoffinMansonMemoInput()
    if lcf_input is not None and len(lcf_input.strain_amplitudes) > 0:
        D_LCF, lcf_cycles = _compute_lcf_damage(lcf_input)

    # --- Combined ---
    D_total = D_HCF + D_LCF
    pass_check = D_total <= 1.0

    # --- Markdown ---
    md_parts: list[str] = [
        "# Memoria -- Fatiga combinada HCF + LCF\n\n",
    ]

    # HCF section
    if hcf_result is not None:
        md_parts.append(
            "## Fatiga de alto ciclo -- Palmgren-Miner (HCF)\n\n"
            + hcf_result.markdown.split("# Memoria", 1)[-1]
            .lstrip(" —–-")
            .lstrip()
        )
        md_parts.append(f"\n**Dano HCF:** D_HCF = {D_HCF:.4f}\n\n")
    else:
        md_parts.append(
            "## Fatiga de alto ciclo -- Palmgren-Miner (HCF)\n\n"
            "Sin datos de espectro HCF. D_HCF = 0.0000\n\n"
        )

    # LCF section
    md_parts.append(_render_lcf_markdown(lcf_for_render, lcf_cycles, D_LCF))

    # Combined verdict
    verdict = "PASS" if pass_check else "FAIL"
    emoji = "✅" if pass_check else "❌"
    md_parts.append(
        f"\n## Resultado combinado\n\n"
        f"$$D_{{total}} = D_{{HCF}} + D_{{LCF}} = {D_HCF:.4f} + {D_LCF:.4f}"
        f" = {D_total:.4f}$$\n\n"
        f"**Verificacion:** D_total <= 1.0 -> {emoji} {verdict}\n"
    )

    markdown = "".join(md_parts)

    # --- LaTeX ---
    latex_parts: list[str] = []
    if hcf_result is not None:
        latex_parts.append(
            r"\text{--- HCF (Palmgren-Miner) ---}\\" + "\n"
            + hcf_result.latex
        )
    else:
        latex_parts.append(r"D_{\text{HCF}} = 0")

    latex_parts.append(r"\\" + "\n" + r"\text{--- LCF (Coffin-Manson) ---}\\" + "\n")
    latex_parts.append(_render_lcf_latex(lcf_for_render, D_LCF))

    latex_parts.append(
        "\\\\\n"
        r"\text{--- Resultado combinado ---}\\" + "\n"
        rf"D_{{\text{{total}}}} = D_{{\text{{HCF}}}} + D_{{\text{{LCF}}}}"
        rf" = {D_HCF:.4f} + {D_LCF:.4f} = {D_total:.4f}"
    )

    latex = "\n".join(latex_parts)

    return CombinedFatigueMemoResult(
        D_HCF=D_HCF,
        D_LCF=D_LCF,
        D_total=D_total,
        pass_check=pass_check,
        hcf_result=hcf_result,
        lcf_cycles=lcf_cycles,
        latex=latex,
        markdown=markdown,
    )


__all__ = [
    "CoffinMansonMemoInput",
    "LCFCycleBreakdown",
    "CombinedFatigueMemoResult",
    "render_combined_fatigue_memo",
]
