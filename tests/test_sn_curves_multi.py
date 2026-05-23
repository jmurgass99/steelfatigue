"""Tests S-N curves multi-código."""
import pytest

from fatiguejm.sn_curves_multi import (
    cycles_to_failure, equivalent_categories, lookup_sn,
    AISC_CATEGORIES, AS4100_CATEGORIES, ASME_CATEGORIES,
)


def test_lookup_aisc():
    c = lookup_sn("US", "B")
    assert c is not None and c.delta_sigma_C_MPa == 110


def test_lookup_as():
    c = lookup_sn("AU", "100")
    assert c is not None


def test_cycles_decreciente():
    c = AISC_CATEGORIES[1]  # B 110
    N_low = cycles_to_failure(c, 50)
    N_high = cycles_to_failure(c, 150)
    assert N_low > N_high


def test_equivalentes_cross_code():
    # Δσ_C ≈ 100 → existen AS100 y ASME-AD100
    matches = equivalent_categories(100, tolerance=5)
    codes = {m.code for m in matches}
    assert {"AU", "ASME"}.issubset(codes)


def test_5_libraries_no_vacias():
    assert all(len(L) > 0 for L in (AISC_CATEGORIES, AS4100_CATEGORIES, ASME_CATEGORIES))
