"""Tests para el servicio de analisis Hot-Spot Stress y endpoint REST."""
from __future__ import annotations

import pytest

from steelfatigue.services.hotspot_service import (
    HotSpotAnalysisInput,
    HotSpotAnalysisResult,
    run_hotspot_analysis,
)


class TestRunHotspotAnalysis:
    """Tests de la funcion run_hotspot_analysis."""

    def test_linear_basic(self):
        """Analisis lineal basico con valores tipicos."""
        result = run_hotspot_analysis(
            sigma_t_half=200.0,
            sigma_3t_half=150.0,
            thickness_mm=10.0,
            weld_type="butt",
            fat_class=90.0,
        )
        assert isinstance(result, HotSpotAnalysisResult)
        # sigma_hs = 1.67*200 - 0.67*150 = 233.5
        assert result.sigma_hot_spot_MPa == pytest.approx(233.5, rel=1e-3)
        assert result.weld_type == "butt"
        assert result.fat_class == 90.0
        assert result.estimated_life_cycles > 0
        assert result.method == "linear"

    def test_quadratic_method(self):
        """Analisis con metodo cuadratico."""
        result = run_hotspot_analysis(
            sigma_t_half=200.0,
            sigma_3t_half=150.0,
            thickness_mm=10.0,
            weld_type="fillet",
            fat_class=80.0,
            method="quadratic",
            sigma_5t_half=120.0,
        )
        # sigma_hs = 2.52*200 - 2.24*150 + 0.72*120 = 254.4
        assert result.sigma_hot_spot_MPa == pytest.approx(254.4, rel=1e-3)
        assert result.weld_type == "fillet"

    def test_life_decreases_with_higher_stress(self):
        """Vida debe disminuir con mayor tension."""
        r_low = run_hotspot_analysis(
            sigma_t_half=100.0, sigma_3t_half=80.0,
            thickness_mm=10.0, fat_class=90.0,
        )
        r_high = run_hotspot_analysis(
            sigma_t_half=200.0, sigma_3t_half=150.0,
            thickness_mm=10.0, fat_class=90.0,
        )
        assert r_low.estimated_life_cycles > r_high.estimated_life_cycles

    def test_life_increases_with_higher_fat_class(self):
        """Vida debe aumentar con mayor categoria FAT."""
        r_low = run_hotspot_analysis(
            sigma_t_half=200.0, sigma_3t_half=150.0,
            thickness_mm=10.0, fat_class=71.0,
        )
        r_high = run_hotspot_analysis(
            sigma_t_half=200.0, sigma_3t_half=150.0,
            thickness_mm=10.0, fat_class=125.0,
        )
        assert r_high.estimated_life_cycles > r_low.estimated_life_cycles

    def test_to_dict_fields(self):
        """to_dict debe incluir todos los campos esperados."""
        result = run_hotspot_analysis(
            sigma_t_half=200.0, sigma_3t_half=150.0,
            thickness_mm=10.0,
        )
        d = result.to_dict()
        assert "sigma_hot_spot_MPa" in d
        assert "weld_type" in d
        assert "fat_class" in d
        assert "estimated_life_cycles" in d
        assert "method" in d

    def test_invalid_thickness_raises(self):
        """thickness_mm <= 0 debe levantar ValueError."""
        with pytest.raises(ValueError):
            run_hotspot_analysis(
                sigma_t_half=100.0, sigma_3t_half=80.0,
                thickness_mm=0.0,
            )

    def test_invalid_fat_class_raises(self):
        """fat_class <= 0 debe levantar ValueError."""
        with pytest.raises(ValueError):
            run_hotspot_analysis(
                sigma_t_half=100.0, sigma_3t_half=80.0,
                thickness_mm=10.0, fat_class=-1.0,
            )


class TestHotspotEndpoint:
    """Tests del endpoint REST /api/fatigue/hotspot/analysis."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from steelfatigue.api.app import create_app
        return TestClient(create_app())

    def test_post_hotspot_analysis_200(self, client):
        """POST valido debe retornar 200 con campos esperados."""
        r = client.post(
            "/api/fatigue/hotspot/analysis",
            json={
                "sigma_t_half": 200.0,
                "sigma_3t_half": 150.0,
                "thickness_mm": 10.0,
                "weld_type": "butt",
                "fat_class": 90.0,
                "method": "linear",
            },
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "sigma_hot_spot_MPa" in data
        assert "weld_type" in data
        assert "fat_class" in data
        assert "estimated_life_cycles" in data
        assert data["sigma_hot_spot_MPa"] == pytest.approx(233.5, rel=1e-3)

    def test_post_hotspot_analysis_quadratic(self, client):
        """POST con metodo quadratic."""
        r = client.post(
            "/api/fatigue/hotspot/analysis",
            json={
                "sigma_t_half": 200.0,
                "sigma_3t_half": 150.0,
                "sigma_5t_half": 120.0,
                "thickness_mm": 10.0,
                "weld_type": "fillet",
                "fat_class": 80.0,
                "method": "quadratic",
            },
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["method"] == "quadratic"

    def test_post_hotspot_analysis_invalid_thickness_422(self, client):
        """POST con thickness_mm invalido debe retornar 422."""
        r = client.post(
            "/api/fatigue/hotspot/analysis",
            json={
                "sigma_t_half": 100.0,
                "sigma_3t_half": 80.0,
                "thickness_mm": -5.0,
                "fat_class": 90.0,
            },
        )
        assert r.status_code == 422

    def test_existing_hotspot_endpoint_still_works(self, client):
        """El endpoint original /api/fatigue/hotspot debe seguir funcionando."""
        r = client.post(
            "/api/fatigue/hotspot",
            json={
                "sigma_t_half": 200.0,
                "sigma_3t_half": 150.0,
                "thickness_mm": 10.0,
            },
        )
        assert r.status_code == 200
        assert "sigma_hot_spot_MPa" in r.json()
