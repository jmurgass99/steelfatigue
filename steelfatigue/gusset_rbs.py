"""Fatiga en placas Gusset (UFM) y oligociclica en conexiones RBS.

- FatigueGussetUFM: Metodo de Fuerza Uniforme (AISC Part 13 / IEG 3240) para fuerzas en
  interfaces viga/columna/gusset.
- FatigueRBS: dano oligociclico Engelhardt / Coffin-Manson / Basquin sobre historial
  de rotaciones plasticas (complementa `steelfatigue.lowcycle`).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

import numpy as np


def _bootstrap_sibling_paths() -> None:
    root = Path(__file__).resolve().parents[2]
    if root.name != "APIS Structural JM":
        return
    siblings = [root / "_platform", root / "SteelConnectionJm"]
    for s in siblings:
        if s.exists() and str(s) not in sys.path:
            sys.path.insert(0, str(s))


_bootstrap_sibling_paths()


class FatigueGussetUFM:
    """Metodo de Fuerza Uniforme para placas gusset (AISC / IEG 3240)."""

    def __init__(self, alpha: float, beta: float, ec: float, eb: float):
        self.alpha = alpha
        self.beta = beta
        self.ec = ec
        self.eb = eb

    def calculate_interface_forces(
        self,
        P_brace: float,
        theta: float,
        include_beam_interface: bool = False,
    ) -> Dict[str, float]:
        """Calcula componentes horizontal y vertical en la interfaz columna-gusset.

        Si ``include_beam_interface=True``, delega en :class:`steelfatigue.lowcycle.UFMGussetForces`
        (Thornton-Muir, AISC Part 13) e incluye ``H_b, V_b, H_c, V_c``.
        """
        V_c = P_brace * (self.beta / (self.alpha + self.beta)) * np.sin(theta)
        H_c = P_brace * (self.alpha / (self.alpha + self.beta)) * np.cos(theta)
        res = {"Vc": float(V_c), "Hc": float(H_c)}
        if include_beam_interface:
            from .lowcycle import UFMGeometry, UFMGussetForces
            ufm = UFMGussetForces(UFMGeometry(self.alpha, self.beta, self.ec, self.eb))
            res.update(ufm.interface_forces(P_brace, theta_rad=theta).to_dict())
        return res


class FatigueRBS:
    """Fatiga oligociclica (Coffin-Manson / Basquin) para conexiones RBS."""

    @staticmethod
    def calculate_oligocyclic_damage(
        plastic_rotation_history: np.ndarray,
        c: float = -0.6,
        eps_f: float = 0.3,
        use_half_reversals: bool = False,
        sigma_f_prime_MPa: float = 0.0,
        E_MPa: float = 200_000.0,
        b: float = -0.10,
    ) -> float:
        """Dano acumulado de Coffin-Manson sobre amplitudes de rotacion plastica.

        Si ``use_half_reversals=True``, delega en :class:`steelfatigue.lowcycle.CoffinMansonRBS`
        (formulacion en inversiones ``2*N_f``). Si ``sigma_f_prime_MPa > 0``, incluye
        el termino elastico de Basquin en la ecuacion de deformacion total.
        """
        arr = np.asarray(plastic_rotation_history, dtype=float)
        if use_half_reversals and sigma_f_prime_MPa <= 0.0:
            from .lowcycle import CoffinMansonParams, CoffinMansonRBS
            evaluator = CoffinMansonRBS(CoffinMansonParams(eps_f=eps_f, c=c, geometric_factor=0.5))
            return float(evaluator.evaluate(np.abs(arr)).total_damage)

        damage = 0.0
        for rot in arr:
            strain_p = rot * 0.5  # factor geometrico simplificado del ala RBS
            if strain_p > 0:
                if sigma_f_prime_MPa > 0.0 and E_MPa > 0.0:
                    lo, hi = 0.5, 1e8
                    for _ in range(80):
                        mid = 0.5 * (lo + hi)
                        eps_cap = (sigma_f_prime_MPa / E_MPa) * (2.0 * mid) ** b + eps_f * (2.0 * mid) ** c
                        if eps_cap > strain_p:
                            lo = mid
                        else:
                            hi = mid
                    N_f = 0.5 * (lo + hi)
                else:
                    N_f = (strain_p / eps_f) ** (1.0 / c)
                    if use_half_reversals:
                        N_f *= 0.5
                damage += 1.0 / N_f
        return float(damage)


__all__ = ["FatigueGussetUFM", "FatigueRBS"]
