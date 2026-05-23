"""Tests Paris law + Wöhler DB."""
import pytest

from fatiguejm.paris_law import ParisInput, integrate_paris
from fatiguejm.wohler_db import (
    FAT_DATABASE, list_fat_categories, lookup_fat, recommend_for_detail,
)


class TestParis:
    def test_propaga_lento_si_ds_bajo(self):
        r_bajo = integrate_paris(ParisInput(
            a_initial_mm=2, a_critical_mm=20, delta_sigma_MPa=50,
        ))
        r_alto = integrate_paris(ParisInput(
            a_initial_mm=2, a_critical_mm=20, delta_sigma_MPa=200,
        ))
        assert r_bajo.N_cycles > r_alto.N_cycles

    def test_a_initial_invalida(self):
        with pytest.raises(ValueError):
            integrate_paris(ParisInput(
                a_initial_mm=20, a_critical_mm=10, delta_sigma_MPa=100,
            ))


class TestWohler:
    def test_db_count(self):
        assert len(FAT_DATABASE) >= 10

    def test_lookup_existente(self):
        d = lookup_fat("FAT 90")
        assert d is not None
        assert d.delta_sigma_C == 90

    def test_recommend_filtra(self):
        r = recommend_for_detail("soldadura")
        assert len(r) > 0

    def test_list_orden(self):
        cats = list_fat_categories()
        assert cats == sorted(cats, key=lambda x: -x.delta_sigma_C)
