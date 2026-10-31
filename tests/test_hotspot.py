"""Tests para hot-spot stress extrapolation (IIW Tipo a/b)."""
import pytest

from steelfatigue.hotspot import (
    HotSpotInput,
    hot_spot_from_radial_samples,
    hot_spot_stress,
)


def test_linear_iiw():
    # σ(t/2) = 200, σ(3t/2) = 150 → σ_hs = 1.67·200 - 0.67·150 = 233.5
    sigma_hs = hot_spot_stress(HotSpotInput(
        sigma_t_half=200, sigma_3t_half=150, thickness_mm=10,
    ))
    assert sigma_hs == pytest.approx(233.5, rel=1e-3)


def test_quadratic_iiw():
    sigma_hs = hot_spot_stress(HotSpotInput(
        sigma_t_half=200, sigma_3t_half=150, sigma_5t_half=120,
        thickness_mm=10, method="quadratic",
    ))
    # 2.52·200 - 2.24·150 + 0.72·120 = 504 - 336 + 86.4 = 254.4
    assert sigma_hs == pytest.approx(254.4, rel=1e-3)


def test_thickness_invalido():
    with pytest.raises(ValueError):
        hot_spot_stress(HotSpotInput(
            sigma_t_half=100, sigma_3t_half=100, thickness_mm=0,
        ))


def test_quadratic_sin_sigma_5t_levanta():
    with pytest.raises(ValueError):
        hot_spot_stress(HotSpotInput(
            sigma_t_half=200, sigma_3t_half=150,
            thickness_mm=10, method="quadratic",
        ))


def test_radial_samples_interpola():
    # Puntos a 3, 7, 15 mm → interpolar a 0 (extrapolación lineal)
    res = hot_spot_from_radial_samples(
        stresses=[300, 200, 100], radii_mm=[3, 7, 15],
        thickness_mm=4, hot_spot_distance_mm=0,
    )
    # pendiente entre (3,300) y (7,200) = -25 → en 0: 300 + (-25)(0-3) = 375
    assert res == pytest.approx(375.0, rel=1e-6)


def test_radial_samples_interpolacion_interna():
    res = hot_spot_from_radial_samples(
        stresses=[300, 200, 100], radii_mm=[3, 7, 15],
        thickness_mm=4, hot_spot_distance_mm=5,
    )
    # Entre (3,300) y (7,200), distancia 5: 300 + (-25)·(5-3) = 250
    assert res == pytest.approx(250.0, rel=1e-6)
