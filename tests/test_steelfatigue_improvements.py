from __future__ import annotations

import math
import numpy as np
import pytest

from steelfatigue.gusset_rbs import FatigueGussetUFM, FatigueRBS
from steelfatigue.multiaxial import (
    brown_miller_parameter,
    critical_plane_search,
    findley_parameter,
)
from steelfatigue.paris_law import ParisInput, integrate_paris, paris_cycles_to_failure
from steelfatigue.rainflow_fatpack import rainflow_count, rainflow_count_exact_float64
from steelfatigue.services.hotspot_service import run_hotspot_analysis


def test_rainflow_exact_float64_preserves_exact_ranges():
    sig = [0.0, 100.123456, 20.654321, 80.5, 50.25, 110.0, 0.0]
    cycles = rainflow_count(sig, use_float64_exact=True)
    ranges = sorted(c.range for c in cycles if c.count == 1.0)
    assert any(abs(r - (80.5 - 50.25)) < 1e-12 for r in ranges)
    assert len(rainflow_count_exact_float64(sig)) == len(cycles)


def test_hotspot_service_trilinear_ec3_knee_and_cutoff():
    # Below constant-amplitude knee (0.737 * 90 = 66.3 MPa), m=5 gives longer life than m=3
    res_m3 = run_hotspot_analysis(52.0, 46.0, thickness_mm=16.0, fat_class=90.0, use_trilinear_ec3=False)
    res_ec3 = run_hotspot_analysis(52.0, 46.0, thickness_mm=16.0, fat_class=90.0, use_trilinear_ec3=True)
    assert res_ec3.estimated_life_cycles > res_m3.estimated_life_cycles

    # Below cut-off (~36.4 MPa), trilinear EC3 gives infinite life
    res_inf = run_hotspot_analysis(20.0, 16.0, thickness_mm=16.0, fat_class=90.0, use_trilinear_ec3=True)
    assert math.isinf(res_inf.estimated_life_cycles)


def test_gusset_ufm_beam_interface_and_rbs_basquin_coffin_manson():
    ufm = FatigueGussetUFM(alpha=380.0, beta=305.0, ec=152.0, eb=178.0)
    forces = ufm.calculate_interface_forces(P_brace=900.0, theta=math.radians(42.0), include_beam_interface=True)
    assert "H_b" in forces and "V_b" in forces and "H_c" in forces and "V_c" in forces

    rot = np.array([0.02, 0.03, 0.025])
    d_reversals = FatigueRBS.calculate_oligocyclic_damage(rot, use_half_reversals=True)
    d_total_strain = FatigueRBS.calculate_oligocyclic_damage(
        rot, use_half_reversals=True, sigma_f_prime_MPa=950.0, E_MPa=200_000.0
    )
    assert d_reversals > 0.0
    # Including elastic strain capacity increases N_f at given total strain -> lower damage
    assert 0.0 < d_total_strain < d_reversals


def test_paris_threshold_and_multiaxial_findley_brown_miller():
    inp_sub = ParisInput(
        a_initial_mm=1.0,
        a_critical_mm=20.0,
        delta_sigma_MPa=30.0,
        delta_K_th_MPa_sqrt_m=5.0,
    )
    res_sub = integrate_paris(inp_sub)
    assert not res_sub.failure
    assert math.isinf(paris_cycles_to_failure(inp_sub))

    assert findley_parameter(80.0, 100.0, k_findley=0.3) == pytest.approx(110.0)
    assert brown_miller_parameter(0.004, 0.001, S_bm=1.0) == pytest.approx(0.003)

    hist = {
        "sxx": [0.0, 200.0, -100.0, 180.0],
        "syy": [0.0, -50.0, 25.0, -40.0],
        "sxy": [0.0, 60.0, -60.0, 50.0],
    }
    cp = critical_plane_search(hist, include_shear=True)
    assert "findley_MPa" in cp and "brown_miller" in cp
    assert cp["findley_MPa"] > 0.0
