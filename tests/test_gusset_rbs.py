"""Tests minimos para gusset_rbs (Master IEG seed)."""
from __future__ import annotations

import numpy as np

from fatiguejm.gusset_rbs import FatigueGussetUFM, FatigueRBS


def test_ufm_symmetric_45deg():
    g = FatigueGussetUFM(alpha=15.0, beta=15.0, ec=5.0, eb=5.0)
    f = g.calculate_interface_forces(P_brace=1000.0, theta=np.radians(45.0))
    # alpha == beta y theta = 45 -> Vc = Hc = 1000 * 0.5 * sqrt(2)/2
    assert f["Vc"] > 0 and f["Hc"] > 0
    assert abs(f["Vc"] - f["Hc"]) < 1e-9


def test_ufm_horizontal_brace_no_vertical():
    g = FatigueGussetUFM(alpha=15.0, beta=20.0, ec=5.0, eb=5.0)
    f = g.calculate_interface_forces(P_brace=1000.0, theta=0.0)
    assert abs(f["Vc"]) < 1e-9
    assert f["Hc"] > 0


def test_rbs_damage_increases_with_amplitude():
    small = FatigueRBS.calculate_oligocyclic_damage(np.array([0.005, 0.005, 0.005]))
    big = FatigueRBS.calculate_oligocyclic_damage(np.array([0.05, 0.05, 0.05]))
    assert big > small > 0.0


def test_rbs_damage_zero_for_no_rotation():
    d = FatigueRBS.calculate_oligocyclic_damage(np.array([0.0, 0.0]))
    assert d == 0.0
