"""Configuracion comun de pytest para SteelFatigue."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def spectrum_simple() -> list[dict[str, float]]:
    """Espectro de tensiones simple para pruebas."""
    return [
        {"stress_range": 80.0, "cycles": 1.0e5},
        {"stress_range": 50.0, "cycles": 5.0e5},
    ]
