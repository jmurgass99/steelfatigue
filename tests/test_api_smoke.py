"""Smoke tests del endpoint HTTP de SteelFatigue.

Cierra el hueco identificado en la auditoría: tests previos cubrían la
lógica pero no la capa HTTP, dejando latente el bug de Pydantic local +
future annotations.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from steelfatigue.api.app import create_app, create_router


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_health_endpoint(client: TestClient):
    r = client.get("/api/fatigue/health")
    assert r.status_code == 200


def test_evaluate_fatigue_endpoint(client: TestClient):
    """POST /api/fatigue/evaluate con spectrum válido debe ser 200."""
    r = client.post(
        "/api/fatigue/evaluate",
        json={
            "detail_category": 71.0,
            "gamma_mf": 1.35,
            "spectrum": [
                {"stress_range": 80.0, "cycles": 1_000_000},
                {"stress_range": 60.0, "cycles": 500_000},
            ],
        },
    )
    assert r.status_code == 200, r.text


def test_ufm_endpoint(client: TestClient):
    """POST /api/fatigue/ufm — método de fuerza uniforme en gusset."""
    r = client.post(
        "/api/fatigue/ufm",
        json={
            "alpha": 200.0, "beta": 150.0,
            "ec": 100.0, "eb": 50.0,
            "P_brace": 500.0, "theta_rad": 0.785,
        },
    )
    assert r.status_code == 200, r.text


def test_lowcycle_endpoint(client: TestClient):
    """POST /api/fatigue/lowcycle — Coffin-Manson sobre historial de rotaciones."""
    r = client.post(
        "/api/fatigue/lowcycle",
        json={
            "plastic_rotation_history": [0.02, 0.03, 0.025, 0.04],
            "eps_f": 0.30, "c": -0.60, "geometric_factor": 0.50,
        },
    )
    assert r.status_code == 200, r.text


def test_missing_required_field_yields_422(client: TestClient):
    r = client.post("/api/fatigue/evaluate", json={"spectrum": []})
    assert r.status_code == 422


# --------------------------------------------------------------------------- #
# Un dato invalido debe ser 422 (culpa del cliente), NUNCA 500.
#
# Los handlers de /endurance y /mean-stress solo capturaban ValueError, pero el
# codigo que invocan lanza steelfatigue.exceptions.ValidationError, que NO hereda de
# ValueError: escapaba como 500. Ya ocurria con `finish` desconocido (ka_surface
# siempre lanzo) y con Soderberg sin Sy; al dejar de devolver kc=1.0 en silencio
# para una carga desconocida, `loading` se sumo al mismo camino.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"Su_MPa": 690.0, "loading": "axail"}, id="loading-desconocido"),
        pytest.param({"Su_MPa": 690.0, "finish": "polished"}, id="finish-desconocido"),
    ],
)
def test_endurance_entrada_invalida_es_422_no_500(client: TestClient, payload):
    r = client.post("/api/fatigue/endurance", json=payload)
    assert r.status_code == 422, r.text


def test_mean_stress_soderberg_sin_Sy_es_422_no_500(client: TestClient):
    r = client.post(
        "/api/fatigue/mean-stress",
        json={"sigma_a_MPa": 50.0, "sigma_m_MPa": 100.0,
              "Se_MPa": 200.0, "Su_MPa": 600.0, "criterion": "soderberg"},
    )
    assert r.status_code == 422, r.text


def test_endurance_entrada_valida_sigue_200(client: TestClient):
    r = client.post("/api/fatigue/endurance",
                    json={"Su_MPa": 690.0, "loading": "axial", "finish": "machined"})
    assert r.status_code == 200, r.text


def test_create_router_exposes_routes():
    router = create_router()
    paths = {r.path for r in router.routes if hasattr(r, "path")}
    assert "/api/fatigue/evaluate" in paths
    assert "/api/fatigue/ufm" in paths
    assert "/api/fatigue/lowcycle" in paths
    assert "/api/fatigue/hotspot" in paths
    assert "/api/fatigue/hotspot/analysis" in paths
