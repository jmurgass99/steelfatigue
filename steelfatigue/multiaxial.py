"""
Modelo Smith-Watson-Topper (SWT, 1970) — fatiga multiaxial.

Parámetro SWT: P_SWT = σ_max · ε_a
donde σ_max = tensión máxima en el plano crítico
y ε_a = amplitud de deformación en ese plano.

Curva: P_SWT = (σ'_f)²/(E) · (2N_f)^(2b) + σ'_f · ε'_f · (2N_f)^(b+c)
"""
from __future__ import annotations

from dataclasses import dataclass
from math import log


@dataclass(frozen=True)
class SWTInput:
    sigma_max_MPa: float          # tensión máxima plano crítico
    eps_amplitude: float          # amplitud deformación
    E_MPa: float = 200_000.0
    sigma_f_prime_MPa: float = 1000.0   # coef. resistencia fatiga
    eps_f_prime: float = 0.5             # coef. ductilidad fatiga
    b: float = -0.10                     # exponente resistencia
    c: float = -0.60                     # exponente ductilidad


def cycles_to_failure_swt(inp: SWTInput,
                            N_max: float = 1e10,
                            tol: float = 1e-6) -> float:
    """Resuelve N_f por bisección de P_SWT(N_f) = σ_max · ε_a."""
    P_target = inp.sigma_max_MPa * inp.eps_amplitude

    def f(N: float) -> float:
        twoN = 2 * N
        return (
            inp.sigma_f_prime_MPa ** 2 / inp.E_MPa * twoN ** (2 * inp.b)
            + inp.sigma_f_prime_MPa * inp.eps_f_prime * twoN ** (inp.b + inp.c)
            - P_target
        )

    lo, hi = 0.5, N_max
    f_lo, f_hi = f(lo), f(hi)
    if f_lo * f_hi > 0:
        # Sin cambio de signo no hay raíz en [lo, hi]. f es DECRECIENTE en N,
        # así que el signo común decide:
        #   f_hi > 0 -> la capacidad supera la demanda incluso en N_max: run-out
        #               (vida infinita).
        #   f_hi < 0 -> la demanda supera la capacidad ya en N=0.5: vida nula.
        # El test anterior comparaba `P_target < f_hi`, dos magnitudes distintas
        # (una demanda contra un residuo), y devolvía el literal 0.0 —vida
        # NULA— para casos de vida INFINITA.
        return float("inf") if f_hi > 0 else 0.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        f_mid = f(mid)
        if abs(f_mid) < tol:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid
    return (lo + hi) / 2.0


def findley_parameter(
    tau_a_MPa: float,
    sigma_n_max_MPa: float,
    k_findley: float = 0.30,
) -> float:
    """Parámetro de plano crítico de Findley (1959): P_F = τ_a + k · σ_n,max [MPa]."""
    return float(tau_a_MPa + k_findley * sigma_n_max_MPa)


def brown_miller_parameter(
    delta_gamma_max: float,
    delta_eps_n: float,
    S_bm: float = 1.0,
) -> float:
    """Parámetro de deformación de plano crítico de Brown & Miller (1973):
    P_BM = Δγ_max / 2 + S · Δε_n.
    """
    return float(0.5 * delta_gamma_max + S_bm * delta_eps_n)


def critical_plane_search(
    stress_history: dict[str, list[float]],
    n_angles: int = 18,
    include_shear: bool = False,
    nu: float = 0.30,
    E_MPa: float = 200_000.0,
) -> dict[str, float]:
    """Búsqueda del plano crítico que maximiza σ_max·ε_a (y opcionalmente métricas de cortante)."""
    import numpy as np
    angles = np.linspace(0, np.pi, n_angles, endpoint=False)
    sxx = np.asarray(stress_history.get("sxx", []))
    syy = np.asarray(stress_history.get("syy", []))
    sxy = np.asarray(stress_history.get("sxy", []))
    if sxx.size == 0:
        raise ValueError(
            "stress_history sin componente 'sxx' (o vacía): no hay historia de "
            "tensiones sobre la que buscar el plano crítico. Sin datos no hay "
            "resultado; un plano con sigma_max=0 sería una demanda inventada."
        )
    best: dict[str, float] = {
        "theta_rad": 0.0,
        "P_SWT": 0.0,
        "sigma_max": 0.0,
        "eps_a": 0.0,
    }
    G_MPa = E_MPa / (2.0 * (1.0 + nu))
    # Cada criterio tiene su propio plano crítico: Findley y Brown-Miller se
    # maximizan sobre todos los planos, no se evalúan en el plano de SWT.
    shear_best = {"findley_MPa": -float("inf"), "brown_miller": -float("inf")}
    for theta in angles:
        c, s = np.cos(theta), np.sin(theta)
        sigma_n = sxx * c ** 2 + syy * s ** 2 + 2 * sxy * c * s
        tau_n = -(sxx - syy) * s * c + sxy * (c ** 2 - s ** 2)
        eps_amp = (sigma_n.max() - sigma_n.min()) / 2.0 / E_MPa
        P = sigma_n.max() * eps_amp
        if P > best["P_SWT"]:
            best = {
                "theta_rad": float(theta),
                "P_SWT": float(P),
                "sigma_max": float(sigma_n.max()),
                "eps_a": float(eps_amp),
            }
        if include_shear:
            tau_amp = float((tau_n.max() - tau_n.min()) / 2.0)
            delta_gamma = float((tau_n.max() - tau_n.min()) / G_MPa)
            pf = findley_parameter(tau_amp, float(sigma_n.max()))
            pbm = brown_miller_parameter(delta_gamma, 2.0 * float(eps_amp))
            if pf > shear_best["findley_MPa"]:
                shear_best.update(findley_MPa=pf, findley_theta_rad=float(theta), tau_a=tau_amp)
            if pbm > shear_best["brown_miller"]:
                shear_best.update(brown_miller=pbm, brown_miller_theta_rad=float(theta))
    if include_shear:
        best.update(shear_best)
    return best


__all__ = [
    "SWTInput",
    "cycles_to_failure_swt",
    "critical_plane_search",
    "findley_parameter",
    "brown_miller_parameter",
]
