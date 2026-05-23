"""Fatiga en placas Gusset (UFM) y oligociclica en conexiones RBS.

Integracion desde Master_IEG_Integrations/fatigue_gusset_rbs.py (2026-05-19).

- FatigueGussetUFM: Metodo de Fuerza Uniforme (IEG 3240) para fuerzas en
  interfaces viga/columna/gusset. Sirve de base para luego aplicar SCF +
  curvas S-N (modulos `sn_curves_multi` / `wohler_db`).
- FatigueRBS: dano oligociclico Engelhardt / Coffin-Manson sobre historial
  de rotaciones plasticas (complementa `fatiguejm.lowcycle`).
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

    def calculate_interface_forces(self, P_brace: float, theta: float) -> Dict[str, float]:
        """Calcula componentes horizontal y vertical en la interfaz columna-gusset.

        theta: angulo de la diagonal con la horizontal (radianes).
        """
        V_c = P_brace * (self.beta / (self.alpha + self.beta)) * np.sin(theta)
        H_c = P_brace * (self.alpha / (self.alpha + self.beta)) * np.cos(theta)
        return {"Vc": float(V_c), "Hc": float(H_c)}


class FatigueRBS:
    """Fatiga oligociclica (Coffin-Manson) para conexiones RBS."""

    @staticmethod
    def calculate_oligocyclic_damage(
        plastic_rotation_history: np.ndarray,
        c: float = -0.6,
        eps_f: float = 0.3,
    ) -> float:
        """Dano acumulado de Coffin-Manson sobre amplitudes de rotacion plastica."""
        damage = 0.0
        arr = np.asarray(plastic_rotation_history, dtype=float)
        for rot in arr:
            strain_p = rot * 0.5  # factor geometrico simplificado del ala RBS
            if strain_p > 0:
                N_f = (strain_p / eps_f) ** (1.0 / c)
                damage += 1.0 / N_f
        return float(damage)


__all__ = ["FatigueGussetUFM", "FatigueRBS"]
