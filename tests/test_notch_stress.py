"""Tests para notch stress IIW."""
import pytest
from steelfatigue.notch_stress import NotchInput, notch_stress, notch_endurance_OK


def test_butt_kt_lower_than_fillet():
    a = notch_stress(NotchInput(sigma_nom_MPa=100, weld_type="butt"))
    b = notch_stress(NotchInput(sigma_nom_MPa=100, weld_type="fillet"))
    assert a.Kt < b.Kt
    assert a.sigma_notch_MPa < b.sigma_notch_MPa


def test_cruciform_highest():
    c = notch_stress(NotchInput(sigma_nom_MPa=100, weld_type="cruciform"))
    f = notch_stress(NotchInput(sigma_nom_MPa=100, weld_type="fillet"))
    assert c.Kt > f.Kt


def test_multi_code():
    for code in ("IIW", "EU", "AISC", "AS", "NSR", "SG"):
        r = notch_stress(NotchInput(sigma_nom_MPa=50, code=code))
        assert r.fat_class > 0
    with pytest.raises(ValueError):
        notch_stress(NotchInput(sigma_nom_MPa=50, code="ZZ"))


def test_endurance_check_high_stress_fails():
    inp = NotchInput(sigma_nom_MPa=200, weld_type="fillet")
    # 10 millones de ciclos a sigma alta no debería pasar
    assert notch_endurance_OK(inp, N_cycles=1e7) is False
    # 1000 ciclos sí
    assert notch_endurance_OK(inp, N_cycles=1e3) is True


def test_invalid_inputs():
    with pytest.raises(ValueError):
        notch_stress(NotchInput(sigma_nom_MPa=10, weld_type="zzz"))
    with pytest.raises(ValueError):
        notch_stress(NotchInput(sigma_nom_MPa=10, radius_mm=0.0))
