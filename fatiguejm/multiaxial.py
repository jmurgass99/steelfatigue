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


def critical_plane_search(stress_history: dict[str, list[float]],
                            n_angles: int = 18) -> dict[str, float]:
    """Búsqueda del plano crítico que maximiza σ_max·ε_a."""
    import numpy as np
    angles = np.linspace(0, np.pi, n_angles, endpoint=False)
    sxx = np.asarray(stress_history.get("sxx", []))
    syy = np.asarray(stress_history.get("syy", []))
    sxy = np.asarray(stress_history.get("sxy", []))
    if sxx.size == 0:
        # Antes devolvía sigma_max = 0.0 y eps_a = 0.0 (y sin la clave P_SWT):
        # una historia de tensiones AUSENTE se leía como "no hay demanda de
        # fatiga", P_SWT = 0 -> vida infinita. La ausencia se propaga como
        # ausencia, no como un cero tranquilizador.
        raise ValueError(
            "stress_history sin componente 'sxx' (o vacía): no hay historia de "
            "tensiones sobre la que buscar el plano crítico. Sin datos no hay "
            "resultado; un plano con sigma_max=0 sería una demanda inventada."
        )
    best = {"theta_rad": 0.0, "P_SWT": 0.0,
             "sigma_max": 0.0, "eps_a": 0.0}
    for theta in angles:
        c, s = np.cos(theta), np.sin(theta)
        sigma_n = sxx * c ** 2 + syy * s ** 2 + 2 * sxy * c * s
        eps_amp = (sigma_n.max() - sigma_n.min()) / 2.0 / 200_000.0
        P = sigma_n.max() * eps_amp
        if P > best["P_SWT"]:
            best = {"theta_rad": float(theta), "P_SWT": float(P),
                     "sigma_max": float(sigma_n.max()),
                     "eps_a": float(eps_amp)}
    return best


__all__ = ["SWTInput", "cycles_to_failure_swt", "critical_plane_search"]
