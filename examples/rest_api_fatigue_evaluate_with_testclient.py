"""Llamar a la API REST (extra `api`) sin levantar un servidor, con el TestClient de FastAPI.

Mismo flujo que haría una hoja de cálculo o un frontend: POST a /api/fatigue/evaluate
con un espectro de bloques y categoría de detalle, POST a /api/fatigue/hotspot con dos
lecturas de tensión y POST a /api/fatigue/paris con una grieta. La aplicación es la
misma que se sirve con `uvicorn steelfatigue.api.app:app`. Requiere
`pip install "steelfatigue[api]"`.

Ejecutar:  python examples/rest_api_fatigue_evaluate_with_testclient.py
"""
import json
import warnings

warnings.filterwarnings("ignore")          # aviso de starlette sobre httpx: no afecta a la API
from fastapi.testclient import TestClient  # noqa: E402

from steelfatigue.api.app import create_app


def main() -> None:
    client = TestClient(create_app())

    r = client.get("/api/fatigue/health")
    print("GET /api/fatigue/health →", r.status_code, r.json())

    payload = {
        "detail_category": 80.0,
        "gamma_mf": 1.15,
        "spectrum": [{"stress_range": 75.16, "cycles": 1.0e6},
                     {"stress_range": 8.67, "cycles": 2.0e6}],
    }
    r = client.post("/api/fatigue/evaluate", json=payload)
    print("\nPOST /api/fatigue/evaluate →", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

    r = client.post("/api/fatigue/hotspot",
                    json={"sigma_t_half": 142.0, "sigma_3t_half": 118.0, "thickness_mm": 20.0})
    print("\nPOST /api/fatigue/hotspot →", r.status_code, r.json())

    r = client.post("/api/fatigue/paris",
                    json={"a_initial_mm": 2.0, "a_critical_mm": 40.0, "delta_sigma_MPa": 80.0})
    body = r.json()
    print("\nPOST /api/fatigue/paris →", r.status_code,
          {k: (round(v, 1) if isinstance(v, float) else v) for k, v in body.items() if k != "a_vs_N"},
          f"({len(body.get('a_vs_N', []))} puntos (N, a) en 'a_vs_N')")

    r = client.post("/api/fatigue/evaluate", json={"detail_category": 80.0, "spectrum": [{"cycles": 10}]})
    print("\nBloque sin 'stress_range' →", r.status_code, "(422: validación de entrada, no 500)")


if __name__ == "__main__":
    main()
