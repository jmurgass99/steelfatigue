"""FatigueRBS cuenta ciclos (no inversiones) por defecto, igual que lowcycle.CoffinMansonRBS."""
import numpy as np
import pytest

from steelfatigue.gusset_rbs import FatigueRBS
from steelfatigue.lowcycle import CoffinMansonParams, CoffinMansonRBS

ROT = np.array([0.02, 0.03, 0.04])


def test_default_matches_lowcycle_reference():
    ref = CoffinMansonRBS(CoffinMansonParams(eps_f=0.3, c=-0.6, geometric_factor=0.5)).evaluate(ROT).total_damage
    assert FatigueRBS.calculate_oligocyclic_damage(ROT) == pytest.approx(ref, rel=1e-12)
    assert FatigueRBS.calculate_oligocyclic_damage(ROT, use_half_reversals=True) == pytest.approx(ref, rel=1e-12)


def test_default_by_hand():
    expected = sum(1.0 / (0.5 * (0.5 * r / 0.3) ** (1.0 / -0.6)) for r in ROT)
    assert FatigueRBS.calculate_oligocyclic_damage(ROT) == pytest.approx(expected, rel=1e-12)


def test_basquin_branch_is_continuous_as_sigma_f_vanishes():
    d0 = FatigueRBS.calculate_oligocyclic_damage(ROT)
    d_eps = FatigueRBS.calculate_oligocyclic_damage(ROT, sigma_f_prime_MPa=1e-9)
    assert d_eps == pytest.approx(d0, rel=1e-6)
